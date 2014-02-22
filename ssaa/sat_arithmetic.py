# -*- coding: utf-8 -*-
from ssaa.propositional_logic import Symbol, Xor, Iff, And, UnassignedSymbol


class ArithmeticExpression(object):
    childs = None
    _formula = None

    def get_propositional_formula(self):
        exprs = set()
        queue = [self]
        while queue:
            current = queue.pop()
            if current not in exprs:
                exprs.add(current)
                for child in current.childs:
                    queue.append(child)
        exprs = list(exprs)
        formulas = [expr._get_formula() for expr in exprs]
        formulas = [formula for formula in formulas if formula is not None]
        return And(*formulas)

    def _get_formula(self):
        return self._formula

    def build_assignment(self, x):
        raise NotImplementedError()

    def recover_value(self, assignment):
        raise NotImplementedError()

    def make_constant(self, value):
        raise NotImplementedError()


class IntegerExpression(ArithmeticExpression):
    pass


class BooleanExpression(ArithmeticExpression):
    def build_assignment(self, x):
        if x not in (True, False):
            raise ValueError("Can only assign boolean values to a "
                             "BooleanExpression")
        return {self.bit: x}

    def recover_value(self, assignment):
        try:
            return assignment[self.bit]
        except KeyError:
            raise UnassignedSymbol(self.bit)

    def make_constant(self, value):
        if value not in (True, False):
            raise ValueError("Can only assign boolean values to a "
                             "BooleanExpression", value)
        formula = self.bit
        if not value:
            formula = -self.bit
        if self._formula is None:
            self._formula = formula
        else:
            self._formula &= formula


class Integer(IntegerExpression):
    def __init__(self, bits):
        self.childs = []
        if isinstance(bits, int):
            self.bits = [Symbol() for _ in xrange(bits)]
        else:
            self.bits = bits

    def build_assignment(self, x):
        if not isinstance(x, (int, long)):
            raise ValueError("Can only assing integer to Integer")
        if x >= 2 ** len(self.bits):
            raise ValueError("Cannot represent {} with {} bits".format(x,
                                                               len(self.bits)))
        a = {}
        for i, bit in enumerate(self.bits):
            a[bit] = bool(x & (1 << i))
        return a

    def recover_value(self, assignment):
        x = 0
        for i, bit in enumerate(self.bits):
            try:
                if assignment[bit]:
                    x += 1 << i
            except KeyError:
                raise UnassignedSymbol(bit)
        return x

    def make_constant(self, value):
        assignment = self.build_assignment(value)
        xs = []
        for bit in self.bits:
            if assignment[bit]:
                xs.append(bit)
            else:
                xs.append(-bit)
        if self._formula is None:
            self._formula = And(*xs)
        else:
            self._formula &= And(*xs)

    def __add__(self, other):
        other = self._convert(other)
        return Sum(self, other)

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        return Substraction(self, other)

    def __mul__(self, other):
        return Multiplication(self, other)

    def __div__(self, other):
        return Divition(self, other)

    def __mod__(self, other):  # TODO: Test
        if isinstance(other, int) and other == 2 ** len(self.bits):
            return self
        return Modulo(self, other)

    def __xor__(self, other):
        other = self._convert(other)
        return BitwiseXor(self, other)

    def __rxor__(self, other):
        return self ^ other

    def __and__(self, other):
        other = self._convert(other)
        return BitwiseAnd(self, other)

    def __or__(self, other):
        other = self._convert(other)
        return BitwiseOr(self, other)

    def __eq__(self, other):
        return EqualIntegers(self, other)

    def __lt__(self, other):
        return LessThan(self, other)

    def __gt__(self, other):
        return GreaterThan(self, other)

    def __le__(self, other):
        return LessOrEqualThan(self, other)

    def __ge__(self, other):
        return GreaterOrEqualThan(self, other)

    def _convert(self, x):  # TODO: Test
        if not isinstance(x, (int, IntegerExpression)):
            raise TypeError("Cannot operate with {}".format(x))
        if isinstance(x, int):
            x = x % (2 ** len(self.bits))
            y = Integer(len(self.bits))
            y.make_constant(x)
            x = y
        return x


class Shift(Integer):  # TODO: Rename to rotate left
    def __init__(self, integer, places):
        bits = integer.bits
        if places >= len(bits):
            raise ValueError("Can only shift up to {} bits".format(len(bits)))
        self.bits = bits[-places:] + bits[:-places]
        self.childs = [integer]


class Sum(Integer):
    def __init__(self, a, b):
        self.childs = [a, b]
        self.bits = [Symbol() for _ in a.bits]
        formula, _, _, _, _ = integer_sum(a, b, self)
        self._formula = formula


class Substraction(Integer):
    def __init__(self, a, b):
        self.childs = [a, b]
        self.bits = [Symbol() for _ in a.bits]
        formula, _, _, _, _ = integer_sum(self, b, a)
        self._formula = formula


class Multiplication(Integer):
    def __init__(self, a, b):
        self.childs = [a, b]
        self.bits = [Symbol() for _ in a.bits]
        formula, _, _, _ = integer_mul(a, b, self)
        self._formula = formula


class Divition(Integer):
    def __init__(self, x, d):
        """
        x = self * d + r

        b = self * d
        x = b + r
        """
        self.bits = [Symbol() for _ in x.bits]
        f1, _, _, b = integer_mul(self, d, zero_carry=True)
        f2, r, _, _, _ = integer_sum(b=b, c=x)
        f3, _, _, _, carry = integer_sum(b=d, c=r)  # Less than
        self.childs = [x, b, d, r]
        self._formula = f1 & f2 & f3 & carry


