from __future__ import annotations

import logging
import warnings
from concurrent.futures import ThreadPoolExecutor
from math import ceil
from typing import List, Tuple

import numpy as np
import pandas as pd
from scipy import sparse


def collect_alleles(
    df: pd.DataFrame, id_col_name: str, locus_col_names: List[str]
) -> pd.DataFrame:
    """
    Given a data frame and the column names containing ID and STR loci, return a long
    data frame of unique alleles at observed loci for every ID.

    :param df: a data frame of STR profile data
    :param id_col_name: the name of the column containing an ID
    :param locus_col_names: the names of columns containing STR loci
    :return: a data frame of unique (ID, locus, allele) records
    """

    # get all alleles as a long data frame (one allele per profile-locus)
    alleles = df.melt(
        id_vars=[id_col_name],
        value_vars=locus_col_names,
        var_name="locus",
        value_name="allele",
    ).dropna()

    alleles = alleles.rename(columns={id_col_name: "id"})

    alleles = alleles.set_index(["id", "locus"])

    # make data frame of unique (ID, locus, allele) records
    alleles = (
        alleles["allele"]
        .str.extractall(r"(?P<allele>\d+(?:\.\d)?)")
        .reset_index()
        .drop(columns="match")
        .drop_duplicates()
        .sort_values(["id", "locus", "allele"])
        .reset_index(drop=True)
    )

    # use categories since this data frame and its derivations might be large
    alleles[["id", "locus", "allele"]] = alleles[["id", "locus", "allele"]].astype(
        "category"
    )

    return alleles


def count_shared_alleles(
    df: pd.DataFrame,
    id_col_name: str,
    locus_col_name: str,
    allele_col_name: str,
) -> Tuple[np.ndarray, List[str]]:
    """
    Given a long data frame with a columns for ID (i.e. sample ID), STR locus name (e.g.
    "tpox"), and count of a single allele (e.g. "11.1"), construct a symmetric numpy
    array such that cells `(i, j)` and `(j, i)` are the number of shared allele counts
    across all STR loci in samples `i` and `j`.

    :param df: a data frame prepared by `collect_alleles`
    :param id_col_name: name of column containing a sample ID
    :param locus_col_name: name of column containing an STR locus name
    :param allele_col_name: name of column containing an allele count
    :return: a tuple of (1) a symmetrix matrix counting the common allele for pairs of
    samples and (2) this matrix's row/column names (sample IDs)
    """

    # create indicator before pivoting into a sparse array
    df["present"] = True

    # pivot into wide data frame indicating presence of each allele counts at each locus
    with warnings.catch_warnings():
        warnings.simplefilter(action="ignore", category=FutureWarning)
        df = df.pivot(
            values="present",
            index=[locus_col_name, allele_col_name],
            columns=id_col_name,
        ).notna()

    # convert to sparse matrix (id_col_name by locus_allele_cols)
    x = sparse.csc_array(df, dtype=np.uint16)

    # get symmetric matrix (ID by ID) of pairwise intersection set sizes
    x = chunked_gram_matrix(x, max_chunk_size=500)

    return x, df.columns.tolist()


def chunked_gram_matrix(x: sparse.csc_array, max_chunk_size: int) -> np.ndarray:
    """
    Calculate the gram matrix ((x^T)x) for a given matrix `x` in chunks.

    :param x: a numpy array
    :param max_chunk_size: the maximum number of columns per chunk
    :return: the gram matrix
    """

    n_col = x.shape[1]  # pyright: ignore
    n_chunks = 1 + n_col // max_chunk_size
    chunk_size = n_col / n_chunks

    y = np.zeros((n_col, n_col), dtype=np.uint16)

    def compute_chunk(i: int) -> Tuple[int, int, np.ndarray]:
        """
        Compute the gram matrix of a subset of `x`.

        :param i: the chunk index
        :return: a tuple of the row indexes and dense numpy array for this chunk
        """

        logging.info(f"Calculating gram matrix (chunk {i + 1} of {n_chunks})")

        i1 = ceil(i * chunk_size)
        i2 = min(ceil((i + 1) * chunk_size), n_col)

        chunk = x[:, i1:i2]  # pyright: ignore
        result = chunk.T.dot(x).toarray()

        return i1, i2, result

    with ThreadPoolExecutor() as executor:
        for i1, i2, result in executor.map(compute_chunk, range(n_chunks)):
            y[i1:i2, :] = result

    return y


