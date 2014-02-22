# -*- coding: utf-8 -*-
import itertools

import pycosat
from propositional_logic import iter_symbols, to_clauses


def is_theorem(formula, assignment=None):
    return solve(-formula, assignment=assignment) is None


def stupid_sat_solver(formula, prev=None):
    if prev is None:
        prev = {}
    literals = set(iter_symbols(formula))
    free = list(literals - set(prev))
    assignment = {}
    assignment.update(prev)
    for bools in itertools.product((True, False), repeat=len(free)):
        assignment.update(zip(free, bools))
        if formula.evaluate(assignment):
            return assignment
    return None


def iter_vars(clauses):
    for clause in clauses:
        for lit in clause:
            yield abs(lit)


def iter_pure_literals(clauses):  # TODO: Test
    positive = set()
    negative = set()
    for clause in clauses:
        for lit in clause:
            assert isinstance(lit, int)
            if lit > 0:
                positive.add(lit)
            else:
                negative.add(-lit)
    for var in positive - negative:
        yield var
    for var in negative - positive:
        yield -var


def iter_unit_literals(clauses):
    for clause in clauses:
        if len(clause) == 1:
            yield clause[0]


def reduce_clauses_with_assignment(clauses, assignments):  # TODO: Test
    assert isinstance(assignments, set)
    newclauses = []
    for clause in clauses:
        newclause = []
        clause = set(clause)  # Idempotent elimination
        for lit in clause:
            if lit in assignments or -lit in clause:  # Tautology (p or -p)
                newclause = None
                break
            elif -lit not in assignments:
                newclause.append(lit)
        if newclause is not None:
            newclauses.append(newclause)
        elif newclause == []:
            return None
    return newclauses


def _assignment_step(clauses):
    result = set()
    result.update(iter_unit_literals(clauses))
    result.update(iter_pure_literals(clauses))
    return result


def simplify_clauses(clauses):
    original_vars = set(iter_vars(clauses))
    global_assignments = set()
    clauses = reduce_clauses_with_assignment(clauses, global_assignments)
    step_assignments = _assignment_step(clauses)
    while step_assignments:
        for lit in step_assignments:
            if -lit not in global_assignments:
                global_assignments.add(lit)
        clauses = reduce_clauses_with_assignment(clauses, global_assignments)
        if clauses is None:
            clauses = [[]]
            break
        step_assignments = _assignment_step(clauses)
    assigned = set(abs(lit) for lit in global_assignments)
    unassigned = set(iter_vars(clauses))
    free = (original_vars - assigned) - unassigned
    return clauses, global_assignments, free


def to_dimacs(clauses):  # TODO: Test
    maxnames = max(abs(lit) for clause in clauses for lit in clause)
    xs = ["c ssaa", "p cnf {} {}".format(maxnames, len(clauses))]
    for clause in clauses:
        line = " ".join(str(i) for i in clause) + " 0"
        xs.append(line)
    return "\n".join(xs)


def from_dimacs(fin):  # TODO: Test
    for line in fin:
        line = line.split()
        if len(line) == 2 and line[0] == "v":
            lit = int(line[1])
            yield lit


def pycosat_solve(clauses, log=False):
    model = pycosat.solve(clauses, verbose=log)
    if model == "UNSAT":
        return None
    return model


def assignment_to_clauses(assignment, names):
    clauses = []
    for symbol, value in assignment.iteritems():
        lit = names[symbol]
        if not value:
            lit = -lit
        clauses.append([lit])
    return clauses


def lits_to_assignment(lits, reverse):
    assignment = {}
    for code in lits:
        value = True
        if code < 0:
            value = False
            code = -code
        assignment[reverse[code]] = value
    return assignment


def solve(formula, assignment=None, solver=pycosat_solve):
    if assignment is None:
        assignment = {}

    formula = formula.to_cnf()
    clauses, names, reverse = to_clauses(formula)

    clauses += assignment_to_clauses(assignment, names)

    clauses, partial, free = simplify_clauses(clauses)

    if [] in clauses:
        return None
    elif not clauses:
        model = []
    else:
        model = solver(clauses)
    if model is None:
        return None

    assignment = lits_to_assignment(itertools.chain(model, partial, free),
                                    reverse)
    return assignment
