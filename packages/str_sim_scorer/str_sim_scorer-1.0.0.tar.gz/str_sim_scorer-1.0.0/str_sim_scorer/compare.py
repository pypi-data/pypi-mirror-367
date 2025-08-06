from __future__ import annotations

from typing import Dict, List, Literal, Union

import numpy as np
import pandas as pd

from str_sim_scorer.utils import (
    collect_alleles,
    compute_tanabe_scores,
    count_common_loci,
    count_shared_alleles,
    scores_array_to_df,
)


def compare(
    df: pd.DataFrame,
    id_col_name: str,
    locus_col_names: List[str],
    output: Literal["df", "symmetric_df", "array"],
) -> Union[Dict[str, Union[np.ndarray, List[str]]], pd.DataFrame]:
    """
    Given a data frame containing STR profile data and column name information, compute
    the Tanabe score ("non-empty markers" mode) for all pairs of records.

    :param df: a data frame of STR profile data
    :param id_col_name: the name of the column containing a sample/profile/patient ID
    :param locus_col_names: the names of columns containing STR loci
    :param output: the output format requested (data frame, symmetric data frame, array)
    :return: a data frame of Tanabe scores, or an array of Tanabe scores along with its
    row/column names (the IDs)
    """

    # get long data frame of unique (ID, locus, allele) records
    alleles = collect_alleles(df, id_col_name, locus_col_names)

    # count alleles shared by pairs of IDs
    shared_alleles, shared_alleles_names = count_shared_alleles(
        df=alleles, id_col_name="id", locus_col_name="locus", allele_col_name="allele"
    )

    # sum markers at common loci for all pairs of IDs
    common_loci, common_loci_names = count_common_loci(
        df=alleles, id_col_name="id", locus_col_name="locus"
    )

    # compute the Tanabe score (non-empty markers ode)
    tanabe_scores, tanabe_scores_names = compute_tanabe_scores(
        shared_alleles, shared_alleles_names, common_loci, common_loci_names
    )

    if output == "array":
        # return a dict of symmetric arrays along with row/column names (the IDs)
        return {
            "shared_alleles": shared_alleles,
            "common_loci": common_loci,
            "tanabe_scores": tanabe_scores,
            "names": tanabe_scores_names,
        }

    elif output == "df":
        # return long data frame of just one triangular of the matrix
        return scores_array_to_df(
            shared_alleles,
            shared_alleles_names,
            common_loci,
            common_loci_names,
            tanabe_scores,
            tanabe_scores_names,
        )

    elif output == "symmetric_df":
        # duplicate rows for (id1, id2) scores as (id2, id1)
        return scores_array_to_df(
            shared_alleles,
            shared_alleles_names,
            common_loci,
            common_loci_names,
            tanabe_scores,
            tanabe_scores_names,
            symmetric=True,
        )
