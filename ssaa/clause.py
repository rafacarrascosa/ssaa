# -*- coding: utf-8 -*-
import bitarray

from solver import simplify_clauses, pycosat_solve, assignment_to_clauses, \
                   lits_to_assignment
from propositional_logic import UnassignedSymbol


class Claused(object):
    relevant_io = {}

    def __init__(self, formula, relevant_io=None):
        if relevant_io is None:
            relevant_io = {}
        for value in relevant_io.values():
            value.childs = []
        self.relevant_io = relevant_io
        self.clauses, self.names, self.reverse = formula.to_cnf().to_clauses()
        self.clauses, self.partial, self.free = simplify_clauses(self.clauses)
        self.rebuild_assignment()

    def reset_assignment(self):
        self.assignment = lits_to_assignment(self.partial, self.reverse)
        self.assignment.update(lits_to_assignment(self.free, self.reverse))

    def add_assignment(self, a):
        self.assignment.update(a)

    def assign(self, sym, value):
        self.assignment[sym] = value

    def assign_lit(self, lit, value):
        self.assign(self.reverse[lit], value)

    def __setattr__(self, attr, value):
        if attr != "relevant_io" and attr in self.relevant_io:
            update = self.relevant_io[attr].build_assignment(value)
            self.add_assignment(update)
        else:
            super(Claused, self).__setattr__(attr, value)

    def __getattr__(self, attr):
        try:
            return self.relevant_io[attr].recover_value(self.assignment)
        except KeyError:
            raise AttributeError("{!r} object has no attribute {!r}".format(
                                                self.__class__.__name__, attr))

    def simplify(self):
        clauses = self.clauses + \
                  assignment_to_clauses(self.assignment, self.names)
        self.clauses, self.partial, self.free = simplify_clauses(clauses)
        self.reset_assignment()

    def solve(self, solver=pycosat_solve):
        clauses = self.clauses + \
                  assignment_to_clauses(self.assignment, self.names)
        model = solver(clauses)
        if model is None:
            return False
        model = lits_to_assignment(model, self.reverse)
        self.assignment = model
        return True

    def dump(self, fout):
        a = bitarray.bitarray()
        it = iter(self.reverse)
        next(it)  # Drop index 0
        for sym in it:
            try:
                a.append(self.assignment[sym])
            except KeyError:
                raise UnassignedSymbol(sym)
        assert len(a) == len(self.reverse) - 1
        a.tofile(fout)

    def load(self, fin, relevants=None):
        if relevants is not None:
            it = []
            for name in relevants:
                it.extend(self.relevant_io[name].bits)
            relevants = [self.names[x] for x in it]
        else:
            it = iter(self.reverse)
            assert None == next(it)  # Drop index 0
        a = self.read_lits(fin, symbols=relevants)
        assign = {}
        for value, sym in zip(a, it):
            assign[sym] = value
        self.assignment = assign

    def read_lits(self, fin, symbols=None):
        a = bitarray.bitarray()
        N = (len(self.reverse) - 1) / 8
        if ((len(self.reverse) - 1) % 8) != 0:
            N += 1
        a.fromfile(fin, N)
        if symbols is not None:
            a = [a[i - 1] for i in symbols]
        return a

    def dump_lits_assignment(self):
        return dict((self.names[lit], v)
                     for lit, v in self.assignment.iteritems())

    def load_lits_assignment(self, lits_assignment):
        self.assignment = dict((self.reverse[sym], v) for
                                sym, v in lits_assignment.iteritems())
