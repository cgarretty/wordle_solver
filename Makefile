build-rust:
	cd rust && maturin develop --release

build-fortran:
	@pipenv run python -m numpy.f2py -c -m wordle fortran/*.f90