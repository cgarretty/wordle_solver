from functools import partial
import numpy as np
from datetime import datetime

import fortran_wordle  # fortran module

from constants import HARD_MODE


def get_from_index(key, index, array):
    """Returns the value at the index of the array
    stored in a separate index location.
    """
    i = np.where(index == key)[0]

    return array[i] if i else ValueError(f"key {key} not found in index")


def filter_words(guess, score, answers) -> np.array:
    """Returns 1d Boolean array (length=possible_solutions)
    where:
      False=word is not a solution based on the board
      True=word is still a possible solution
    """
    scores = fortran_wordle.score_guesses(
        np.array([guess], "bytes", order="C"), answers
    )
    return answers[scores.squeeze() == score]


def find_best_guess(
    answers: list, guesses: list, depth: int = 3, breadth: int = 5
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

    if answers.shape[0] == 1:
        return answers[0], 1

    # initialize possible solutions to all words
    score_cards = fortran_wordle.score_guesses(guesses, answers)

    find_worst_case = lambda x: np.unique(x, return_counts=True)[1].max()
    worst_cases = np.apply_along_axis(find_worst_case, 1, score_cards)
    best_worst_case_index = worst_cases.argmin()

    # return word and max remaining words after guessing it.
    return guesses[best_worst_case_index], worst_cases[best_worst_case_index]
