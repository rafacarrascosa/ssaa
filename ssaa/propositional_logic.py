# -*- coding: utf-8 -*-
import itertools


class UnassignedSymbol(Exception):
    pass


class Formula(object):
    def evaluate(self, assignment):
        pass

    def __add__(self, other):
        a = self
        b = other
        if isinstance(b, Or):
            a, b = b, a
        if isinstance(a, Or):
            args = [b]
            if isinstance(b, Or):
                args = b.args
            return Or(*(a.args + args))
        else:
            return Or(a, b)

    def __and__(self, other):
        return And(self, other)

    def __or__(self, other):
        return Or(self, other)

    def __neg__(self):
        return Not(self)

    def to_cnf(self):
        return to_cnf(self)

    def to_clauses(self):
        return to_clauses(self)


class Symbol(Formula):
    def evaluate(self, assignment):
        if self not in assignment:
            raise UnassignedSymbol(self)
        v = assignment[self]
        assert v is True or v is False
        return v


class And(Formula):
    def __init__(self, *args):
        if not args:
            raise ValueError("Empty range And not allowed.")
        xs = []
        for x in args:
            if isinstance(x, And):
                xs.extend(x.args)
            else:
                xs.append(x)
        self.args = xs

    def evaluate(self, assignment):
        return all([x.evaluate(assignment) for x in self.args])


class Or(Formula):
    def __init__(self, *args):
        if not args:
            raise ValueError("Empty range Or not allowed.")
        xs = []
        for x in args:
            if isinstance(x, Or):
                xs.extend(x.args)
            else:
                xs.append(x)
        self.args = xs

    def evaluate(self, assignment):
        return any([x.evaluate(assignment) for x in self.args])


class Not(Formula):
    def __init__(self, expr):
        self.args = [expr]

    def evaluate(self, assignment):
        return not self.args[0].evaluate(assignment)


class Implies(Formula):
    def __init__(self, a, b):
        self.args = [a, b]

    def evaluate(self, assignment):
        P, Q = self.args
        a = P.evaluate(assignment)
        b = Q.evaluate(assignment)
        return (not a) or b


class Iff(Formula):
    def __init__(self, a, b):
        self.args = [a, b]

    def evaluate(self, assignment):
        P, Q = self.args
        a = P.evaluate(assignment)
        b = Q.evaluate(assignment)
        return a is b


class Xor(Formula):
    def __init__(self, a, b):
        self.args = [a, b]

    def evaluate(self, assignment):
        P, Q = self.args
        a = P.evaluate(assignment)
        b = Q.evaluate(assignment)
        return (a and (not b)) or (b and (not a))


def is_atomic(formula):
    if not isinstance(formula, Formula):
        raise ValueError("argument must be a Formula")
    return isinstance(formula, Symbol) or\
         (isinstance(formula, Not) and isinstance(formula.args[0], Symbol))


def is_simple_disjunction(formula):
    if is_atomic(formula):
        return True
    if not isinstance(formula, Or):
        return False
    if isinstance(formula, Or):
        for symbol in formula.args:
            if not is_atomic(symbol):
                return False
    return True


def is_cnf(formula):
    if is_atomic(formula) or is_simple_disjunction(formula):
        return True
    if not isinstance(formula, And):
        return False
    for disjunction in formula.args:
        if not is_simple_disjunction(disjunction):
            return False
    return True


def post_order_depth_first(formula):
    """
    Iterate over the subformulas of the formula (is a tree) in a way such that
    every subformula is preceded by it's childs.
    """
    q = [formula]
    i = 0
    while i != len(q):
        node = q[i]
        i += 1
        if isinstance(node, Symbol):
            continue
        for other in node.args:
            q.append(other)
    q.reverse()
    return q


def iter_symbols(formula):
    for sub in post_order_depth_first(formula):
        if isinstance(sub, Symbol):
            yield sub


def symbols_of(formula):
    return set(iter_symbols(formula))


def pformula(formula, var=None):
    if var is None:
        var = {}
    if formula in var:
        return var[formula]
    if isinstance(formula, Symbol):
        ret = u"p{}".format(len(var))
        var[formula] = ret
        return ret
    if isinstance(formula, Not):
        return u"¬{}".format(pformula(formula.args[0], var))
    if isinstance(formula, And):
        sep = u" and "
    if isinstance(formula, Or):
        sep = u" or "
    if isinstance(formula, Implies):
        sep = u" => "
    if isinstance(formula, Iff):
        sep = u" <=> "
    if isinstance(formula, Xor):
        sep = u" ° "
    return "(" + sep.join(pformula(x, var) for x in formula.args) + ")"


def rformula(formula, var=None):
    if var is None:
        var = {}
    if formula in var:
        return var[formula]
    if isinstance(formula, Symbol):
        ret = u"p{}".format(len(var))
        var[formula] = ret
        return ret
    if isinstance(formula, Not):
        return u"¬{}".format(rformula(formula.args[0], var))
    return formula.__class__.__name__ + \
           "(" + ", ".join(rformula(x, var) for x in formula.args) + ")"


