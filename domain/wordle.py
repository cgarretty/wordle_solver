from attrs import define, Factory, field, frozen, cmp_using
import numpy as np

from rust import score_guess

WORD_SIZE = 5


@frozen
class TileScore:
    in_position: bool
    in_word: bool


GRAY = TileScore(False, False)
GREEN = TileScore(True, False)
YELLOW = TileScore(False, True)


@define
class Board:
    answer: str = field(eq=cmp_using(eq=np.array_equal))
    guesses: list[str] = Factory(list)
    scores: list[TileScore] = Factory(list)
    max_guesses: int = 6

    def score(self, guess):
        self.guesses.append(guess)

        in_position, in_word = score_guess(self.answer, guess)
        score = [TileScore(x, y) for x, y in zip(in_position, in_word)]

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
