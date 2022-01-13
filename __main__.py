import json
import sys

import numpy as np
import pandas as pd

WORD_SIZE = 5

def is_somewhere(letter_array: np.array, letter) -> np.array:
    letter_mask = np.isin(letter_array, letter)

    return letter_array[np.any(letter_mask, axis=1)]

def is_nowhere(letter_array: np.array, letter, letter_count:int) -> np.array:
    letter_mask = np.isin(letter_array, letter)
    letter_count_mask = np.count_nonzero(letter_mask, axis=1) <= letter_count

    return letter_array[letter_count_mask]

def is_here(letter_array: np.array, letter: str, position: int) -> np.array:

    return letter_array[letter_array[:, position] == letter]

def is_not_here(letter_array: np.array, letter: str, position: int) -> np.array:

    return letter_array[letter_array[:, position] != letter]

def filter_words(guessed_word: list, solutions, all_words):
    previous_letters = list()
    updated_solutions = solutions.copy()
    updated_all_words = all_words.copy()

    # sort descending by feedback value
    sorted_guessed_word = sorted(guessed_word, key=lambda x: x[1], reverse=True)
    for letter, score, i in sorted_guessed_word:

        if score == 0:
            letter_count = len([l for l in previous_letters if l == letter.decode('utf-8')])

            updated_solutions = is_nowhere(updated_solutions, letter, letter_count)
            updated_all_words = is_nowhere(updated_all_words, letter, letter_count)

        if score == 2:
            updated_solutions = is_here(updated_solutions, letter, i)
            updated_all_words = is_here(updated_solutions, letter, i)

        if score == 1:
            updated_solutions = is_not_here(updated_solutions, letter, i)
            updated_all_words = is_not_here(updated_all_words, letter, i)

            updated_solutions = is_somewhere(updated_solutions, letter)
            updated_all_words = is_somewhere(updated_all_words, letter)

        previous_letters.append(letter.decode('utf-8'))

    print(len(updated_all_words), "possible word(s) remaining!")

    return updated_solutions, updated_all_words


def get_bytecode_array(word_list: list, word_size: int) -> np.array:
    """
        Returns n sized numpy array with shape (n, s) where:
            n = len(word_list)
            s = word_size
    """
    word_array = np.array(word_list, dtype=bytes)

    return word_array.view('S1').reshape((word_array.size, 5))


def get_letter_position_frequency(letter_array: np.array, word_size: int) -> pd.DataFrame:
    """
       Returns DataFrame of the letter, position frequencys for
       the given np.array (letter_array).
    """
    letter_position_frequency = {l: [] for l in 'abcdefghijklmnopqrstuvwxyz'}
    for i in range(word_size):
        letters, counts = np.unique(letter_array[:, i], return_counts=True)
        position_frequency = {
            x.decode("utf-8"): y for x, y in list(zip(letters, counts))
        }

        for letter in letter_position_frequency.keys():
            letter_frequency = position_frequency.get(letter, 0)
            letter_position_frequency[letter].append(letter_frequency)

    df = pd.DataFrame(letter_position_frequency).transpose()

    for i in range(word_size):
        df[i] = (df[i] / df[i].sum()) * 100

    return df

def get_highest_score_word(letter_array: np.array, letter_position_frequency: pd.DataFrame, word_size: int) -> str:
    high_score = 0
    high_score_word = ""
    for word in letter_array:
        word_score = sum(
            letter_position_frequency[i][l.decode('utf-8')]
            for l in word
            for i in range(word_size)
        )
        if high_score < word_score:
            high_score = word_score
            high_score_word = word

    if high_score == 0:
        raise KeyError("No words match.")

    display = ''.join([l.decode("utf-8") for l in high_score_word]).upper()
    print("my best guess is", display, "with a score of ", high_score)

    return high_score_word

with open("./database.json") as data_file:
    words = json.load(data_file)
    solutions = get_bytecode_array(words["solutions"], WORD_SIZE)
    all_words = get_bytecode_array(words["herrings"] + words["solutions"], WORD_SIZE)

print("solutions:", solutions.shape)
print("all_words:", all_words.shape)

for i in range(6):
    lpf = get_letter_position_frequency(solutions, WORD_SIZE)
    highest_score_word = get_highest_score_word(all_words, lpf, WORD_SIZE)

    feedback = input("feedback: ") # string of 5 numbers (0=gray, 1=yellow, 2=green)
    if feedback == "22222":
        sys.exit("I WIN!")

    guess_result = np.array([int(o) for o in feedback], dtype=np.int32)
    guessed_word = list(zip(highest_score_word, guess_result, range(WORD_SIZE)))

    solutions, all_words = filter_words(guessed_word, solutions, all_words)

print("I LOSE :(")
