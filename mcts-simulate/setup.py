from setuptools import setup
from Cython.Build import cythonize

setup(
    name='MCTS Cython app',
    ext_modules=cythonize("*.pyx"),
    zip_safe=False,
)
