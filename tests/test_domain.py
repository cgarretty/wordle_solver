import pytest
from domain import wordle, board


def test_guess_result_is_correct():
    game = board.Board(answer="peace")
    guess = "serai"
    test_result = [wordle.GRAY, wordle.GREEN, wordle.GRAY, wordle.YELLOW, wordle.GRAY]

    assert test_result == game.score(guess)


def test_tougher_example_is_correct():
    game = board.Board(answer="stops")
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
    game = board.Board(answer="stoop")
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
    game = board.Board(answer="steep")
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
    game = board.Board(answer="clear")
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
    game = board.Board(answer="steep", max_guesses=6)
    guesses = ["elect", "treat", "treat", "treat", "treat"]

    for guess in guesses:
        game.score(guess)

    with pytest.raises(board.OutOfGuesses):
        game.score("treat")


def test_you_win():
    game = board.Board(answer="steep", max_guesses=6)
    guesses = ["elect", "treat", "treat", "treat", "treat"]

    for guess in guesses:
        game.score(guess)

    with pytest.raises(board.YouWin):
        game.score("steep")


def test_guess_case_lt():
    first_guess = wordle.GuessCase(guess=b"serai", score=b"00010", count=697)
    second_guess = wordle.GuessCase(guess=b"phony", score=b"00000", count=480)

    assert first_guess > second_guess


def test_guess_case_sort_1():
    cases = [
        wordle.GuessCase(guess=b"serai", score=b"01110", count=697),
        wordle.GuessCase(guess=b"phony", score=b"00200", count=697),
    ]
    cases.sort()

    assert cases[0].guess == b"phony"
