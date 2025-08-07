"""Mapping related classes and functions."""

import logging
from dataclasses import dataclass
from enum import Enum, auto

from Bio import SeqIO

from xlranker.config import MappingConfig, config
from xlranker.data import get_default_fasta
from xlranker.util.readers import read_mapping_table_file

logger = logging.getLogger(__name__)


class FastaType(Enum):
    """Types of Fasta files supported by XLRanker."""

    UNIPROT = auto(), "UNIPROT FASTA type"
    GENCODE = auto(), "Gencode FASTA type"


def extract_gene_symbol_uniprot(fasta_description: str) -> str:
    """Get the gene symbol from a UNIPROT style FASTA description.

    Method:

    1. Split the description by spaces
    2. Find split with GN= (Gene Name)
    3. Remove GN= from split and return

    If split with GN= not found, return the UNIPROT symbol.

    1. Using first split (when splitting by space), split again by |
    2. If there is at least 2 elements in split, return second element

    If can't get UNIPROT symbol, return original description.

    Args:
        fasta_description (str): FASTA description string

    Returns:
        str: Gene Symbol from description. If can't be extracted, try getting UNIPROT ID.
             If all fails, return original description

    """
    splits = fasta_description.split(" ")
    for split in splits:
        if "GN=" in split:  # check if gene name split
            return split[3:]  # Remove GN= from string
    splits = splits[0].split("|")
    if len(splits) >= 2:
        return splits[1]
    return fasta_description  # return if failed


def extract_gene_symbol_gencode(fasta_description: str, **kwargs) -> str:
    """Get the gene symbol from a UNIPROT style FASTA description.

    Method:

    1. Split the description by spaces
    2. Find split with GN= (Gene Name)
    3. Remove GN= from split and return

    If split with GN= not found, return the UNIPROT symbol.

    1. Using first split (when splitting by space), split again by |
    2. If there is at least 2 elements in split, return second element

    If can't get UNIPROT symbol, return original description.

    Args:
        fasta_description (str): FASTA description string
        **kwargs: See below.

    Kwargs:
        split_by (str): Character to split description string
        split_index (str): Index (0-based) of gene symbol after splitting.
                           All characters after first space are removed.

    Returns:
        str: Gene Symbol from description. If can't be extracted, return original description

    """
    split_by = kwargs["split_by"]
    split_index = kwargs["split_index"]
    split_res = fasta_description.split(split_by)
    if split_index >= len(split_res):
        return split_res[0]  # keep first split if split_index is too large
    if len(split_res) != 0:
        return split_res[split_index].split(" ")[0]  # remove elements after space
    return fasta_description  # return if failed


@dataclass
class MappingResult:
    """Results from mapping peptide sequences to proteins.

    Args:
        peptide_to_protein (dict[str, list[str]]): Dictionary where keys are peptide sequences and values are the list of proteins that map to that sequence.
        protein_sequences (dict[str, str] | None): Optional dictionary where keys are protein names and values are those proteins sequence. Used for linkage location. None if sequence not available (i.e. mapping table)

    """

    peptide_to_protein: dict[str, list[str]]
    protein_sequences: dict[str, str] | None


def extract_gene_symbol(fasta_description: str, fasta_type: FastaType, **kwargs) -> str:
    """Extract the gene symbol from a FASTA entry based on fasta_type.

    Args:
        fasta_description (str): FASTA entry string
        fasta_type (FastaType): FastaType of the FASTA file. Either UNIPROT or GENCODE
        **kwargs: See below.

    Kwargs:
        split_by (str): Character to split description string. Only used if FastaType is GENCODE.
        split_index (str): Index (0-based) of gene symbol after splitting.
                           All characters after first space are removed.
                           Only used if FastaType is GENCODE.

    Returns:
        str: the gene symbol extracted from the FASTA entry
    """
    match fasta_type:
        case FastaType.UNIPROT:
            return extract_gene_symbol_uniprot(fasta_description).upper()
        case FastaType.GENCODE:
            return extract_gene_symbol_gencode(fasta_description, **kwargs).upper()


