import random
import json
import sys

import colorama
import click
import numpy as np

from domain import constants, wordle

YELLOW_EMOJI = "🟨"
GRAY_EMOJI = "⬛"
GREEN_EMOJI = "🟩"


def scorecard(board):
    return (
        "Scorecard:\n"
        + f"Wordle ### {len(board.guesses)}/{board.max_guesses}\n"
        + "\n".join(
            "".join(
                GREEN_EMOJI
                if tile == wordle.GREEN
                else YELLOW_EMOJI
                if tile == wordle.YELLOW
                else GRAY_EMOJI
                for tile in score
            )
            for score in board.scores
        )
    )


def play_wordle(board: wordle.Board, wordlist) -> None:
    colorama.init()
    print("Welcome to Wordle!")
    print("Enter a 5-letter word to guess the answer.")
    print(f"You have {board.max_guesses} guesses.", end="\n\n")
    while True:
        try:
            guess = input(colorama.Fore.RESET + f"#{len(board.guesses)} ->").lower()
            if guess not in wordlist:
                sys.stdout.flush()
                print("\r That's not a word, try again.")
                continue
            score = board.score(guess)
            print(
                "".join(
                    colorama.Fore.GREEN + letter
                    if tile == wordle.GREEN
                    else colorama.Fore.YELLOW + letter
                    if tile == wordle.YELLOW
                    else colorama.Fore.LIGHTBLACK_EX + letter
                    for letter, tile in zip(guess.upper(), score)
                )
            )

        except wordle.YouWin:
            print(colorama.Fore.GREEN + board.answer.upper(), "You win!")
            colorama.deinit()
            print(scorecard(board))
            break
        except wordle.OutOfGuesses:
            print("You lose! ->", colorama.Fore.WHITE + board.answer.upper())
            colorama.deinit()
            print(scorecard(board))
            break


@click.group()
def play():
    click.echo("Welcome to Wordle!")


@play.command()
def play_random():
    with open("database.json", "r") as f:
        word_lists = json.load(f)
    all_words = word_lists["herrings"] + word_lists["solutions"]
    answer = random.choice(word_lists["solutions"])
    board = wordle.Board(answer=answer)
    play_wordle(board, all_words)


@play.command()
def wordle_solver():
    with open(constants.PATH_TO_WORDS) as data_file:
        words = json.load(data_file)
        guesses = np.array(words["solutions"] + words["herrings"], "bytes", order="C")
        answers = (
            np.array(words["solutions"], "bytes", order="C")
            if not constants.EXPANDED_SOLUTIONS
            else guesses
        )

    0  # start the rounds of guessing
    for round in range(constants.ROUNDS):
        print("possible answers remaining:", len(answers))
        case = wordle.find_best_guess(answers, guesses)
        best_guess = case.root()
        total_rounds = case.total_parents() + 1
        # Write the best guess to screen
        print(
            f"my best guess is {str(best_guess.guess, encoding='utf-8').upper()}"
            f" ({best_guess.count} max answers left after guess, and {total_rounds} round(s) left)"
        )

        # get user input. String of 5 numbers (0=gray, 1=yellow, 2=green)
        score = input("feedback: ")
        if score == "22222":
            sys.exit("I WIN!")
        else:
            # filter the possible solutions based on result
            case = wordle.GuessCase(
                best_guess.guess,
                bytes(score, encoding="utf-8"),
            )
            answers = case.filter_words(answers)
            case.count = len(answers)

    print("I LOSE :(")


if __name__ == "__main__":
    play()
