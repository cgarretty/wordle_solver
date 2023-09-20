import collections
import numpy as np

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


def find_worst_case(cases: np.array) -> np.array:
    worst_cases = lambda x: x.most_common(1)[0]
    return [worst_cases(c) for c in cases]


def find_best_worst_case(
    worst_cases: np.array, guesses: np.array, breadth: int
) -> np.array:
    scores, counts = zip(*worst_cases)
    scores = np.array(scores)
    counts = np.array(counts)
    # find gueseses, score and count of the best worst case
    sorted = np.argsort(counts)
    top_guesses = np.take_along_axis(guesses, sorted, axis=0)[:breadth]
    top_counts = np.take_along_axis(counts, sorted, axis=0)[:breadth]
    top_scores = np.take_along_axis(scores, sorted, axis=0)[:breadth]

    return list(zip(top_guesses.tolist(), top_scores.tolist(), top_counts.tolist()))


def find_best_guess(
    answers: list, guesses: list, round: int = None, breadth: int = 5
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
        return answers[0], round + 1

    # initialize possible solutions to all words
    score_cards = fortran_wordle.score_guesses(guesses, answers)
    cases = np.apply_along_axis(collections.Counter, 1, score_cards)

    worst_cases = find_worst_case(cases)
    best_worst_cases = find_best_worst_case(worst_cases, guesses, breadth)

    max_rounds = []
    for i, (guess, worst_case, count) in enumerate(best_worst_cases):
        a = filter_words(guess, worst_case, answers)
        # if HARD_MODE:
        #     guesses = filter_words(guess, worst_case, guesses)

        g, r = find_best_guess(a, guesses, round=(round + 1))
        max_rounds.append(r)

    cases = list(zip(best_worst_cases, max_rounds))
    cases.sort(key=lambda x: (x[1], x[0][2]))

    return cases[0][0][0], cases[0][1]
