# wordle_solver

A solver for the internet sensation, [Wordle](https://www.powerlanguage.co.uk/wordle/)! 

Thoughly tested using the super smart advasarial wordle game, [Absurdle](https://qntm.org/files/wordle/index.html).

Absurdle 5/∞

⬜⬜⬜⬜⬜

⬜⬜🟨⬜🟩

⬜⬜⬜⬜⬜

⬜⬜⬜⬜🟩

🟩🟩🟩🟩🟩

### Running locally

__REQUIREMENTS__
 - `gfortran` - fortran compiler (Install [gcc view Homebrew](https://formulae.brew.sh/formula/gcc)).
 - `make`
 - `pipenv` for python depedency management ([Install pipenv](https://pipenv.pypa.io/en/latest/install/))

 1. run `make build` to python and build fortran dependencies
 2. In the root directory of this project, run `pipenv install`
 3. Anytime you want to play Wordle, run `pipenv run python wordle_solver` to start the solver. NOTE: the first run will take a few minutes to load because it is generating all the possible combinations.