def count_common_loci(
    df: pd.DataFrame,
    id_col_name: str,
    locus_col_name: str,
) -> Tuple[np.ndarray, List[str]]:
    """
    Given a long data frame with a columns for ID (i.e. sample ID), STR locus name (e.g.
    "tpox"), and count of a single allele (e.g. "11.1"), construct a symmetric numpy
    array such that cells `(i, j)` and `(j, i)` are the total number of observed alleles
    in samples `i` and `j` at STR loci observed in both samples.

    :param df: a data frame prepared by `collect_alleles`
    :param id_col_name: name of column containing a sample ID
    :param locus_col_name: name of column containing an STR locus name
    :return: a tuple of (1) a symmetrix matrix counting the number of alleles at common
    loci for pairs of samples and (2) this matrix's row/column names (sample IDs)
    """

    # create indicator before pivoting into a sparse array
    df["present"] = True

    # pivot into wide data frame counting alleles observed at each locus
    with warnings.catch_warnings():
        warnings.simplefilter(action="ignore", category=FutureWarning)
        loci = df.pivot_table(
            values="present",
            index=id_col_name,
            columns=locus_col_name,
            aggfunc=np.sum,  # pyright: ignore
        )

    # save the row names for later
    ids = loci.index.tolist()

    # Minkowski addition gives us the pairwise sums of the rows
    m = np.array(loci)
    x = (m[:, None] + m).reshape(-1, m.shape[1])

    # construct another matrix of the same shape, but this time use 0/1 to indicate
    # which loci are present in both profiles for each pair
    m[m > 0] = 1
    xz = (m[:, None] * m).reshape(-1, m.shape[1])

    # sum the number of alleles in each pair, but only at loci where both profiles
    # had allele data
    nz_pair_combs = x * xz  # element-wise
    nz_pair_sums = np.sum(nz_pair_combs, axis=1).reshape((m.shape[0], m.shape[0]))

    return nz_pair_sums, ids


def compute_tanabe_scores(
    shared_alleles: np.ndarray,
    shared_alleles_names: List[str],
    common_loci: np.ndarray,
    common_loci_names: List[str],
) -> Tuple[np.ndarray, List[str]]:
    """
    Compute the Tanabe score for pairs of IDs, given previously-calculated counts of
    shared alleles and common markers.

    :param shared_alleles: an array from `count_shared_alleles`
    :param shared_alleles_names: a list of row/col IDs for `shared_alleles`
    :param common_loci: an array from `count_common_loci`
    :param common_loci_names: a list of row/col IDs for `common_loci`
    :return: a data frame with Tanabe scores for pairs of IDs
    """

    np.testing.assert_array_equal(
        shared_alleles_names,
        common_loci_names,
        err_msg="shared_alleles and common_loci row/col names do not match",
    )

    return (
        np.divide(
            2 * shared_alleles,
            common_loci,
            out=np.zeros_like(shared_alleles, dtype=np.float64),
            where=common_loci != 0,
            dtype=np.float64,
        ),
        shared_alleles_names,
    )


def scores_array_to_df(
    shared_alleles: np.ndarray,
    shared_alleles_names: List[str],
    common_loci: np.ndarray,
    common_loci_names: List[str],
    tanabe_scores: np.ndarray,
    tanabe_scores_names: List[str],
    symmetric: bool = False,
) -> pd.DataFrame:
    """
    Convert a symmetric Tanabe score matrix into a long-form Pandas DataFrame.

    :param shared_alleles: an array from `count_shared_alleles`
    :param shared_alleles_names: a list of row/col IDs for `shared_alleles`
    :param common_loci: an array from `count_common_loci`
    :param common_loci_names: a list of row/col IDs for `common_loci`
    :param tanabe_scores: an array from `compute_tanabe_scores`
    :param tanabe_scores_names: list of row/col IDs for `tanabe_scores
    :param symmetric: if True, include both (id1, id2) and (id2, id1) rows
    :return: a DataFrame with columns ['id1', 'id2', 'tanabe_score']
    """

    if len({*shared_alleles.shape, *common_loci.shape, *tanabe_scores.shape}) > 1:
        raise ValueError("Input matrices must be square and identical.")

    np.testing.assert_array_equal(
        shared_alleles_names,
        common_loci_names,
        err_msg="shared_alleles_names and common_loci_names do not match",
    )

    np.testing.assert_array_equal(
        shared_alleles_names,
        tanabe_scores_names,
        err_msg="shared_alleles_names and tanabe_scores_names do not match",
    )

    np.testing.assert_array_equal(
        common_loci_names,
        tanabe_scores_names,
        err_msg="common_loci_names and tanabe_scores_names do not match",
    )

    if len(tanabe_scores_names) != tanabe_scores.shape[0]:
        raise ValueError("Length of names must match matrix dimensions.")

    i_upper, j_upper = np.triu_indices_from(tanabe_scores, k=1)
    id1 = pd.Categorical.from_codes(i_upper, categories=tanabe_scores_names)
    id2 = pd.Categorical.from_codes(j_upper, categories=tanabe_scores_names)

    df = pd.DataFrame(
        {
            "id1": id1,
            "id2": id2,
            "shared_alleles": shared_alleles[i_upper, j_upper],
            "common_loci": common_loci[i_upper, j_upper],
            "tanabe_score": tanabe_scores[i_upper, j_upper],
        }
    ).astype(
        {
            "shared_alleles": "uint8",
            "common_loci": "uint8",
            "tanabe_score": "float64",
        }
    )

    if symmetric:
        df = pd.concat(
            [df, df.rename(columns={"id1": "id2", "id2": "id1"})[::-1]],
            ignore_index=True,
        )

    return df.reset_index(drop=True)  # pyright: ignore
