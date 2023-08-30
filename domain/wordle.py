from attrs import frozen, define, Factory, cmp_using, field

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
    answer = field(eq=cmp_using(eq=np.array_equal))
    word_size: int = 5

    def score(self, guess):
        score = [GRAY] * self.word_size  # list of 5 gray tiles

        answer_letters = [*self.answer]
        guess_letters = [*guess]

        print(f"answer_letters at start: {answer_letters}")

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
