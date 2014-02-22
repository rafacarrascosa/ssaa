try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name="ssaa",
    version="0.01",
    description="A library to generate propositional formulas that represent",
    long_description=open('README.rst').read(),
    author="Rafael Carrascosa",
    author_email="rafacarrascosa@gmail.com",
    url="https://github.com/rafacarrascosa/ssaa",
    keywords=["propositional logic", "propositional formula", "arithmetic",
              "sat", "propositional", "generator", "formula", "logic",
              "arithmetics",],
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Topic :: Utilities",
        ],
    packages=["ssaa"],
    install_requires=open('requirements.txt').read().split(),
)
