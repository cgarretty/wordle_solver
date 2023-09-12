from functools import partial
import numpy as np

from constants import HARD_MODE


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
    word_count = len(all_words)
    # send the answer when possible_solutions is down to just one
    # True value. since np.argmin will behave unexpectedly.
    if sum(possible_solutions) == 1:
        answer_index = np.argmax(possible_solutions)
        return all_words[answer_index], 0

    # store count of the largest set of remaining words, if that index
    # in all_words were guessed.
    max_remaining_words = np.empty(shape=(word_count), dtype=np.int64)
    for word_index in range(word_count):
        if not possible_solutions[word_index] and HARD_MODE:
            continue
        # get the score_card for each guessable word
        score_card = score_cards[word_index]
        # find the largest set of a specfic result given a specific guess
        _, counts = np.unique(
            score_card[possible_solutions], return_counts=True, axis=(0)
        )
        count_of_biggest_group = max(counts)
        max_remaining_words[word_index] = count_of_biggest_group

    best_index = np.argmin(max_remaining_words)
    best_word = all_words[best_index]
    remaining_after_guess = max_remaining_words[best_index]

    return best_word, remaining_after_guess
