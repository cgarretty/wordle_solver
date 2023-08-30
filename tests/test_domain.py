import pytest
from domain import wordle

def test_guess_result_is_correct():
    game = wordle.Board(answer='peace')
    guess = 'serai'
    test_result = [
        wordle.GRAY,
        wordle.GREEN, 
        wordle.GRAY, 
        wordle.YELLOW, 
        wordle.GRAY
    ]
    
    assert test_result == game.score(guess)

def test_tougher_example_is_correct():
    game = wordle.Board(answer='stops')
    guess = 'books'

    test_result = [
        wordle.GRAY,
        wordle.GRAY,
        wordle.GREEN,
        wordle.GRAY,
        wordle.GREEN,
    ]

    assert test_result == game.score(guess)