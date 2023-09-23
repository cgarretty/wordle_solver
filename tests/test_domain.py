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


def test_another_tough_example_is_correct():
    game = wordle.Board(answer="stoop")
    guess = "books"

    test_result = [
        wordle.GRAY,
        wordle.YELLOW,
        wordle.GREEN,
        wordle.GRAY,
        wordle.YELLOW,
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


def test_broken_example():
    game = wordle.Board(answer="clear")
    guess = "nares"
    test_results = [
        wordle.GRAY,
        wordle.YELLOW,
        wordle.YELLOW,
        wordle.YELLOW,
        wordle.GRAY,
    ]

    assert test_results == game.score(guess)


def test_out_of_guesses():
    game = wordle.Board(answer="steep", max_guesses=6)
    guesses = ["elect", "treat", "treat", "treat", "treat"]

    for guess in guesses:
        game.score(guess)

    with pytest.raises(wordle.OutOfGuesses):
        game.score("treat")


def test_you_win():
    game = wordle.Board(answer="steep", max_guesses=6)
    guesses = ["elect", "treat", "treat", "treat", "treat"]

    for guess in guesses:
        game.score(guess)

    with pytest.raises(wordle.YouWin):
        game.score("steep")


def test_guess_case_lt():
    first_guess = wordle.GuessCase(guess=b"serai", score=b"00010", count=697)
    second_guess = wordle.GuessCase(guess=b"phony", score=b"00000", count=480)

    assert first_guess > second_guess


def test_guess_case_sort():
    cases = [
        wordle.GuessCase(guess=b"serai", score=b"00010", count=697),
        wordle.GuessCase(guess=b"phony", score=b"00000", count=480),
    ]
    cases.sort()

    assert cases[0].guess == b"phony"
