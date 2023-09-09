from attrs import define, Factory, field, frozen, cmp_using
import numpy as np

from rust import score_guess

WORD_SIZE = 5


@frozen
class TileScore:
    in_position: bool
    in_word: bool


GRAY = TileScore(False, False)
GREEN = TileScore(True, True)
YELLOW = TileScore(False, True)


@define
class Board:
    answer: str = field(eq=cmp_using(eq=np.array_equal))
    guesses: list[str] = Factory(list)
    scores: list[TileScore] = Factory(list)
    max_guesses: int = 6

    def score(self, guess):
        self.guesses.append(guess)

        score = [
            TileScore(tile[0], tile[1]) for tile in score_guess(self.answer, guess)
        ]

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
