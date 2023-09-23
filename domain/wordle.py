from attrs import define, Factory, field, cmp_using
import numpy as np
import collections

from domain import constants
from domain import fortran_wordle

WORD_SIZE = 5

GREEN = 2
YELLOW = 1
GRAY = 0


@define
class GuessCase:
    guess: bytes
    score: bytes
    count: int
    parent: object = None

    def __eq__(self, __value) -> bool:
        return self.guess == __value.guess and self.score == __value.score

    def __lt__(self, __value) -> bool:
        return self.count <= __value.count

    def filter_answers(self, answers):
        possible_solutions = answers[
            fortran_wordle.score_guesses(
                np.array([self.guess], "bytes", order="C"), answers
            ).squeeze()
            == self.score
        ]

        return possible_solutions


@define
class Board:
    answer: str = field(eq=cmp_using(eq=np.array_equal))
    guesses: list[str] = Factory(list)
    scores: list[int] = Factory(list)
    max_guesses: int = 6

    def score(self, guess):
        self.guesses.append(guess)
        byte_score = fortran_wordle.score_guesses(guess, self.answer)
        score = [int(tile) for tile in str(byte_score, encoding="utf-8")]
        self.scores.append(score)
        if score == [GREEN] * WORD_SIZE:
            raise YouWin
        if len(self.guesses) >= self.max_guesses:
            raise OutOfGuesses

        return score


class OutOfGuesses(Exception):
    pass


class YouWin(Exception):
    pass


def assign_worst_cases(
    scores: np.array, guesses: np.array, parent: GuessCase
) -> list[GuessCase]:
    counts = collections.Counter(scores)
    cases = [
        GuessCase(guess, score, count, parent=parent)
        for guess, score, count in zip(guesses, *counts)
    ]
    cases.sort()

    return cases[0]


def find_best_guess(
    answers: list,
    guesses: list,
    parent_case: GuessCase = None,
    breadth: int = 5,
) -> tuple:
    """Returns the best word to guess given the
    word list (all_words), how each word scores against
    all words in the word list, and what words remain
    a possible solution to the puzzle.

    "Best" is defined as the word that will obtain the
    information to elimate the most words in the worst
    case scenario (gets scored in a way that narrows down
    the solution as small as possible).
    """
    if answers.shape[0] == 1:
        return GuessCase(answers[0], b"22222", 1, parent=parent_case)

    # initialize possible solutions to all words
    score_cards = fortran_wordle.score_guesses(guesses, answers)
    worst_cases = np.apply_along_axis(
        assign_worst_cases, 1, score_cards, args=(guesses, parent_case)
    )

    max_rounds = []
    for case in np.sort(worst_cases, axis=0)[:breadth]:
        a = case.filter_words(answers)
        if constants.HARD_MODE:
            guesses = case.filter_words(guesses)
        c = find_best_guess(a, guesses, parent_case=case)
        max_rounds.append(c.find_max_rounds())

    return np.sort(max_rounds, axis=0)[0]
