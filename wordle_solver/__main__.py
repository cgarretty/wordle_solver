import json
import sys
from os.path import exists
import pickle

import numpy as np

import constants
import rust
import wordle

with open(constants.PATH_TO_WORDS) as data_file:
    words = json.load(data_file)
    all_words = words["herrings"] + words["solutions"]

# Caching the score_cards for faster results
get_from_cache = exists(constants.PATH_TO_CACHE) and constants.USE_CACHE
if get_from_cache:
    with open(constants.PATH_TO_CACHE, "rb") as db:
        score_cards = pickle.load(db)
else:
    score_cards = rust.score_all_words(all_words, all_words)

# refresh cache
# with open(constants.PATH_TO_CACHE, "wb") as db:
#     pickle.dump(score_cards, db)


possible_solutions = np.ones(shape=len(all_words), dtype=bool)
# start the rounds of guessing
for round in range(constants.ROUNDS):
    print("possible_solutions remaining:", sum(possible_solutions))
    # choose the best guess
    # pre-calculated first word for speed
    if round == 0 and constants.USE_PRECALC_FIRST_GUESS:
        best_guess = "serai"
        max_remaining = 697
    else:
        best_guess, max_remaining = wordle.find_minimax(
            all_words[possible_solutions] if constants.HARD_MODE else all_words,
            score_cards,
            possible_solutions,
        )

    # Write the best guess to screen
    print(f"my best guess is {best_guess} ({max_remaining} solutions at most)")

    # get user input. String of 5 numbers (0=gray, 1=yellow, 2=green)
    feedback = input("feedback: ")
    if feedback == "22222":
        sys.exit("I WIN!")

    # filter the possible solutions based on result
    result = list(feedback)
    score_card = score_cards[best_guess]
    possible_solutions = rust.filter_words(
        result,
        possible_solutions,
        score_card,
    )

print("I LOSE :(")
