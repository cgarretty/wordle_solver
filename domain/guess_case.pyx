from cpython.object cimport Py_LT, Py_GT


from domain import fortran_wordle
cimport numpy as cnp

cdef class GuessCase:
    cdef public bytes guess 
    cdef public bytes score
    cdef int count
    cdef GuessCase parent

    def __init__(self, bytes guess, bytes score, int count, GuessCase parent = None):
        self.guess = guess
        self.score = score
        self.count = count
        self.parent = parent

    def __richcmp__(self, other, int op):
        cdef:
            list self_score = sorted(self.score, reverse=True)
            list other_score = sorted(other.score, reverse=True)

        if op == Py_LT:
            return (
                self.total_parents(),
                self.total_count(),
                other_score,
            ) < (
                other.total_parents(),
                other.total_count(),
                self_score,
            )

        if op == Py_GT:
            return (
                self.total_parents(),
                self.total_count(),
                other_score,
            ) > (
                other.total_parents(),
                other.total_count(),
                self_score,
            )

    def __repr__(self):
        return "{parent} -> {guess} - {score} ({count})".format(
            parent=self.parent,
            guess=self.guess,
            score=self.score,
            count=self.count,
        )

    cpdef int total_parents(self):
        if self.parent is None:
            return 0
        else:
            return 1 + self.parent.total_parents()

    cpdef int total_count(self):
        if self.parent is None:
            return self.count
        else:
            return self.count + self.parent.total_count()

    cdef list list_parents(self):
        if self.parent is None:
            return [self]
        else:
            return [self] + self.parent.list_parents()

    cpdef object root(self, int round = 0):
        cdef parents = sorted(self.list_parents())
        
        if self.parent is None:
            return self
        else:
            return parents[round]

    cpdef cnp.ndarray filter_words(self, cnp.ndarray[:] answers):
        cdef cnp.ndarray word_filter = fortran_wordle.score_guesses(
                [self.guess], answers
            ).squeeze() == self.score
        cdef cnp.ndarray possible_solutions = answers[word_filter]

        return possible_solutions
