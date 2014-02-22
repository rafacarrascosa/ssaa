# -*- coding: utf-8 -*-
import unittest
import random
from ssaa.sat_arithmetic import Integer
from ssaa.solver import solve
from ssaa.propositional_logic import pformula


class OperatorBruteForceMixin(object):
    topN=32
    def test_random_operator(self):
        operator = self.operator
        random.seed("Tara ra ra ta")
        for _ in xrange(100):
            N = random.randint(2, self.topN)
            M = 2 ** N
            a = Integer(N)
            b = Integer(N)
            c = operator(a, b)
            va = random.randint(0, M - 1)
            vb = random.randint(0, M - 1)
            try:
                vc = operator(va, vb) % M
            except ZeroDivisionError:
                continue
            assign = {}
            assign.update(a.build_assignment(va))
            assign.update(b.build_assignment(vb))
            assign.update(c.build_assignment(vc))
            formula = c.get_propositional_formula()
            self.assertNotEqual(solve(formula, assign), None,
                      "Model is UNSAT for a={} b={} c={}\n".format(va, vb, vc))
            a.make_constant(va)
            b.make_constant(vb)
            c.make_constant(vc)
            formula = c.get_propositional_formula()
            self.assertNotEqual(solve(formula), None)


class IntegerOperatorBruteForceMixin(OperatorBruteForceMixin):
    def test_random_wrong_operator(self):
        operator = self.operator
        random.seed("Tara ra ra ta ta ra ra ra ta")
        N = 5
        M = 2 ** N
        for _ in xrange(10):
            a = Integer(N)
            b = Integer(N)
            c = operator(a, b)
            va = random.randint(0, M - 1)
            vb = random.randint(0, M - 1)
            try:
                correct = operator(va, vb) % M
            except ZeroDivisionError:
                continue
            a.make_constant(va)
            b.make_constant(vb)
    
            for vc in xrange(M):
                if vc == correct:
                    continue
                c.make_constant(vc)
                formula = c.get_propositional_formula()
                model = solve(formula)
                self.assertEqual(model, None,
                        "Model is SAT for a={} b={} c={}\n".format(va, vb, vc))

    def test_random_operator_with_constant(self):
        operator = self.operator
        random.seed("Feels like I only go backwards")
        for _ in xrange(100):
            N = random.randint(2, self.topN)
            M = 2 ** N
            a = Integer(N)
            b = random.randint(0, M - 1)
            c = operator(a, b)
            va = random.randint(0, M - 1)
            try:
                vc = operator(va, b) % M
            except ZeroDivisionError:
                continue
            assign = {}
            assign.update(a.build_assignment(va))
            assign.update(c.build_assignment(vc))
            formula = c.get_propositional_formula()
            self.assertNotEqual(solve(formula, assign), None,
                      "Model is UNSAT for a={} b={} c={}\n".format(va, b, vc))


class TestSum(unittest.TestCase, IntegerOperatorBruteForceMixin):
    def operator(self, a, b):
        return a + b


class TestMul(unittest.TestCase, IntegerOperatorBruteForceMixin):
    topN=10
    def operator(self, a, b):
        return a * b

    def test_random_operator_with_constant(self):
        pass


class TestSub(unittest.TestCase, IntegerOperatorBruteForceMixin):
    def operator(self, a, b):
        return a - b

    def test_random_operator_with_constant(self):
        pass


class TestDiv(unittest.TestCase, IntegerOperatorBruteForceMixin):
    topN=10
    def operator(self, a, b):
        return a / b

    def test_random_operator_with_constant(self):
        pass


class TestMod(unittest.TestCase, IntegerOperatorBruteForceMixin):
    topN=10
    def operator(self, a, b):
        return a % b

    def test_random_operator_with_constant(self):
        pass


class TestXor(unittest.TestCase, IntegerOperatorBruteForceMixin):
    def operator(self, a, b):
        return a ^ b


class TestAnd(unittest.TestCase, IntegerOperatorBruteForceMixin):
    def operator(self, a, b):
        return a & b


class TestOr(unittest.TestCase, IntegerOperatorBruteForceMixin):
    def operator(self, a, b):
        return a | b


class TestLt(unittest.TestCase, OperatorBruteForceMixin):
    def operator(self, a, b):
        return a < b


class TestGt(unittest.TestCase, OperatorBruteForceMixin):
    def operator(self, a, b):
        return a > b


class TestGeq(unittest.TestCase, OperatorBruteForceMixin):
    def operator(self, a, b):
        return a >= b


class TestLeq(unittest.TestCase, OperatorBruteForceMixin):
    def operator(self, a, b):
        return a <= b


class TestRSum(unittest.TestCase, IntegerOperatorBruteForceMixin):
    def operator(self, a, b):
        return b + a


class TestRXor(unittest.TestCase, IntegerOperatorBruteForceMixin):
    def operator(self, a, b):
        return b ^ a


if __name__ == "__main__":
    unittest.main()
