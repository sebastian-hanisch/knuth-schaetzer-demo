"""Einheiten des Rechenkerns, jede an einer von Hand gerechneten Mini-Instanz."""

import random
from fractions import Fraction

import numpy as np
import pytest

import ksc_algorithm as A


class Scripted:
    """Zufallsquelle mit vorgegebenen Antworten für randrange (nach Modulo n)."""

    def __init__(self, values):
        self.values = list(values)

    def randrange(self, n):
        return self.values.pop(0) % n


def test_parse_tree_and_exact_size_on_the_hand_tree(hand_tree, complete_tree):
    ch, root, n = A.parse_tree(hand_tree["text"])
    assert n == hand_tree["nodes"] and A.exact_size(ch, root) == 7 and len(ch(root)) == 2 and [len(ch(k)) for k in ch(root)] == [3, 1]
    ch2, root2, n2 = A.parse_tree(complete_tree["text"])
    assert n2 == 7 and A.exact_size(ch2, root2) == 7


def test_exact_distribution_of_the_estimator(hand_tree):
    ch, root, _ = A.parse_tree(hand_tree["text"])
    dist = A.enumerate_probes(ch, root)
    assert len(dist) == hand_tree["leaves"] and sum(p for p, _, _ in dist) == 1
    totals = {}
    for p, size, _ in dist:
        totals[size] = totals.get(size, 0) + p
    assert totals == {9: Fraction(1, 2), 5: Fraction(1, 2)}
    assert A.estimator_moments(dist) == (7, 4)
    assert sorted(w for _, _, w in dist) == [2, 6, 6, 6]


def test_scripted_probes_follow_the_hand_computation(hand_tree):
    ch, root, _ = A.parse_tree(hand_tree["text"])
    assert A.knuth_probe(ch, root, Scripted([0, 0]))[:2] == (9, 6) and A.knuth_probe(ch, root, Scripted([1, 0]))[:2] == (5, 2)
    assert A.knuth_probe(ch, root, Scripted([0, 2]))[3] == 3      # besuchte Knoten: Wurzel, Kind, Blatt


def test_complete_tree_has_zero_variance(complete_tree):
    ch, root, _ = A.parse_tree(complete_tree["text"])
    assert A.estimator_moments(A.enumerate_probes(ch, root)) == (7, 0)
    rng = random.Random(1)
    assert {A.knuth_probe(ch, root, rng)[0] for _ in range(50)} == {7}


def test_tiny_trees():
    for text, n, var in (("()", 1, 0), ("(())", 2, 0), ("((()))", 3, 0), ("(()())", 3, 0)):
        ch, root, size = A.parse_tree(text)
        assert size == n and A.estimator_moments(A.enumerate_probes(ch, root)) == (n, var)


def test_parse_tree_errors_are_german():
    for text, part in (("", "leer"), ("(a)", "runde Klammern"), ("()()", "mehr als eine Wurzel"), ("())", "schließende Klammern"), ("(()", "fehlen"), ("(" * 40 + ")" * 40, "Tiefe"), ("(" + "()" * 300 + ")", "Höchstens 300")):
        with pytest.raises(ValueError, match=part):
            A.parse_tree(text)


def test_queens_by_hand_and_known_counts():
    ch = A.queens_children(4)
    assert [A.exact_size(A.queens_children(n), ()) for n in (1, 2, 3)] == [2, 3, 6]
    assert A.queens_solutions(4) == 2 and A.exact_leaf_count(ch, (), lambda c: len(c) == 4) == 2
    assert [A.queens_solutions(n) for n in (1, 2, 3, 5, 6, 8)] == [1, 0, 0, 10, 4, 92]


def test_grid_paths_by_brute_force_and_distribution():
    assert [A.paths_brute(n) for n in (2, 3, 4, 5)] == [2, 12, 184, 8512]
    for check in (False, True):
        for n, truth in ((2, 2), (3, 12), (4, 184)):
            dist = A.path_distribution(n, check)
            assert sum(p for p, _ in dist) == 1 and sum(p * w for p, w in dist) == truth, (n, check)
    assert all(w > 0 for _, w in A.path_distribution(4, True)) and any(w == 0 for _, w in A.path_distribution(4, False))
    assert {w for _, w in A.path_distribution(2, False)} == {2}


def test_path_probe_by_hand():
    rng = Scripted([0, 0, 0, 0])
    assert A.path_probe(2, rng, False) == (2, 2)
    with pytest.raises(ValueError):
        A.path_probe(1, random.Random(1), False)
    with pytest.raises(ValueError):
        A.path_distribution(5, False)
    with pytest.raises(ValueError):
        A.paths_brute(6)


