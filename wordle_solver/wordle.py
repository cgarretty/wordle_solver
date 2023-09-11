import numpy as np

from constants import HARD_MODE


def find_minimax(
    all_words: list[str], score_cards: dict, possible_solutions: np.array
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
    # send the answer when possible_solutions is down to just one
    # True value. since np.argmin will behave unexpectedly.
    if sum(possible_solutions) == 1 and not HARD_MODE:
        answer_index = np.argmax(possible_solutions)
        return all_words[answer_index], 0

    # store count of the largest set of remaining words, if that index
    # in all_words were guessed.
    max_remaining_words = np.zeros(shape=(len(all_words)), dtype=np.int64)
    for word_index, word in enumerate(all_words):
        # get the score_card for each guessable word
        score_card = score_cards[word]
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
