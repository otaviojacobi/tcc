from setuptools import setup
from Cython.Build import cythonize

setup(
    name='Othello Cython app',
    ext_modules=cythonize("othello_cython.pyx"),
    zip_safe=False,
)