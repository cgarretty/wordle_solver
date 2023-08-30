import pytest
from domain import wordle


def test_guess_result_is_correct():
    game = wordle.Board(answer="peace")
    guess = "serai"
    test_result = [wordle.GRAY, wordle.GREEN, wordle.GRAY, wordle.YELLOW, wordle.GRAY]

    assert test_result == game.score(guess)


def test_tougher_example_is_correct():
    game = wordle.Board(answer="stops")
    guess = "books"

    test_result = [
        wordle.GRAY,
        wordle.GRAY,
        wordle.GREEN,
        wordle.GRAY,
        wordle.GREEN,
    ]

    assert test_result == game.score(guess)


def test_with_repeated_letters_in_answer():
    game = wordle.Board(answer="steep")
    guess = "elect"
    test_results = [
        wordle.YELLOW,
        wordle.GRAY,
        wordle.GREEN,
        wordle.GRAY,
        wordle.YELLOW,
    ]

    assert test_results == game.score(guess)


def test_out_of_guesses():
    game = wordle.Board(answer="steep", max_guesses=5)
    guesses = ["elect", "treat", "treat", "treat", "treat"]

    for guess in guesses:
        game.score(guess)

    with pytest.raises(wordle.OutOfGuesses):
        game.score("treat")