class Modulo(Integer):
    def __init__(self, x, d):
        """
        x = d * c + self

        b = d * c
        x = b + r
        """
        self.bits = [Symbol() for _ in x.bits]
        f1, _, c, b = integer_mul(d, zero_carry=True)
        f2, _, _, _, _ = integer_sum(self, b, x)
        f3, _, _, _, carry = integer_sum(b=d, c=self)  # Less than
        self.childs = [x, b, d, c]
        self._formula = f1 & f2 & f3 & carry


class BitwiseOperator(Integer):  # TODO: Test
    def __init__(self, a, b):
        self.childs = [a, b]
        self.bits = [Symbol() for _ in a.bits]
        formulas = []
        for bita, bitb, bitc in zip(a.bits, b.bits, self.bits):
            formulas.append(Iff(bitc, self.operator(bita, bitb)))
        self._formula = And(*formulas)


class BitwiseXor(BitwiseOperator):  # TODO: test
    operator = lambda self, a, b: Xor(a, b)


class BitwiseAnd(BitwiseOperator):  # TODO: test
    operator = lambda self, a, b: a & b


class BitwiseOr(BitwiseOperator):  # TODO: test
    operator = lambda self, a, b: a | b


class EqualIntegers(BooleanExpression):
    def __init__(self, a, b):
        if len(a.bits) != len(b.bits):
            raise ValueError("Can only compare numbers of equal amount "
                             "of bits")
        self.childs = [a, b]
        formulas = []
        for bita, bitb in zip(a.bits, b.bits):
            formulas.append(Iff(bita, bitb))
        self.bit = Symbol()
        self._formula = Iff(self.bit, And(*formulas))


class LessThan(BooleanExpression):
    def __init__(self, a, b):
        self.childs = [a, b]
        formula, _, _, _, carry = integer_sum(b=b, c=a)
        self.bit = carry
        self._formula = formula


class LessOrEqualThan(BooleanExpression):
    def __init__(self, a, b):
        gt = GreaterThan(a, b)
        self.childs = [gt]
        self.bit = Symbol()
        self._formula = Iff(self.bit, -gt.bit)


class GreaterThan(BooleanExpression):
    def __init__(self, a, b):
        self.childs = [a, b]
        formula, _, _, _, carry = integer_sum(b=a, c=b)
        self.bit = carry
        self._formula = formula


class GreaterOrEqualThan(BooleanExpression):
    def __init__(self, a, b):
        lt = LessThan(a, b)
        self.childs = [lt]
        self.bit = Symbol()
        self._formula = Iff(self.bit, -lt.bit)


def bit_sum(a, b, result, c=None):
    if not isinstance(a, Symbol) or not isinstance(b, Symbol) or \
            (result is not None and not isinstance(result, Symbol)) or \
            (c is not None and not isinstance(c, Symbol)):
        raise ValueError("Arguments to bit_sum are expected to be Symbols")
    carry = Symbol()
    if c is None:
        formula = Iff(result, Xor(a, b)) & Iff(carry, a & b)
    else:
        formula = Iff(result, Xor(a, Xor(b, c))) & \
                  Iff(carry, (a & c) | (b & c) | (a & b))
    return formula, carry


def _comfortable_input(a=None, b=None, c=None, bits=None):
    if a is None and b is None and c is None and bits is None:
        raise ValueError("Need amount of bits for sum")
    if bits is not None and not isinstance(bits, int):
        raise ValueError("Bits expected to be integer")
    xs = [len(x.bits) for x in [a, b, c] if x is not None]
    if xs:
        if max(xs) != min(xs):
            raise ValueError("Can only add numbers of equal amount of bits")
        bits = xs[0]
    if a is None:
        a = Integer(bits)
    if b is None:
        b = Integer(bits)
    if c is None:
        c = Integer(bits)
    return a, b, c


def integer_sum(a=None, b=None, c=None, bits=None):
    a, b, c = _comfortable_input(a, b, c, bits)
    formulas = []
    carry = None
    for bita, bitb, bitc in zip(a.bits, b.bits, c.bits):
        formula, carry = bit_sum(bita, bitb, bitc, carry)
        formulas.append(formula)
    return And(*formulas), a, b, c, carry


def integer_mul(a=None, b=None, c=None, bits=None, zero_carry=False):
    a, b, c = _comfortable_input(a, b, c, bits)
    if len(a.bits) == 1:
        return Iff(c.bits[0], a.bits[0] & b.bits[0]), a, b, c
    formulas = []
    partials = []
    for i in xrange(len(a.bits)):
        bbit = b.bits[i]
        newbits = []
        for abit in a.bits:
            newbit = Symbol()
            newbits.append(newbit)
            formulas.append(Iff(newbit, abit & bbit))
        U = _mul_upgrade(newbits, i)
        partials.append(U)
    total = partials[0]
    for partial in partials[1:]:
        total += partial
    for cbit, tbit in zip(c.bits, total.bits):
        formulas.append(Iff(cbit, tbit))
    if zero_carry:
        for tbit in total.bits[len(c.bits):]:
            formulas.append(-tbit)
    return And(*formulas) & total.get_propositional_formula(), a, b, c


def _mul_upgrade(bits, shift):
    zero = Integer(len(bits))
    zero.make_constant(0)
    upgraded = Integer(bits + zero.bits)
    upgraded.childs.append(zero)
    upgraded = Shift(upgraded, shift)
    assert len(upgraded.bits) == 2 * len(bits)
    return upgraded
