"""Unabhängige Orakel: jede Zahl und jede Erwartung gegen einen zweiten Rechenweg (vollständiges Aufzählen aller Sondierungen, Zählen mit itertools, Rückverfolgung, Brute Force)."""

import itertools
import random
import statistics
from fractions import Fraction

import numpy as np
import pytest

import ksc_algorithm as A


def random_tree_text(rng, max_nodes=40):
    """Zufälliger Baum in Klammerschreibweise mit höchstens `max_nodes` Knoten."""
    budget = [max_nodes - 1]

    def build(depth):
        kids = []
        while budget[0] > 0 and depth < 6 and rng.random() < 0.55:
            budget[0] -= 1
            kids.append(build(depth + 1))
        return "(" + "".join(kids) + ")"

    return build(0)


def queens_prefix_count(n):
    """Zahl der gültigen Teilstellungen (alle Präfixe, Wurzel eingeschlossen) durch Zählen mit itertools, unabhängig von der Rückverfolgung."""
    total = 1
    for r in range(1, n + 1):
        for cols in itertools.product(range(n), repeat=r):
            if all(cols[i] != cols[j] and abs(cols[i] - cols[j]) != j - i for i in range(r) for j in range(i + 1, r)):
                total += 1
    return total


def test_estimator_is_exactly_unbiased_on_random_trees():
    rng = random.Random(11)
    for _ in range(40):
        text = random_tree_text(rng)
        ch, root, n = A.parse_tree(text)
        mean, var = A.estimator_moments(A.enumerate_probes(ch, root))
        assert mean == n and var >= 0, text


def test_variance_is_zero_exactly_for_trees_with_equal_branching_per_level():
    for text in ("(())", "(()())", "((()())(()()))", "(((()())(()()))((()())(()())))"):
        ch, root, n = A.parse_tree(text)
        assert A.estimator_moments(A.enumerate_probes(ch, root))[1] == 0


def test_queens_tree_sizes_against_counting_prefixes_with_itertools():
    for n in range(1, 7):
        assert A.exact_size(A.queens_children(n), ()) == queens_prefix_count(n), n
    assert [A.exact_size(A.queens_children(n), ()) for n in (6, 8, 9, 10)] == [153, 2057, 8394, 35539]


def test_queens_solutions_against_permutations_and_known_values():
    for n in range(1, 8):
        brute = sum(1 for p in itertools.permutations(range(n)) if all(abs(p[i] - p[j]) != j - i for i in range(n) for j in range(i + 1, n)))
        assert A.queens_solutions(n) == brute, n
    assert [A.queens_solutions(n) for n in (8, 9, 10)] == [92, 352, 724]


def test_queens_solution_estimator_is_unbiased_on_small_boards():
    """Erwartung des Lösungsschätzers = Zahl der Lösungen, exakt über alle Sondierungen des Baums (n = 4, 5, 6)."""
    for n in (4, 5, 6):
        ch = A.queens_children(n)
        total = Fraction(0)
        stack = [((), Fraction(1), 1)]
        while stack:
            node, prob, weight = stack.pop()
            kids = ch(node)
            if not kids:
                total += prob * (weight if len(node) == n else 0)
                continue
            for k in kids:
                stack.append((k, prob / len(kids), weight * len(kids)))
        assert total == A.queens_solutions(n), n


def test_path_estimator_is_exactly_unbiased_and_the_check_does_not_change_the_mean():
    truth = {2: 2, 3: 12, 4: 184}
    for n, t in truth.items():
        means = []
        for check in (False, True):
            dist = A.path_distribution(n, check)
            mean = sum(p * w for p, w in dist)
            var = sum(p * (w - mean) ** 2 for p, w in dist)
            means.append((mean, var))
        assert means[0][0] == means[1][0] == t
        assert means[1][1] <= means[0][1], n


