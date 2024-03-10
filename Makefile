
build-python:
	@pipenv install

build-fortran:
	@pipenv run python -m numpy.f2py -c -m domain.fortran_wordle fortran/*.f90

build-cython:
	@pipenv run python setup.py build_ext --inplace

build:
	@make build-python
	@make build-fortran

test:
	@pipenv run pytest

run-cli-game:
	@pipenv run python -m cli play-random

find-best-guess:
	@pipenv run python -m cli wordle-solver

play-reverse-wordle:
	@pipenv run python -m cli reverse-wordle