def remove_sugar(formula):
    """
    Make an equivalente formula made of And, Or, Not and Symbol.
    """
    if isinstance(formula, Symbol):
        return formula
    if isinstance(formula, Not):
        return -remove_sugar(formula.args[0])
    if len(formula.args) == 1:
        return remove_sugar(formula.args[0])
    if isinstance(formula, And):
        return And(*[remove_sugar(x) for x in formula.args])
    if isinstance(formula, Or):
        return Or(*[remove_sugar(x) for x in formula.args])
    if isinstance(formula, Implies):
        P, Q = formula.args
        return remove_sugar(-P | Q)
    if isinstance(formula, Iff):
        P, Q = formula.args
        return remove_sugar((-P | Q) & (-Q | P))
    if isinstance(formula, Xor):
        P, Q = formula.args
        return remove_sugar((-P & Q) | (-Q & P))
    assert False


def apply_demorgan(formula):
    if is_atomic(formula):
        return formula
    if isinstance(formula, Not):
        sub = formula.args[0]
        if isinstance(sub, Not):
            return apply_demorgan(sub.args[0])
        if isinstance(sub, And):
            return apply_demorgan(Or(*[-x for x in sub.args]))
        if isinstance(sub, Or):
            return apply_demorgan(And(*[-x for x in sub.args]))
        assert False
    if isinstance(formula, And):
        return And(*[apply_demorgan(x) for x in formula.args])
    if isinstance(formula, Or):
        return Or(*[apply_demorgan(x) for x in formula.args])
    raise ValueError("apply_demorgan requieres all instances of {} to be "
             "previously removed using remove_sugar".format(formula.__class__))


def to_negative_normal_form(formula):
    formula = remove_sugar(formula)
    formula = apply_demorgan(formula)
    return formula


def is_negative_normal_form(formula):
    for x in post_order_depth_first(formula):
        if not isinstance(x, (And, Or, Not, Symbol)):
            return False
        if isinstance(x, Not) and not isinstance(x.args[0], Symbol):
            return False
    return True


def _polynomial_cnf_distribute_or(formula):
    """
    This version of distribute generates (at worse) a formula that is
    polynomially larger than the input. As a side effect it introduces dummy
    variables into the formula.
    Input and output are not equivalent but equi-satisfasible.
    """
    assert isinstance(formula, Or)
    ands = []
    rest = []
    for x in formula.args:
        assert not isinstance(x, Or)
        if isinstance(x, And):
            ands.append(cnf_distribute_and(x))
        else:
            rest.append(x)
    if not ands:
        return formula
    Zs = [Symbol() for _ in ands]
    rest.extend(Zs)
    result = Or(*rest)
    for Z, and_ in zip(Zs, ands):
        for value in and_.args:
            result &= -Z | value
    return result


def _exponential_cnf_distribute_or(formula):
    """
    This version of distribute generates (at worse) a formula that is
    exponentially larger than the input. Input and output are equivalent.
    """
    assert isinstance(formula, Or)
    ands = []
    rest = []
    for x in formula.args:
        assert not isinstance(x, Or)
        if isinstance(x, And):
            ands.append(cnf_distribute_and(x))
        else:
            rest.append(x)
    if not ands:
        return formula
    ys = []
    if rest:
        ands.append(And(Or(*rest)))
    for xs in itertools.product(*[x.args for x in ands]):
        ys.append(Or(*xs))
    return And(*ys)


def cnf_distribute_or(formula):
    return _exponential_cnf_distribute_or(formula)


def cnf_distribute_and(formula):
    assert isinstance(formula, And)
    xs = []
    for x in formula.args:
        if isinstance(x, Or):
            xs.append(cnf_distribute_or(x))
        else:
            xs.append(x)
    return And(*xs)


def to_cnf(formula):
    nnf = to_negative_normal_form(formula)
    if is_atomic(nnf):
        return nnf
    if isinstance(nnf, And):
        return cnf_distribute_and(nnf)
    elif isinstance(nnf, Or):
        return cnf_distribute_or(nnf)
    else:
        return formula


def upgrade_cnf_formula(formula):
    if not is_cnf(formula):
        raise ValueError("Expecting a formula in cnf")
    if is_atomic(formula):
        return And(Or(formula))
    elif is_simple_disjunction(formula):
        return And(formula)
    return formula


def upgrade_simple_disjunction(formula):
    if is_atomic(formula):
        return Or(formula)
    return formula


def iter_clauses(formula):
    formula = upgrade_cnf_formula(formula)
    for clause in formula.args:
        clause = upgrade_simple_disjunction(clause)
        yield clause.args


def is_horn(formula):
    for clause in iter_clauses(formula):
        positive = sum(1 for literal in clause if isinstance(literal, Symbol))
        if positive > 1:
            return False
    return True


def to_clauses(formula):  # TODO: Test
    if not is_cnf(formula):
        raise ValueError("Formula has to be in CNF")
    names = {}
    reverse = [None]
    clauses = []
    for atoms in iter_clauses(formula.to_cnf()):
        clause = []
        for atom in atoms:
            polarity = 1
            if not isinstance(atom, Symbol):
                atom = atom.args[0]
                polarity = -1
            if atom not in names:
                name = len(reverse)
                names[atom] = name
                reverse.append(atom)
            else:
                name = names[atom]
            clause.append(polarity * name)
        clauses.append(clause)
    return clauses, names, reverse
