from attrs import define, Factory, field, cmp_using
import numpy as np
import collections

from domain import fortran_wordle, constants

WORD_SIZE = 5

GREEN = 2
YELLOW = 1
GRAY = 0


@define
class GuessCase:
    guess: bytes
    score: bytes
    count: int = None
    parent: object = None

    def __lt__(self, other) -> bool:
        return (
            self.total_parents(),
            self.total_count(),
            sorted(list(other.score), reverse=True),
        ) < (
            other.total_parents(),
            other.total_count(),
            sorted(list(self.score), reverse=True),
        )

    def __repr__(self) -> str:
        return f"{self.parent} -> {self.guess} - {self.score} ({self.count})"

    def total_parents(self):
        if self.parent is None:
            return 0
        else:
            return 1 + self.parent.total_parents()

    def total_count(self):
        if self.parent is None:
            return self.count
        else:
            return self.count + self.parent.total_count()

    def list_parents(self):
        if self.parent is None:
            return [self]
        else:
            return [self] + self.parent.list_parents()

    def root(self, round: int = 0):
        if self.parent is None:
            return self
        else:
            parents = sorted(self.list_parents())
            return parents[round]

    def filter_words(self, answers):
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
    scores: np.array, guess: np.array, parent: GuessCase
) -> GuessCase:
    counts = collections.Counter(scores)
    cases = [
        GuessCase(guess, score, count, parent=parent) for score, count in counts.items()
    ]

    cases.sort()

    return cases[-1]


def find_best_guess(
    answers: list,
    guesses: list,
    parent_case: GuessCase = None,
    breadth: int = 10,
) -> tuple:
    """Returns the best word to guess given answers and guesses.

    "Best" is defined as the word that will obtain the
    information to elimate the most words in the worst
    case scenario, in the least rounds.
    """

    # base case: only one answer left
    if answers.shape[0] == 1:
        final = GuessCase(answers[0], b"22222", 0, parent=parent_case)
        return final

    if constants.HARD_MODE and parent_case:
        guesses = parent_case.filter_words(guesses)

    # initialize scores to all guesses for all answers
    score_cards = fortran_wordle.score_guesses(guesses, answers)

    # find the worst case scenario for each guess
    worst_cases = [
        assign_worst_cases(score, guess, parent_case)
        for score, guess in zip(score_cards, guesses)
    ]

    return np.sort(
        [
            find_best_guess(case.filter_words(answers), guesses, parent_case=case)
            for case in np.sort(worst_cases, axis=0)[:breadth]
        ]
    )[0]