def convert_str_to_fasta_type(possible_type: str) -> FastaType:
    """Convert string to FastaType enum. Case insensitive.

    Args:
        possible_type (str): string to convert to FastaType.

    Returns:
        FastaType: FastaType.GENCODE if possible_type is GENCODE. FastaType.UNIPROT for all other cases.

    """
    possible_type = possible_type.upper()
    match possible_type:
        case "UNIPROT":
            return FastaType.UNIPROT
        case "GENCODE":
            return FastaType.GENCODE
        case _:
            return FastaType.UNIPROT  # TODO: Determine if new UNKNOWN type should be created. Maybe a possible error?


class PeptideMapper:
    """Peptide mapper class.

    Raises:
        ValueError: Raises error if there is an issue with mapping tables

    """

    mapping_table_path: str
    split_by: str
    split_index: int
    is_fasta: bool
    fasta_type: FastaType

    def __init__(
        self,
        mapping_table_path: str | None = None,
        split_by: str = "|",
        split_index: int = 3,
        is_fasta: bool = True,
        fasta_type: FastaType = FastaType.UNIPROT,
    ) -> None:
        """Initialize PeptideMapper.

        Args:
            mapping_table_path (str | None, optional): Path to mapping table.
                                                       Can be in fasta or mapping table.
                                                       If none, then uses the default uniprot version
                                                       Defaults to None.
            split_by (str, optional): character in fasta description to split into id components.
                                      Defaults to "|".
            split_index (int, optional): index of gene symbol in fasta file. Defaults to 3.
            is_fasta (bool, optional): is input file fasta file. Defaults to True.
            fasta_type (FastaType): Type of FASTA header. Can be UNIPROT or GENCODE

        """
        if mapping_table_path is None:
            logger.info("Using default gencode fasta file for peptide mapping")
            self.mapping_table_path = get_default_fasta()
            # Make sure variables match defaults
            split_by = "|"
            split_index = 3
            is_fasta = True
        else:
            logger.info("Using custom fasta file for peptide mapping")
            logging.debug(f"FASTA File Path: {mapping_table_path}")
            self.mapping_table_path = mapping_table_path
        self.split_by = split_by
        self.split_index = split_index
        self.is_fasta = is_fasta
        self.fasta_type = fasta_type

    def map_sequences(self, sequences: list[str]) -> MappingResult:
        """Map a list of sequences to genes.

        Args:
            sequences (list[str]): list of sequences to map to genes

        Returns:
            dict[str, list[str]]: dictionary where keys are peptide sequences
                                  values are list of genes that map to that sequence

        """
        if self.is_fasta:  # determine which mapping function to use
            map_res = self.map_fasta(sequences)
        else:  # mapping table just needs to be read
            map_res = MappingResult(
                peptide_to_protein=read_mapping_table_file(self.mapping_table_path),
                protein_sequences=None,
            )
        no_maps = 0
        for seq in sequences:  # verify all sequences have mapping information
            if seq not in map_res.peptide_to_protein:
                logger.debug(f"is_fasta: {self.is_fasta}")
                logger.warning(f"{seq} not found in mapping table!")
            elif len(map_res.peptide_to_protein[seq]) == 0:
                logger.debug(f"is_fasta: {self.is_fasta}")
                logger.warning(f"{seq} maps to no proteins!")
                no_maps += 1
        if no_maps != 0:
            logger.warning(f"{no_maps} sequences do not have mapped proteins")
        return map_res

    def map_fasta(self, sequences: list[str]) -> MappingResult:
        """Map the provided sequences to proteins using a FASTA file.

        Args:
            sequences (list[str]): list of peptide sequences to map.

        Returns:
            MappingResult: Result of the mapping.

        """
        if config.reduce_fasta:
            return self.map_fasta_with_reduction(sequences)
        return self.map_fasta_no_reduction(sequences)

    def map_fasta_no_reduction(self, sequences: list[str]) -> MappingResult:
        """Maps the provided sequences to proteins using the original FASTA file.

        Args:
            sequences (list[str]): list of peptide sequences to map.

        Returns:
            MappingResult: Result of the mapping.

        """
        logger.debug("Mapping FASTA file without reduction")
        matches: dict[str, set[str]] = {}
        for seq in sequences:
            matches[seq] = set()
        logger.info(f"Mapping {len(sequences)} peptide sequences")
        for record in SeqIO.parse(self.mapping_table_path, "fasta"):
            for sequence in sequences:
                if sequence in record.seq:
                    matches[sequence].add(
                        extract_gene_symbol(
                            record.description,
                            self.fasta_type,
                            split_by=self.split_by,
                            split_index=self.split_index,
                        )
                    )

        final_matches: dict[str, list[str]] = {}
        for key in matches:
            final_matches[key] = list(matches[key])
        return MappingResult(peptide_to_protein=final_matches, protein_sequences=None)

    def map_fasta_with_reduction(self, sequences: list[str]) -> MappingResult:
        """Maps the provided sequences to proteins with a modified FASTA file where only the longest sequence is kept for duplicated proteins.

        Duplicate proteins are proteins that share the same gene symbol identification.

        Args:
            sequences (list[str]): list of peptide sequences to map.

        Returns:
            MappingResult: Result of the mapping.

        """
        logger.debug("Mapping FASTA file with reduction")
        matches: dict[str, set[str]] = {}
        for seq in sequences:
            matches[seq] = set()
        logger.info(f"Mapping {len(sequences)} peptide sequences")

        # First, build a mapping from gene symbol to its longest protein sequence
        gene_to_longest_protein = {}
        gene_to_longest_length: dict[str, int] = {}

        for record in SeqIO.parse(self.mapping_table_path, "fasta"):
            gene_symbol = extract_gene_symbol(
                record.description,
                self.fasta_type,
                split_by=self.split_by,
                split_index=self.split_index,
            )
            seq_str = str(record.seq)
            seq_len = len(seq_str)
            if (
                gene_symbol not in gene_to_longest_length
                or seq_len > gene_to_longest_length[gene_symbol]
            ):
                gene_to_longest_length[gene_symbol] = seq_len
                gene_to_longest_protein[gene_symbol] = seq_str

        protein_sequences: dict[str, str] = {}

        # Now, map sequences only if they are present in the longest protein sequence for that gene
        for gene_symbol, protein_seq in gene_to_longest_protein.items():
            mapped = False
            for sequence in sequences:
                if sequence in protein_seq:
                    matches[sequence].add(gene_symbol)
                    mapped = True
            if mapped:
                protein_sequences[gene_symbol] = protein_seq

        final_matches: dict[str, list[str]] = {}
        for key in matches:
            final_matches[key] = list(matches[key])
        return MappingResult(
            peptide_to_protein=final_matches, protein_sequences=protein_sequences
        )

    @staticmethod
    def from_config(mapping_config: MappingConfig) -> "PeptideMapper":
        """Create a PeptideMapper from a MappingConfig object.

        Args:
            mapping_config (MappingConfig): mapping config to build PeptideMapper.

        Returns:
            PeptideMapper: PeptideMapper built according to config options.

        """
        split_by = (
            mapping_config.split_by if mapping_config.split_by is not None else ""
        )
        split_index = (
            mapping_config.split_index if mapping_config.split_index is not None else 0
        )
        if mapping_config.fasta_type is None:
            fasta_type = FastaType.UNIPROT
        else:
            fasta_type = convert_str_to_fasta_type(mapping_config.fasta_type)
        return PeptideMapper(
            mapping_table_path=mapping_config.custom_table,
            split_by=split_by,
            split_index=split_index,
            is_fasta=mapping_config.is_fasta,
            fasta_type=fasta_type,
        )