def test_paths_against_brute_force_and_stueck_13_constants():
    import ksc_constants as C
    for n in (2, 3, 4, 5):
        assert A.paths_brute(n) == C.KNOWN_PATHS[n]
    assert C.KNOWN_PATHS[6] == 1262816 and C.KNOWN_PATHS[10] == 41044208702632496804


def test_sampled_path_estimates_stay_inside_the_band_on_fixed_seeds():
    import ksc_constants as C
    for n, check, probes in ((5, False, 20000), (5, True, 3000), (6, True, 3000)):
        rng = random.Random(100 + n)
        nb = A.grid_neighbor_lists(n)
        ws = [A.path_probe(n, rng, check, nb)[0] for _ in range(probes)]
        mean, half = statistics.fmean(ws), A.confidence_halfwidth(ws, 3.5)
        assert abs(mean - C.KNOWN_PATHS[n]) <= half, (n, check)


def test_sampled_queens_estimates_stay_inside_the_band_on_fixed_seeds():
    for n in (6, 8):
        ch = A.queens_children(n)
        rng = random.Random(7 + n)
        sizes = [A.knuth_probe(ch, (), rng)[0] for _ in range(5000)]
        assert abs(statistics.fmean(sizes) - A.exact_size(ch, ())) <= A.confidence_halfwidth(sizes, 3.5), n


def test_knapsack_optimum_against_brute_force_on_random_instances():
    for seed in range(8):
        for corr in (False, True):
            items, cap = A.knapsack_instance(12, seed, corr)
            assert A.knapsack_opt(items, cap) == A.knapsack_brute(items, cap), (seed, corr)


def test_knapsack_tree_contains_an_optimal_leaf_and_the_estimator_is_unbiased():
    for seed in range(4):
        items, cap = A.knapsack_instance(9, seed, True)
        opt = A.knapsack_opt(items, cap)
        ch = A.knapsack_children(items, cap, opt)
        size = A.exact_size(ch, (0, 0, 0))
        mean, var = A.estimator_moments(A.enumerate_probes(ch, (0, 0, 0)))
        assert mean == size
        stack, best = [(0, 0, 0)], 0
        while stack:
            node = stack.pop()
            kids = ch(node)
            best = max(best, node[1])
            stack.extend(kids)
        assert best == opt, seed


def test_tilings_against_independent_counts_and_every_tiling_is_valid():
    expected = {(2, 2): 2, (2, 3): 3, (3, 4): 11, (4, 4): 36, (4, 5): 95, (6, 6): 6728, (6, 8): 167089}
    for (r, c), count in expected.items():
        tilings, n_edges = A.domino_tilings(r, c)
        assert len(tilings) == count, (r, c)
    tilings, n_edges = A.domino_tilings(4, 4)
    assert all(len(t) == 8 for t in tilings) and len(set(tilings)) == 36 and n_edges == 24


def test_hash_estimator_is_exactly_unbiased_over_all_constraints_on_a_small_board():
    tilings, n_edges = A.domino_tilings(2, 3)
    matrix = A.tiling_matrix(tilings, n_edges)
    for m in (1, 2):
        total, count = 0, 0
        for cbits in itertools.product((0, 1), repeat=n_edges * m):
            c = np.array(cbits, dtype=np.uint8).reshape(n_edges, m)
            for bbits in itertools.product((0, 1), repeat=m):
                total += A.hash_cell_count(matrix, c, np.array(bbits, dtype=np.uint8)) * 2 ** m
                count += 1
        assert Fraction(total, count) == len(tilings), m


def test_hash_estimates_stay_inside_the_band_on_a_fixed_seed():
    tilings, n_edges = A.domino_tilings(6, 6)
    matrix = A.tiling_matrix(tilings, n_edges)
    rng = np.random.default_rng(5)
    ests = [A.hash_estimate(matrix, 4, rng) for _ in range(300)]
    assert abs(statistics.fmean(ests) - 6728) <= 3.5 * statistics.stdev(ests) / (300 ** 0.5)
