import collections
import cython
from cython.cimports import numpy as cnp
import numpy as np

from domain import fortran_wordle, constants
from domain.guess_case import GuessCase
from domain.board import Board

WORD_SIZE = 5
GREEN = 2
YELLOW = 1
GRAY = 0


@cython.cfunc
def assign_worst_cases(
    scores: cnp.ndarray,
    guess: cnp.numpy.bytes_,
    parent: object,
) -> object:
    counts = collections.Counter(scores)
    cases = [
        GuessCase(bytes(guess), bytes(score), count, parent=parent)
        for score, count in counts.items()
    ]

    return max(cases)


@cython.ccall
def find_best_guess(
    answers: cnp.ndarray,
    guesses: cnp.ndarray,
    parent_case: GuessCase = None,
    breadth: cython.int = 10,
) -> object:
    """Returns the best word to guess given answers and guesses.

    "Best" is defined as the word that will obtain the
    information to elimate the most words in the worst
    case scenario, in the least rounds.
    """

    # base case: only one answer left
    if answers.shape[0] == 1:
        final = GuessCase(bytes(answers[0]), b"22222", 0, parent=parent_case)
        return final

    if constants.HARD_MODE and parent_case:
        guesses: cnp.ndarray = parent_case.filter_words(guesses)

    # initialize scores to all guesses for all answers
    score_cards = fortran_wordle.score_guesses(guesses, answers)

    # find the worst case scenario for each guess
    worst_cases = [
        assign_worst_cases(scores, guess, parent_case)
        for scores, guess in zip(score_cards, guesses)
    ]

    return min(
        [
            find_best_guess(case.filter_words(answers), guesses, parent_case=case)
            for case in np.sort(worst_cases, axis=0)[:breadth]
        ]
    )