def test_reachability_helper():
    nb = A.grid_neighbor_lists(3)
    assert A.path_reachable(nb, 0, 8, 0) and not A.path_reachable(nb, 0, 8, 1 << 1 | 1 << 3) and A.path_reachable(nb, 8, 8, 0)
    assert sorted(nb[4]) == [1, 3, 5, 7] and sorted(nb[0]) == [1, 3]


def test_knapsack_by_hand_and_brute_force():
    items = [(10, 5), (6, 4), (6, 4)]
    assert A.knapsack_opt(items, 8) == 12 and A.knapsack_opt(items, 9) == 16 and A.knapsack_brute(items, 9) == 16
    assert A.fractional_bound(items, 8, 0, 0, 0) == 10 + 6 * 3 / 4
    inst, cap = A.knapsack_instance(10, 5, True)
    assert A.knapsack_opt(inst, cap) == A.knapsack_brute(inst, cap) and all(v == w + 10 for v, w in inst) and cap == sum(w for _, w in inst) // 2
    ratios = [v / w for v, w in inst]
    assert ratios == sorted(ratios, reverse=True)


def test_knapsack_tree_by_hand():
    items = [(10, 5), (6, 4), (6, 4)]
    ch = A.knapsack_children(items, 9, 16)
    root = (0, 0, 0)
    assert ch(root) == [(1, 10, 5)]      # Weglassen von Gegenstand 0 gibt höchstens 12 < 16
    # Wurzel; Gegenstand 0 nehmen: (1,10,5) mit zwei Kindern: Gegenstand 1 nehmen (16, Gewicht 9, danach nur Weglassen von 2: Schranke 16) oder weglassen (10 + 6 = 16 reicht noch, Gegenstand 2 nehmen)
    assert A.exact_size(ch, root) == 6 and [len(ch(k)) for k in ch((1, 10, 5))] == [1, 1]
    with pytest.raises(A.TreeTooLarge):
        A.exact_size(ch, root, limit=2)


def test_chen_by_hand_on_a_tree_whose_types_collide():
    """Baum ((()())(()(()()))): Wurzel mit a (zwei Blätter) und b (ein Blatt und c mit zwei Blättern): 1 + 3 + 5 = 9 Knoten.
    Typ = Zahl der Kinder: a und b haben beide zwei und teilen sich einen Vertreter mit Gewicht 2. Wird a gewählt: 1 + 2 + 4 = 7; wird b gewählt: 1 + 2 + 2 + 2 + 4 = 11. Erwartung (7 + 11)/2 = 9."""
    ch, root, n = A.parse_tree("((()())(()(()())))")
    assert n == 9 and A.exact_size(ch, root) == 9
    runs = [A.chen_probe(ch, root, random.Random(s), depth_of=lambda node: 0)[0] for s in range(2000)]
    assert set(runs) == {7, 11} and abs(sum(runs) / len(runs) - 9) < 0.15
    ch2, root2, _ = A.parse_tree("((()()())(()))")
    assert {A.chen_probe(ch2, root2, random.Random(s), depth_of=lambda node: 0)[0] for s in range(50)} == {7}   # die Typen trennen a und b: kein Zufall übrig


def test_hash_cells_by_hand():
    tilings, n_edges = A.domino_tilings(2, 3)
    assert len(tilings) == 3 and n_edges == 7
    m = A.tiling_matrix(tilings, n_edges)
    assert m.shape == (3, 7) and m.sum() == 9 and all(row.sum() == 3 for row in m)
    c = np.zeros((7, 1), dtype=np.uint8)
    assert A.hash_cell_count(m, c, np.array([0], dtype=np.uint8)) == 3 and A.hash_cell_count(m, c, np.array([1], dtype=np.uint8)) == 0
    assert A.hash_estimate(m, 0, np.random.default_rng(1)) == 3
    assert len(A.domino_tilings(4, 4)[0]) == 36 and len(A.domino_tilings(3, 3)[0]) == 0 and len(A.domino_tilings(2, 8)[0]) == 34


def test_statistics_helpers():
    assert A.mean_cv([2, 4]) == (3, pytest.approx(1 / 3)) and A.mean_cv([0, 0])[1] == float("inf")
    assert A.probes_for_error(2.0, 0.05) == 1600 and A.probes_for_error(0.0, 0.05) == 0
    assert A.block_means([1, 2, 3, 4, 5], 2) == [1.5, 3.5] and A.block_means([1, 2], 5) == []
    assert A.confidence_halfwidth([1, 3]) == pytest.approx(1.96 * (2 ** 0.5) / (2 ** 0.5)) and A.confidence_halfwidth([5]) == float("inf")
    for bad in (lambda: A.probes_for_error(1, 0), lambda: A.probes_for_error(1, 1), lambda: A.block_means([1], 0), lambda: A.queens_children(0), lambda: A.knapsack_instance(0, 1, True), lambda: A.domino_tilings(0, 3)):
        with pytest.raises(ValueError):
            bad()
