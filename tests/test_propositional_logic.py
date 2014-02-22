# -*- coding: utf-8 -*-
import unittest
import random
from ssaa.random_formula import random_formula, random_assignment
from ssaa.propositional_logic import UnassignedSymbol, to_cnf, is_cnf, \
                                     Symbol, is_atomic, apply_demorgan, \
                                     to_negative_normal_form, remove_sugar, \
                                     is_negative_normal_form
from ssaa.propositional_logic import pformula, rformula, iter_symbols


class TestPropositionalLogic(unittest.TestCase):
    def test_is_atomic(self):
        s = Symbol()
        self.assertTrue(is_atomic(s))
        self.assertTrue(is_atomic(-s))
        self.assertFalse(is_atomic(s | -s))

    def test_evaluation_works(self):
        random.seed("satisfaction 1")
        values = set()
        for depth in xrange(10):
            for _ in xrange(10):
                formula = random_formula(depth)
                a = random_assignment(formula)
                x = formula.evaluate(a)
                values.add(x)
                self.assertIn(x, (True, False))
                symbol = random.choice(list(a))
                del a[symbol]
                self.assertRaises(UnassignedSymbol, formula.evaluate, a)
                if depth == 0:
                    break
        self.assertEqual(len(values), 2)

    def test_cnf_works(self):
        random.seed("satisfaction 2")
        self.brute_t3st_transformation(to_cnf, is_cnf, implies=True)

    def test_nnf_works(self):
        random.seed("satisfaction 3")
        self.brute_t3st_transformation(to_negative_normal_form,
                                       checker=is_negative_normal_form)

    def test_apply_demorgan_works(self):
        random.seed("satisfaction 4")
        adm = lambda x: apply_demorgan(remove_sugar(x))
        self.brute_t3st_transformation(adm)

    def test_remove_sugar_works(self):
        random.seed("satisfaction 5")
        self.brute_t3st_transformation(remove_sugar)

    def brute_t3st_transformation(self, transformer, checker=None,
                                  implies=False):
        for depth in xrange(4):
            for _ in xrange(10):
                formula = random_formula(depth)
                transformed = transformer(formula)
                if checker is not None:
                    self.assertTrue(checker(transformed))
                for _ in xrange(1000):
                    a = random_assignment(transformed)
                    x = formula.evaluate(a)
                    y = transformed.evaluate(a)
                    if implies:
                        self.assertTrue(not y or x)
                    else:
                        self.assertEqual(x, y)
                if depth == 0:
                    break


if __name__ == "__main__":
    unittest.main()
