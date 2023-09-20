import json
import sys
import numpy as np

import constants
import wordle

with open(constants.PATH_TO_WORDS) as data_file:
    words = json.load(data_file)
    all_words = np.array(words["solutions"] + words["herrings"], "bytes", order="C")

answers, guesses = all_words, all_words

0  # start the rounds of guessing
for round in range(constants.ROUNDS):
    print("possible_solutions remaining:", len(answers))
    best_guess, max_rounds = wordle.find_best_guess(answers, guesses, round=round)
    print(best_guess, max_rounds)
    # Write the best guess to screen
    print(
        f"my best guess is {str(best_guess, encoding='utf-8').upper()}"
        f" ({max_rounds} rounds at most)"
    )

    # get user input. String of 5 numbers (0=gray, 1=yellow, 2=green)
    score = input("feedback: ")
    if score == "22222":
        sys.exit("I WIN!")
    else:
        # filter the possible solutions based on result
        answers = wordle.filter_words(
            best_guess, bytes(score, encoding="utf-8"), answers
        )

print("I LOSE :(")
