from setuptools import Extension, setup
from Cython.Build import cythonize
import numpy

extensions = [
    Extension("*", ["domain/*.pyx"], include_dirs=[numpy.get_include()]),
    Extension("wordle", ["domain/wordle.py"], include_dirs=[numpy.get_include()]),
]

setup(ext_modules=cythonize(extensions))
