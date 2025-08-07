"""Prioritization models for ML step.

Model Process:
1. Identify Positive Dataset
    - All representative pairs from parsimonious selection
2. Generate Negative Dataset
    - Random protein pairs that are not candidate pairs

"""

import logging
import os
import random
from pathlib import Path
from typing import Any, Container

import numpy as np
import polars as pl
import xgboost
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold

from xlranker.bio.pairs import ProteinPair
from xlranker.config import config
from xlranker.data import load_default_ppi, load_gmts
from xlranker.lib import XLDataSet
from xlranker.selection import BestSelector, PairSelector
from xlranker.status import PrioritizationStatus

logger = logging.getLogger(__name__)


DEFAULT_XGB_PARAMS: dict[str, Any] = {
    "objective": "binary:logistic",
    "eval_metric": "auc",
    "eta": 0.1,
    "max_depth": 6,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "min_child_weight": 1,
    "tree_method": "hist",
}


def in_same_set(a: str, b: str, sets: list[list[set[str]]]) -> bool:
    """Check if a and b are located in the same set in any of the exclusive sets provided.

    Args:
        a (str): entity a
        b (str): entity b
        sets (list[list[set[str]]]): list of gmts, which are lists of sets

    Returns:
        bool: True if a and b both located in at least one set

    """
    for gmt in sets:
        for gene_set in gmt:
            if a in gene_set and b in gene_set:
                return True
    return False


class ModelConfig:  # TODO: Determine if this should go into the config module.
    """Configuration options for the ML prioritization step."""

    runs: int
    folds: int
    xgb_params: dict[str, Any]

    def __init__(
        self,
        runs: int = 10,
        folds: int = 5,
        xgb_params: dict[str, Any] = DEFAULT_XGB_PARAMS,
    ):
        """Config for the prioritization model.

        Args:
            runs (int, optional): the number of model runs. Defaults to 10.
            folds (int, optional): number of folds per run. Defaults to 5.
            xgb_params (dict[str, Any], optional): dictionary of parameters for the XGBoost model. Defaults to DEFAULT_XGB_PARAMS.

        """
        self.runs = runs
        self.folds = folds
        self.xgb_params = xgb_params

    def validate(self) -> bool:
        """Validate the parameters of the config.

        Returns:
            bool: True if all parameters are the correct type and meet the minimum value requirements.

        """
        attrs = {
            "runs": (int, lambda x: x >= 1),
            "folds": (int, lambda x: x >= 1),
            "xgb_params": (dict, None),
        }
        for attr, (typ, cond) in attrs.items():
            value = getattr(self, attr, None)
            if not isinstance(value, typ):
                return False
            if cond and not cond(value):
                return False
        return True


