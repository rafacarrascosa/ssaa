# -*- coding: utf-8 -*-
import random
from ssaa.propositional_logic import Symbol, And, Or, Not, Implies, Iff, Xor, \
                                     iter_symbols


def random_formula(depth=6):
    if depth == 0 or random.random() < 0.05:
        return Symbol()
    if random.random() < 0.1:
        return Not(random_formula(depth - 1))
    operator = random.choice([And, Or, Implies, Iff, Xor])
    if operator in (And, Or):
        xs = [random_formula(depth - 1) for _ in xrange(random.randint(1, 5))]
    else:
        xs = [random_formula(depth - 1), random_formula(depth - 1)]
    return operator(*xs)


def random_assignment(formula):
    assignment = {}
    for symbol in iter_symbols(formula):
        assignment[symbol] = random.random() < 0.5
    return assignment
