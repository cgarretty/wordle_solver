
build-python:
	@pipenv install

build-fortran:
	@pipenv run python -m numpy.f2py -c -m domain.fortran_wordle fortran/*.f90

build:
	@make build-python
	@make build-fortran

test:
	@pipenv run pytest

run-cli-game:
	@pipenv run python -m cli play-random

find-best-guess:
	@pipenv run python -m cli wordle-solver