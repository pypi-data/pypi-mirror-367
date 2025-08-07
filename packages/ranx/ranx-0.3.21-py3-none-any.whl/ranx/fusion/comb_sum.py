from typing import List

from numba import njit, prange
from numba.typed import List as TypedList

from ..data_structures import Run
from .common import (
    convert_results_dict_list_to_run,
    create_empty_results_dict,
    create_empty_results_dict_list,
    to_unicode,
)


# LOW LEVEL FUNCTIONS ==========================================================
@njit(cache=True)
def _comb_sum(results):
    combined_results = create_empty_results_dict()

    for res in results:
        for doc_id in res.keys():
            doc_id = to_unicode(doc_id)
            if combined_results.get(doc_id, False) == False:
                combined_results[doc_id] = sum(
                    [res.get(doc_id, 0.0) for res in results]
                )

    return combined_results


@njit(cache=True, parallel=True)
def _comb_sum_parallel(runs):
    q_ids = TypedList(runs[0].keys())
    combined_results = create_empty_results_dict_list(len(q_ids))

    for i in prange(len(q_ids)):
        q_id = q_ids[i]
        combined_results[i] = _comb_sum([run[q_id] for run in runs])

    return convert_results_dict_list_to_run(q_ids, combined_results)


# HIGH LEVEL FUNCTIONS =========================================================
def comb_sum(runs: List[Run], name: str = "comb_sum") -> Run:
    r"""Computes CombSUM as proposed by [Fox et al.](https://trec.nist.gov/pubs/trec2/papers/txt/23.txt).

    ```bibtex
        @inproceedings{DBLP:conf/trec/FoxS93,
            author    = {Edward A. Fox and
                        Joseph A. Shaw},
            title     = {Combination of Multiple Searches},
            booktitle = {{TREC}},
            series    = {{NIST} Special Publication},
            volume    = {500-215},
            pages     = {243--252},
            publisher = {National Institute of Standards and Technology {(NIST)}},
            year      = {1993}
        }
    ```

    Args:
        runs (List[Run]): List of Runs.
        name (str): Name for the combined run. Defaults to "comb_sum".

    Returns:
        Run: Combined run.

    """
    run = Run()
    run.name = name
    run.run = _comb_sum_parallel(TypedList([run.run for run in runs]))
    run.sort()
    return run
