import unittest
from ssaa.solver import simplify_clauses


class TestUnitPropagateClauses(unittest.TestCase):
    def test_simple_clauses(self):
        clauses = [[1]]
        simple, assign, free = simplify_clauses(clauses)
        self.assertEqual(simple, [])
        self.assertEqual(assign, set([1]))
        self.assertEqual(free, set())
        clauses = [[1],
                   [-1, 2],
                   [-2, 3]]
        simple, assign, free = simplify_clauses(clauses)
        self.assertEqual(simple, [])
        self.assertEqual(assign, set([1, 2, 3]))
        self.assertEqual(free, set())
        clauses = [[1, 2, -4],
                   [-1, 2, 4],
                   [-2, 3, 4]]
        simple, assign, free = simplify_clauses(clauses)
        self.assertEqual(simple, [])
        self.assertEqual(assign, set([3, 2]))
        self.assertEqual(free, set([4, 1]))

    def test_cannot_go_on(self):
        clauses = [[1],
                   [-4, 2, -1, -3],
                   [-2, 3, 4]]
        simple, assign, free = simplify_clauses(clauses)
        self._same_clauses(simple, [[-4, 2, -3], [-2, 3, 4]])
        self.assertEqual(assign, set([1]))
        self.assertEqual(free, set())

    def test_unsat(self):
        clauses = [[1],
                   [-1, -2],
                   [2, -1]]
        simple, assign, free = simplify_clauses(clauses)
        self.assertIn([], simple)
        self.assertTrue(assign == set([1, 2]) or assign == set([1, -2]))
        self.assertEqual(free, set())

    def test_tautology(self):
        clauses = [[1, -1]]
        simple, assign, free = simplify_clauses(clauses)
        self.assertEqual(simple, [])
        self.assertEqual(assign, set())
        self.assertEqual(free, set([1]))


    def _same_clauses(self, a, b):
        a = sorted(set(x) for x in a)
        b = sorted(set(x) for x in b)
        self.assertEqual(a, b)

if __name__ == "__main__":
    unittest.main()
