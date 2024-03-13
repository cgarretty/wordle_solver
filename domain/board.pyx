from domain import fortran_wordle
cimport numpy as cnp

cdef int WORD_SIZE = 5
cdef int GREEN = 2
cdef int YELLOW = 1
cdef int GRAY = 0

cdef class OutOfGuesses(Exception):
    pass

cdef class YouWin(Exception):
    pass

cdef class Board:
    cdef str answer
    cdef int max_guesses
    cdef list guesses
    cdef list scores

    def __init__(self, str answer, int max_guesses = 6):
        self.answer = answer
        self.max_guesses = max_guesses
        self.guesses = []
        self.scores = []

    cpdef list score(self, str guess):
        cdef list score
        cdef cnp.ndarray byte_score 
        # score guess
        byte_score = fortran_wordle.score_guesses(guess, self.answer)
        score = [int(tile) for tile in str(byte_score, encoding="utf-8")]
        self.guesses.append(guess)
        self.scores.append(score)
        
        if score == [GREEN] * WORD_SIZE:
            raise YouWin
        
        if len(self.guesses) >= self.max_guesses:
            raise OutOfGuesses

        return score