class PrioritizationModel:
    """Prioritization model using XGBoost to predict which pair should be selected as the representative.

    Raises:
        ValueError: Raised if there aren't enough negatives and config.fragile is True.

    """

    positives: list[ProteinPair]
    to_predict: list[ProteinPair]
    dataset: XLDataSet
    existing_pairs: set[Container[str]]
    model_config: ModelConfig
    n_features: int
    gmts: list[list[set[str]]]
    ppi_db: pl.DataFrame
    default_ppi: bool
    xgboost_model: xgboost.XGBClassifier
    pair_selector: PairSelector

    def __init__(
        self,
        dataset: XLDataSet,
        model_config: ModelConfig | None = None,
        gmt_list: list[list[set[str]]] | None = None,
        ppi_db: pl.DataFrame | None = None,
        pair_selector: PairSelector = BestSelector(with_secondary=False),
    ):
        """Initialize PrioritizationModel.

        Args:
            dataset (XLDataSet): XL data set that needs prioritization. Requires Parsimony Analysis to have been performed.
            model_config (ModelConfig | None, optional): Config for the model. If None use defaults. Defaults to None.
            gmt_list (list[list[set[str]]] | None, optional): list of exclusive sets. Negative pairs can't be in the same set. Defaults to None.
            ppi_db (pl.DataFrame | None, optional): PPI database. Should have two columns P1 and P2, where P1 is first alphabetically. Defaults to None.
            pair_selector (PairSelector,  optional): Pair selector

        """
        self.dataset = dataset
        self.positives = []
        self.to_predict = []
        for protein_pair in self.dataset.protein_pairs.values():
            match protein_pair.prioritization_status:
                case PrioritizationStatus.PARSIMONY_PRIMARY_SELECTED:
                    if protein_pair.a.name != protein_pair.b.name:
                        self.positives.append(protein_pair)
                case PrioritizationStatus.PARSIMONY_AMBIGUOUS:
                    self.to_predict.append(protein_pair)
        self.existing_pairs = set(
            tuple(sorted([p.a.name, p.b.name]))
            for p in self.dataset.protein_pairs.values()
        )
        self.n_features = len(self.to_predict[0].abundance_dict()) - 1
        if model_config is None:
            model_config = ModelConfig()
        self.model_config = model_config
        if gmt_list is None:
            gmt_list = load_gmts()
        self.gmts = gmt_list
        if ppi_db is None:
            self.default_ppi = True
            ppi_db = load_default_ppi()
        self.ppi_db = ppi_db
        self.pair_selector = pair_selector

    def is_intra(self, a: str, b: str) -> float:
        """Determine if a and b are intra pairs and represent as float.

        Args:
            a (str): name of protein a
            b (str): name of protein b

        Returns:
            float: 1.0 if a and b have same name, else returns 0.0

        """
        if config.human_only:  # Capitalize to ensure consistent case
            a = a.upper()
            b = b.upper()
        if a == b:
            return 1.0
        return 0.0

    def is_ppi(self, a: str, b: str) -> float:
        """Determine if protein a and protein b has a known ppi in  ppi_db.

        Order of `a` and `b` does not matter.

        Args:
            a (str): First protein
            b (str): Second protein

        Returns:
            float: Return float with 1.0 meaning there is a known ppi in the db

        """
        if config.human_only:  # Capitalize to ensure consistent case
            a = a.upper()
            b = b.upper()
        if a > b:
            c = a
            a = b
            b = c
        row_exists = self.ppi_db.filter(
            (self.ppi_db["P1"] == a) & (self.ppi_db["P2"] == b)
        )
        return 1.0 if row_exists.height > 0 else 0.0

    def get_negatives(self, n: int) -> list[ProteinPair]:
        """Get a list of negative protein pairs.

        Args:
            n (int): the number of pairs to generate

        Raises:
            ValueError: Raised if the value of `n` is larger than what is possible
                        and if config.fragile is True

        Returns:
            list[ProteinPair]: list of negative protein pairs

        """
        negatives: list[ProteinPair] = []
        n_prot = len(self.dataset.proteins.values())
        if n > (n_prot * (n_prot - 1)) // 2 - len(self.positives):
            msg = f"n value for get_negatives ({n}) is too large. Setting to maximum value: {(n_prot * (n_prot - 1)) // 2 - len(self.positives)}"
            if config.fragile:
                logger.error(msg)
                raise ValueError(
                    "get_negatives(n: int) n value is too large and fragile is True"
                )
            logger.warning(msg)
            n = (n_prot * (n_prot - 1)) // 2 - len(self.positives)
        protein_ids = list(self.dataset.proteins.keys())

        generated: set[Container[str]] = set()

        while len(negatives) < n:
            a, b = random.sample(protein_ids, 2)
            pair_key = tuple(sorted([a, b]))
            if (
                pair_key in self.existing_pairs
                or pair_key in generated
                or in_same_set(a, b, self.gmts)
            ):
                continue
            negatives.append(
                ProteinPair(self.dataset.proteins[a], self.dataset.proteins[b])
            )
            generated.add(pair_key)
        return negatives

    def construct_df_from_pairs(
        self, pair_list: list[ProteinPair], has_label: bool, label_value: float = 0.0
    ) -> pl.DataFrame:
        """Construct a DataFrame from the list of Protein Pairs.

        Args:
            pair_list (list[ProteinPair]): list of protein pairs to get the dataframe from
            has_label (bool): if True, adds label column to dataframe
            label_value (float, optional): value assigned to the label column. Defaults to 0.0 (negative).

        Returns:
            pl.DataFrame: DataFrame object with the first column being the pair ID, following columns with abundances for the proteins. If `has_label` is true, last column is label with a value of `label_value`.

        """
        df_array: list[dict[str, str | int | float | None]] = []
        is_first = True
        headers = ["pair"]  # headers in the correct order
        schema: dict[str, pl.DataType] = {"pair": pl.String()}
        for pair in pair_list:
            pair_dict = pair.abundance_dict()
            if (
                config.human_only or not self.default_ppi
            ):  # Can only add if only human or if using custom PPI DB
                pair_dict["is_ppi"] = self.is_ppi(pair.a.name, pair.b.name)
                # pair_dict["is_intra"] = self.is_intra(pair.a.name, pair.b.name)
            if has_label:
                pair_dict["label"] = label_value
            df_array.append(pair_dict)
            if is_first:
                is_first = False
                for header in pair_dict.keys():
                    if "pair" != header:
                        headers.append(header)
                        schema[header] = pl.Float64()
        return pl.DataFrame(df_array, schema=pl.Schema(schema)).select(headers)

    def construct_predict_df(self) -> pl.DataFrame:
        """Construct the data frame for pairs that need predictions.

        Returns:
            pl.DataFrame: Polars DataFrame of the protein pairs needing prediction.

        """
        return self.construct_df_from_pairs(self.to_predict, has_label=False)

    def construct_training_df(self, negative_pairs: list[ProteinPair]) -> pl.DataFrame:
        """Generate a Polars DataFrame from the positive pairs and a list of negative ProteinPair.

        Args:
            negative_pairs (list[ProteinPair]): the list of negative pairs to add to DataFrame

        Returns:
            pl.DataFrame: DataFrame where the first column is 'pair', followed by abundances. Last column is 'label'

        """
        positive_df = self.construct_df_from_pairs(
            self.positives, has_label=True, label_value=1.0
        )
        negative_df = self.construct_df_from_pairs(
            negative_pairs, has_label=True, label_value=0.0
        )
        return pl.concat([positive_df, negative_df])

    def run_model(self):
        """Run the model and get predictions for all protein pairs."""
        random_seed = random.random() * 100000

        predict_df = self.construct_predict_df()

        predict_X = predict_df.drop("pair").to_numpy()

        predictions = np.zeros((self.model_config.runs, len(self.to_predict)))

        # Lists to store data for Shapley values and AUC plots
        all_test_labels = []
        all_test_preds = []
        run_ids = []
        aucs = []

        for run in range(self.model_config.runs):
            logger.info(f"Model on run {run + 1}/{self.model_config.runs}")
            np.random.seed(int(random_seed + run))
            train_df = self.construct_training_df(
                self.get_negatives(len(self.positives))
            )

            X = train_df.drop(["pair", "label"]).to_numpy()
            y = train_df.get_column("label").to_numpy()

            skf = StratifiedKFold(
                n_splits=self.model_config.folds,
                shuffle=True,
                random_state=(int(random_seed + run)),
            )

            y_test_run = np.array([])
            y_test_pred_run = np.array([])

            # Run k-fold cross-validation
            for fold, (train_idx, test_idx) in enumerate(skf.split(X, y)):
                # Split data
                X_train, X_test = X[train_idx], X[test_idx]
                y_train, y_test = y[train_idx], y[test_idx]

                model = xgboost.XGBClassifier(
                    **self.model_config.xgb_params,
                    random_state=int(random_seed + run * fold),
                )

                _ = model.fit(X_train, y_train)

                y_test_pred = model.predict_proba(X_test)[:, 1]

                y_test_run = np.append(y_test_run, y_test)
                y_test_pred_run = np.append(y_test_pred_run, y_test_pred)

            # Train a model on the entire dataset for predictions
            random_seed = random.random() * 100000
            model = xgboost.XGBClassifier(
                **self.model_config.xgb_params, random_state=int(random_seed)
            )
            model.fit(X, y)

            # Get predictions for the prediction dataset
            cur_predictions = model.predict_proba(predict_X)[:, 1]
            predictions[run] = cur_predictions

            auc_score = roc_auc_score(y_test_run, y_test_pred_run)
            aucs.append(auc_score)
            logger.info(f"ROC AUC for run {run + 1}: {auc_score:.2f}")
            all_test_labels.append(y_test_run)
            all_test_preds.append(y_test_pred_run)
            run_ids.append(run)

        mean_predictions = np.mean(predictions, axis=0)

        for i, protein_pair in enumerate(self.to_predict):
            protein_pair.set_score(mean_predictions[i])

        os.makedirs(
            config.output, exist_ok=True
        )  # TODO: Have this done automatically or ask if its okay if exists.

        predict_df = predict_df.with_columns(pl.Series("prediction", mean_predictions))
        predict_df.write_csv(
            str(Path(config.output).joinpath("model_output.tsv")), separator="\t"
        )

        # Print summary statistics
        logger.info(
            f"Average AUC across {self.model_config.runs} runs: {np.mean(aucs):.4f} ± {np.std(aucs):.4f}"
        )
        logger.info("Results saved to: .")

    def get_selected(self) -> list[ProteinPair]:
        """Get all `ProteinPair`s that were accepted.

        Returns:
            list[ProteinPair]: All machine-learning selected pairs predicted by this model

        """
        return [
            p
            for p in self.to_predict
            if p.prioritization_status == PrioritizationStatus.ML_PRIMARY_SELECTED
            or p.prioritization_status == PrioritizationStatus.ML_SECONDARY_SELECTED
        ]

    def get_selections(self) -> list[ProteinPair]:
        """Get the best pair for each protein pair subgroup.

        Returns:
            list[ProteinPair]: list of the protein pairs that were accepted

        """
        self.pair_selector.process(self.to_predict)
        return self.get_selected()

    def save_model(self, file_path: str) -> None:
        """Save the model using the official XGBoost method.

        Args:
            file_path (str): path to save model to.

        """
        self.xgboost_model.save_model(file_path)
