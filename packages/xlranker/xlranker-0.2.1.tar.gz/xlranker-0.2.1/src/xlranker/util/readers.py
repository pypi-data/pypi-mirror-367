"""Functions for reading data files, mapping files, and networks."""

import logging
from pathlib import Path

import polars as pl

from xlranker.bio import Peptide
from xlranker.bio.pairs import PeptidePair
from xlranker.util import get_pair_id
from xlranker.config import config

logger = logging.getLogger(__name__)


def read_data_matrix(
    data_path: str, additional_null_values: list[str] = []
) -> pl.DataFrame:
    """Reads data matrix into a Polars DataFrame with samples/measurements being columns.

    Format:
     - Has header (any names allowed).
     - First column must be the protein/gene followed by measurements.
     - Null/missing values: "", "NA". More can be added.

    Args:
        data_path (str): path to the data matrix
        additional_null_values (list[str]): list of str of additional values that should considered as null

    Returns:
        pl.DataFrame: Polars DataFrame of the input data

    """
    null_values = ["", "NA"]
    null_values.extend(additional_null_values)
    return pl.read_csv(
        data_path, has_header=True, separator="\t", null_values=null_values
    )


def base_name(file_path: Path | str) -> str:
    """Get the base name from a path.

    Example:
        ```
        file_path = "example/test.tsv"
        base = base_name(file_path) # base = "test"
        assert base == "test"
        ```

    Args:
        file_path (Path | str): path of file to get base name of

    Returns:
        str: the base file name

    """
    return Path(file_path).stem


def read_data_folder(
    folder_path: str, additional_null_values=[]
) -> dict[str, pl.DataFrame]:
    """Reads all TSV files in a folder.

    Args:
        folder_path (str): path of the folder that contains files ending in .tsv
        additional_null_values (list[str]): list of str of additional values that should considered as null in the data files

    Raises:
        FileNotFoundError: raised if no TSV files are found

    Returns:
        list[pl.DataFrame]: list of all of the data files in a Polars DataFrame, as read by the read_data_matrix function

    """
    file_glob = Path(folder_path).glob("*.tsv")
    file_list: list[Path] = list(file_glob)
    if len(file_list) == 0:
        raise FileNotFoundError(f"No TSV files were found in directory: {folder_path}")
    ret_dict = {}
    for file in file_list:
        ret_dict[base_name(file)] = read_data_matrix(
            str(file), additional_null_values=config.additional_null_values
        )
    return ret_dict


def read_network_file(network_path: str) -> dict[str, PeptidePair]:
    """Reads TSV network file to a list of PeptideGroup.

    Args:
        network_path (str): path to the TSV file

    Returns:
        list[PeptideGroup]: list of PeptideGroup representing the network

    """
    try:
        with open(network_path) as r:
            text = r.read().split("\n")
        new_rows = set()  # Track unique rows
        valid_rows = 0  # Keeps track of number of edges in original file
        for row in text:
            if "\t" in row:
                valid_rows += 1
                vals = row.split("\t")
                val_a = vals[0]
                val_b = vals[1]
                if val_a > val_b:  # Make sure edges are all sorted the same.
                    temp = val_a
                    val_a = val_b
                    val_b = temp
                new_rows.add(f"{val_a}\t{val_b}")
    except IndexError:
        logger.error("Index out of bound. Make sure network is in the correct format.")
        raise IndexError()
    except FileNotFoundError:
        logger.error(f"File not found: {network_path}")
        raise FileNotFoundError
    duplicate_rows = valid_rows - len(new_rows)  # Count number of duplicated rows
    if duplicate_rows > 0:  # Send warning that duplicate edges were removed.
        logger.warning(
            f"Found and removed {duplicate_rows} duplicated edge(s) in network."
        )
    network: dict[str, PeptidePair] = {}
    for row in new_rows:
        vals = row.split("\t")
        a = Peptide(vals[0])
        b = Peptide(vals[1])
        group = PeptidePair(a, b)
        network[get_pair_id(a, b)] = group
    return network


def read_mapping_table_file(file_path: str) -> dict[str, list[str]]:
    """Read mapping file where the first column is the peptide sequence and the following columns are proteins that map to that sequence.

    Args:
        file_path (str): path to the tab-separated mapping table

    """
    try:
        with open(file_path, mode="r") as r:
            raw_text = r.read().split("\n")
        mapping_res: dict[str, list[str]] = dict()
        uniq_sequences: set[str] = set()
        for line in raw_text:
            if "\t" in line:
                vals = line.split("\t")
                seq = vals[0]
                if seq in uniq_sequences:
                    logging.warning(
                        f"Peptide sequence {seq} duplicated! Keeping first instance."
                    )
                else:
                    uniq_sequences.add(seq)
                    mapping_res[seq] = vals[1:]
        if len(mapping_res) == 0:
            logging.error(f"No peptide sequences found in mapping file: {file_path}")
            raise ValueError("No peptide sequence identified")
        return mapping_res
    except FileNotFoundError:
        logging.error(f"Could not find mapping table file at {file_path}!")
        raise ValueError("Could not read mapping table: File not found.")
