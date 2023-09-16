from functools import partial
import numpy as np
from datetime import datetime

import polars as pl

import rust

from wordle_solver.constants import HARD_MODE


def get_from_index(key, index, array):
    """Returns the value at the index of the array
    stored in a separate index location.
    """
    i = np.where(index == key)[0]

    return array[i] if i else ValueError(f"key {key} not found in index")


def filter_words(
    guess_result: list, possible_solutions: np.array, score_card: dict
) -> np.array:
    """Returns 1d Boolean array (length=possible_solutions)
    where:
      False=word is not a solution based on the board
      True=word is still a possible solution
    """
    compare_to_result = partial(np.array_equal, guess_result)
    filtered = np.apply_along_axis(compare_to_result, 2, score_card).flatten()

    return np.logical_and(filtered, possible_solutions)


def find_minimax(
    all_words: list[str], score_cards: np.array, possible_solutions: np.array
) -> tuple:
    """Returns the best word to guess given the
    word list (all_words), how each word scores against
    all words in the word list, and what words remain
    a possible solution to the puzzle.

    "Best" is defined as the word that will obtain the
    information to elimate the most words in the worst
    case scenario (gets scored in a way that narrows down
    the solution as small as possible).
    """

    max_remaining = score_cards.map_rows(
        lambda x: rust.highest_count_of_unique(pl.Series(x))
    )

    best_index = max_remaining.select(pl.col("map").arg_min())[0, 0]

    return all_words[best_index], max_remaining.min()[0, 0]


def get_best_guess(score_cards: pl.DataFrame) -> pl.DataFrame:
    possible_solutions = score_cards.clone()
    K = 5  # limit top guesses
    N = 6  # number of rounds to run
    for round_num in range(N):
        worst_cases = (
            (
                possible_solutions.group_by("_guess", "value")
                .count()
                # filter to maximun count for each guess
                .filter(pl.col("count").max().over("_guess") == pl.col("count"))
                .select("_guess", pl.col("value"), "count")
                .sort("count")[0:K]  # limit to top K
            )
            # join to create possible_solutions remainging.
            .join(score_cards, how="inner", on=["_guess", "value"]).select(
                "_guess",
                pl.col("variable"),  # possible solutions remaining
            )
        )

        best_worst_cases = worst_cases.group_by("_guess").agg(
            pl.col("variable").count().alias("count")
        )
        print(f"round {round_num}: best guesses so far are")
        print(best_worst_cases)

        possible_solutions = worst_cases.join(
            score_cards, how="left", on=["variable"]
        ).select(
            pl.col("_guess_right").alias("_guess"),
            "variable",
            "value",
        )
