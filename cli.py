import random
import json
import sys

import colorama

from domain import wordle

YELLOW_EMOJI = "🟨"
GRAY_EMOJI = "⬛"
GREEN_EMOJI = "🟩"

def scorecard(board):
    return "Scorecard:\n" + \
    f"Wordle ### {len(board.guesses)}/{board.max_guesses}\n" + \
    "\n".join(
        "".join(
            GREEN_EMOJI if tile == wordle.GREEN else YELLOW_EMOJI if tile == wordle.YELLOW else GRAY_EMOJI
            for tile in score
        ) for score in board.scores
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


if __name__ == "__main__":
    with open("database.json", "r") as f:
        word_lists = json.load(f)
    all_words = word_lists["herrings"] + word_lists["solutions"]
    answer = random.choice(word_lists["solutions"])
    board = wordle.Board(answer=answer)
    play_wordle(board, all_words)
