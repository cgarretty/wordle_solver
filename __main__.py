import json
import sys
from os.path import exists
import pickle

import numpy as np
import pandas as pd

# Game config
HARD_MODE = False # TODO: be able to toggle to hard mode.
WORD_SIZE = 5
ROUNDS = 6

# Optimization config
USE_CACHE = True
USE_PRECALC_FIRST_GUESS = True
PATH_TO_CACHE = './all_words_score_cards.pickle'


def get_result_structure(feedback: str) -> np.array:
    """Return structured array of feedback from a guessed word.
       feedback is a character string with characters 0-2.
       0=Gray, 1=Yellow, 2=Green for each tile in a Wordle
       guess.

       The result_structure returned is an 2d array shaped
       (WORD_SIZE, 2), which matches the shape of the
       score_card for each word.
    """
    guess_result = np.array([int(o) for o in feedback], dtype=np.int32)
    result_structure = np.zeros(shape=(WORD_SIZE, 2), dtype=bool)

    for i, letter in enumerate(guess_result):
        if letter == 2:
            result_structure[i, :] = True
        if letter == 1:
            result_structure[i, 1] = True

    return result_structure


def get_bytecode_array(word_list: list) -> np.array:
    """Returns n sized numpy array with shape (n, s) where:
            n = len(word_list)
            s = word_size
    """
    word_array = np.array(word_list, dtype=bytes)

    return word_array.view('S1').reshape((word_array.size, WORD_SIZE))


def get_display_name(word: np.array) -> str:
    """Returns the uppercase string of byte array.
       e.g. np.array(b's', b't', b'o', b'a', b'e') -> 'STOAE'
    """
    return ''.join([l.decode("utf-8") for l in word]).upper()


def score_word(guess_word: np.array, all_words: np.array) -> np.array:
    """Returns the "score_card" for a given guess_word.
       The score_card represents the what the Wordle board
       would return if you play the guess word. So the
       axes represent:

       0 = The word (same index as supplied word_list).
       1 = The letter.
       2 = The score. The first element is if the letter
           is in the correct position, and the second
           element is if the letter exists in the word.
           i.e. [True, True] = Green, [False, True] = Yellow,
           [False, False] = Gray
    """
    # make a copy so we don't mutate the original
    all_words_copy = all_words.copy()

    # The additional dimension is for the two possible matches
    # (position and "in the word").
    score_card = np.zeros(shape=(len(all_words), WORD_SIZE, 2), dtype=bool)

    # check for exact positional matches (scored as 2's)
    for letter_index, letter in enumerate(guess_word):
        letter_exact_match = all_words[:, letter_index] == letter
        score_card[letter_exact_match, letter_index, :] = True

    # consider these letters "settled," so they're not double
    # counted when discovering yellow letters.
    all_words_copy[np.all(score_card, axis=2)] = None

    # check for matches in word (scored as 1's)
    for letter_index, letter in enumerate(guess_word):
        letter_position = np.isin(all_words_copy, letter)
        score_card[np.any(letter_position, axis=1), letter_index, 1] = True
        # settle the letter in the first found position
        all_words_copy[letter_position.cumsum(axis=1).cumsum(axis=1) == 1] = None

    return score_card


def filter_words(best_guess, guess_result, possible_solutions, score_card):
    """Returns 1d Boolean array (length=possible_solutions)
       where:
         False=word is not a solution based on the board
         True=word is still a possible solution
    """
    possible_solutions_copy = possible_solutions.copy()
    for i, score in enumerate(score_card):
        if not np.array_equal(score, guess_result):
            possible_solutions_copy[i] = False

    return possible_solutions_copy


def score_all_words(all_words: np.array) -> str:
    """Return the score_cards for all words in all_words.
       see `score_words` for more details.
    """
    all_score_cards = {}
    for word_index, word in enumerate(all_words):
        display_name = get_display_name(word)
        if cache:
            score_card = cache[display_name]
        else:
            score_card = score_word(word, all_words)
            all_score_cards.update({display_name: score_card})

    # refresh cache
    with open(PATH_TO_CACHE, 'wb') as db:
        pickle.dump(all_score_cards, db)

    return all_score_cards


def find_minimax(all_words, score_cards, possible_solutions) -> tuple:
    """Returns the best word to guess given the
       word list (all_words), how each word scores against
       all words in the word list, and what words remain
       a possible solution to the puzzle.

       "Best" is defined as the word that will obtain the
       information to elimate the most words in the worst
       case scenario (gets scored in a way that narrows down
       the solution as least as possible).
    """
    # send the answer when possible_solutions is down to just one
    # True value. since np.argmin will behave unexpectedly.
    if sum(possible_solutions) == 1:
        answer_index = np.argmax(possible_solutions)
        return all_words[answer_index], 0

    # store count of the largest set of remaining words, if that index
    # in all_words were guessed.
    max_remaining_words = np.zeros(shape=(len(all_words)), dtype=np.int64)
    for word_index, word in enumerate(all_words):
        # get the score_card for each guessable word
        display_name = get_display_name(word)
        score_card = score_cards[display_name]
        # find the largest set of a specfic result given a specific guess
        _, counts = np.unique(
            score_card[possible_solutions],
            return_counts=True,
            axis=(0)
        )
        count_of_biggest_group = max(counts)
        max_remaining_words[word_index] = count_of_biggest_group

    best_index = np.argmin(max_remaining_words)
    print(best_index)
    best_word = all_words[best_index]
    remaining_after_guess = max_remaining_words[best_index]

    return best_word, remaining_after_guess


with open("./database.json") as data_file:
    words = json.load(data_file)
    all_words = get_bytecode_array(words["herrings"] + words["solutions"])

# Caching the score_cards for faster results
get_from_cache = exists(PATH_TO_CACHE) and USE_CACHE
if get_from_cache:
    with open(PATH_TO_CACHE, 'rb') as db:
        score_cards = pickle.load(db)
else:
    score_cards = score_all_words(all_words)

possible_solutions = np.ones(shape=all_words.shape[0], dtype=bool)
# start the rounds of guessing
for round in range(ROUNDS):
    print("possible_solutions remaining:", sum(possible_solutions))
    # choose the best guess
    # pre-calculated first word for speed
    if round == 0 and USE_PRECALC_FIRST_GUESS:
        best_guess = np.array([b's', b'e', b'r', b'a', b'i'])
        max_remaining = 697
    else:
        best_guess, max_remaining = find_minimax(
            all_words,
            score_cards,
            possible_solutions,
        )

    # Write the best guess to screen
    display_name = get_display_name(best_guess)
    print(f"my best guess is {display_name} ({max_remaining} solutions at most)")

    # get user input. String of 5 numbers (0=gray, 1=yellow, 2=green)
    feedback = input("feedback: ")
    if feedback == "22222":
        sys.exit("I WIN!")

    # filter the possible solutions based on result
    result = get_result_structure(feedback)
    score_card = score_cards[display_name]
    possible_solutions = filter_words(
        best_guess,
        result,
        possible_solutions,
        score_card,
    )

print("I LOSE :(")
