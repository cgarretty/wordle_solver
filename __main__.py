import json
import sys
from os.path import exists
import pickle

import numpy as np
import pandas as pd

WORD_SIZE = 5
USE_CACHE = True
PATH_TO_CACHE = './all_words_score_cards.pickle'

def score_word(guess_word, all_words):
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


def get_result_structure(feedback):
    guess_result = np.array([int(o) for o in feedback], dtype=np.int32)
    result_structure = np.zeros(shape=(WORD_SIZE, 2), dtype=bool)

    for i, letter in enumerate(guess_result):
        if letter == 2:
            result_structure[i, :] = True
        if letter == 1:
            result_structure[i, 1] = True

    return result_structure

def filter_words(best_word, guess_result, all_words, cache=None):
    score_card = cache if cache else score_word(best_word, all_words)

    remaining_words = []
    for i, score in enumerate(score_card):
        if np.array_equal(score, guess_result):
            remaining_words.append(i)

    return all_words[remaining_words].copy()


def get_bytecode_array(word_list: list) -> np.array:
    """
        Returns n sized numpy array with shape (n, s) where:
            n = len(word_list)
            s = word_size
    """
    word_array = np.array(word_list, dtype=bytes)

    return word_array.view('S1').reshape((word_array.size, WORD_SIZE))

def get_best_guess(all_words, cache=None) -> str:
    # store count of the largest set of remaining words, if that index
    # in all_words were guessed.
    max_remaining_words = np.zeros(shape=(len(all_words)), dtype=np.int64)

    all_score_cards = {}
    for word_index, word in enumerate(all_words):
        display_name = ''.join([l.decode("utf-8") for l in word]).upper()
        if cache:
            score_card = cache[display_name]
        else:
            score_card = score_word(word, all_words)
            all_score_cards.update({display_name: score_card})

        score_card
        _, counts = np.unique(score_card, return_counts=True, axis=(0))
        count_of_biggest_group = max(counts)
        max_remaining_words[word_index] = count_of_biggest_group

    # refresh cache
    with open(PATH_TO_CACHE, 'wb') as db:
        pickle.dump(all_score_cards, db)

    best_index = np.argmin(max_remaining_words)
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
    score_cards=None

possible_solutions = all_words.copy()
# np.ones(shape=all_words.shape[0], dtype=bool)

# start the rounds of guessing
for i in range(6):
    print("possible_solutions remaining:", all_words.shape[0])
    # choose the best guess
    if i == 0 and USE_CACHE: # pre-calculated first word for speed
        best_word = np.array([b's', b'e', b'r', b'a', b'i'])
        max_remaining = 697
    else:
        best_word, max_remaining = get_best_guess(
            all_words,
            cache=score_cards,
        )

    # Write result to screen
    display = ''.join([l.decode("utf-8") for l in best_word]).upper()
    print("my best guess is", display, f"({max_remaining} solutions at most)")

    # string of 5 numbers (0=gray, 1=yellow, 2=green)
    feedback = input("feedback: ")
    if feedback == "22222":
        sys.exit("I WIN!")

    # check the result
    result = get_result_structure(feedback)
    all_words = filter_words(best_word, result, all_words, cache=score_cards)

print("I LOSE :(")
