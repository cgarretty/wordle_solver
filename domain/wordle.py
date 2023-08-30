from attrs import asdict, define, make_class, Factory, field, frozen, cmp_using

import numpy as np


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
    word_size: int = 5
    guesses: list[str] = Factory(list)
    max_guesses: int = 6

    def score(self, guess):
        if len(self.guesses) >= self.max_guesses:
            raise OutOfGuesses

        self.guesses.append(guess)
        score = [GRAY] * self.word_size  # list of 5 gray tiles
        answer_letters = [*self.answer]
        guess_letters = [*guess]

        for letter_index, guess_letter in enumerate(guess_letters):
            # check for matches in word (scored as 1's)
            if guess_letter == answer_letters[letter_index]:
                score[letter_index] = GREEN
                answer_letters[letter_index] = None  # letter settled

        for letter_index, guess_letter in enumerate(guess_letters):
            if guess_letter in answer_letters and score[letter_index] != GREEN:
                score[letter_index] = YELLOW
                found_letter = answer_letters.index(guess_letter)
                answer_letters[found_letter] = None  # letter settled

        return score


class OutOfGuesses(Exception):
    pass
