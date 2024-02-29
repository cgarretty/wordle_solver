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
BOT_EMOJI = "🤖"
PERSON_EMOJI = "👤"

INITIAL_CASE = wordle.GuessCase(
    bytes("serai", encoding="utf-8"), bytes("00000", encoding="utf-8"),
)

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
    pass


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
        if round == 0:
            case = wordle.find_best_guess(answers, guesses)
        else:
            case = wordle.find_best_guess(answers, guesses, result_case)
        print("worst case path:", case)
        best_guess = case.root(round)
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
            result_case = wordle.GuessCase(
                best_guess.guess,
                bytes(score, encoding="utf-8"),
                parent=result_case if round > 0 else None,
            )
            answers = result_case.filter_words(answers)
            result_case.count = len(answers)

    print("I LOSE :(")


def input_answer(answers, remaining_answers):
    chance = 1
    while chance <= 3:
        answer = input(f"{PERSON_EMOJI} Enter a 5-letter word: ").lower().encode("utf-8")
        # check if the answer is valid
        if answer not in answers:
            print("That's not a in our list, try again.")
        elif answer not in remaining_answers:
            print(f"That word doesn't fit the previous guesses, {3 - chance} chance(s) left.")
            chance += 1
        # if the answer is valid, start the game
        else:
            print(f"You have chosen the word {colorama.Fore.GREEN + str(answer.decode()).upper() + colorama.Fore.RESET}. Let's play!")
            return answer
        
    raise wordle.YouWin
    


@play.command()
def reverse_wordle():
    print("Welcome to Reverse Wordle!")
    print("The year is 2025, and humans now make solutions to silly little games for our robot overlords.")
    print("Enter a 5-letter word as the answer to the puzzle, and the computer will try to guess it.")
    print("After each guess, you can change the answer, but it must fit the previous guesses.")
    print("Computers are impatient, so you will only get THREE CHANCES to change the answer per round.")
    with open(constants.PATH_TO_WORDS) as data_file:
        words = json.load(data_file)
        guesses = np.array(words["solutions"] + words["herrings"], "bytes", order="C")
        answers = (
            np.array(words["solutions"], "bytes", order="C")
            if not constants.EXPANDED_SOLUTIONS
            else guesses
        )

    remaining_answers = answers
    answer = input_answer(answers, remaining_answers)
    board = wordle.Board(answer=answer)
    round = 0
    while True:
        print(f"{BOT_EMOJI} thinking...")
        case = wordle.find_best_guess(remaining_answers, guesses) if round > 0 else INITIAL_CASE
        best_guess = case.root(0)
        try:
            score = board.score(best_guess.guess)
        except wordle.OutOfGuesses:
            print(colorama.Fore.GREEN + f"{BOT_EMOJI} You win, I lose!")
            colorama.deinit()
            print(scorecard(board))
            break
        except wordle.YouWin:
            print(f"{BOT_EMOJI} My best guess is... {colorama.Fore.GREEN + best_guess.guess.decode().upper() + colorama.Fore.RESET}!")
            print(colorama.Fore.RED + f"{BOT_EMOJI} I win, you lose! MUHAHA")
            print(scorecard(board))
            colorama.deinit()
            break

        display_guess = "".join(
            colorama.Fore.GREEN + letter
            if tile == wordle.GREEN
            else colorama.Fore.YELLOW + letter
            if tile == wordle.YELLOW
            else colorama.Fore.LIGHTBLACK_EX + letter
            for letter, tile in zip(best_guess.guess.decode().upper(), score)
        ) + colorama.Fore.RESET

        print(f"{BOT_EMOJI} My best guess is {display_guess}.")
        result_case = wordle.GuessCase(
            best_guess.guess,
            bytes("".join([str(i) for i in score]), encoding="utf-8"),
            parent=best_guess,
        )
        remaining_answers = result_case.filter_words(remaining_answers)
        print("possible answers to choose from:", len(remaining_answers))
    
        change = input("would you like to change the answer? (y/n)")
        if change == "y":
            try:
                answer = input_answer(answers, remaining_answers)
                board.answer = answer
            except wordle.YouWin:
                print(colorama.Fore.GREEN + f"{BOT_EMOJI} You win, I lose! here are the remaining words:")
                for word in remaining_answers:
                    print(" -", word.decode())
                colorama.deinit()
                print(scorecard(board))
                break
            
        round += 1


if __name__ == "__main__":
    play()
