"""Eigenschaften (Schicht 2): Gesetze, die für alle Bäume und Einstellungen gelten müssen, unabhängig von einzelnen Zahlen."""

import random
import statistics

import numpy as np
import pytest

import ksc_algorithm as A
import ksc_constants as C
import ksc_evaluation as ev
from test_oracle_ksc import random_tree_text


def test_expectation_equals_the_node_count_and_estimates_are_at_least_the_depth_sum():
    rng = random.Random(21)
    for _ in range(30):
        ch, root, n = A.parse_tree(random_tree_text(rng))
        for p, size, weight in A.enumerate_probes(ch, root):
            assert size >= 1 and weight >= 1 and size >= weight
        assert A.estimator_moments(A.enumerate_probes(ch, root))[0] == n


def test_probabilities_of_all_probes_sum_to_one_and_every_leaf_appears_once():
    rng = random.Random(22)
    for _ in range(30):
        ch, root, n = A.parse_tree(random_tree_text(rng))
        dist = A.enumerate_probes(ch, root)
        leaves = sum(1 for node in range(n) if not ch(node))
        assert sum(p for p, _, _ in dist) == 1 and len(dist) == leaves


def test_every_probe_weight_is_the_inverse_of_its_probability():
    rng = random.Random(23)
    for _ in range(20):
        ch, root, _ = A.parse_tree(random_tree_text(rng))
        for p, _, weight in A.enumerate_probes(ch, root):
            assert p * weight == 1


def test_error_of_the_mean_falls_with_the_number_of_probes():
    ch = A.queens_children(8)
    exact = A.exact_size(ch, ())
    rng = random.Random(5)
    pool = [A.knuth_probe(ch, (), rng)[0] for _ in range(20000)]
    med = [statistics.median(abs(m - exact) / exact for m in A.block_means(pool, N)) for N in (10, 100, 1000)]
    assert med[0] > med[1] > med[2] and 2.0 < med[0] / med[1] < 5.0


def test_reachability_check_removes_dead_ends_and_lowers_the_variation_coefficient():
    for n in (4, 5, 6):
        nb = A.grid_neighbor_lists(n)
        rng = random.Random(n)
        plain = [A.path_probe(n, rng, False, nb)[0] for _ in range(6000)]
        checked = [A.path_probe(n, rng, True, nb)[0] for _ in range(600)]
        assert all(w > 0 for w in checked) and any(w == 0 for w in plain) and A.mean_cv(checked)[1] < A.mean_cv(plain)[1]


def test_variation_coefficient_of_the_path_weights_grows_with_the_grid():
    cvs = []
    for n in (4, 6, 8):
        rng = random.Random(40 + n)
        nb = A.grid_neighbor_lists(n)
        cvs.append(A.mean_cv([A.path_probe(n, rng, True, nb)[0] for _ in range(1500)])[1])
    assert cvs == sorted(cvs) and cvs[-1] > 2 * cvs[0]


def test_needed_probes_grow_with_the_square_of_the_variation_coefficient():
    assert A.probes_for_error(2.0, 0.05) == 4 * A.probes_for_error(1.0, 0.05) and A.probes_for_error(1.0, 0.025) == 4 * A.probes_for_error(1.0, 0.05)


def test_block_means_partition_the_sample():
    xs = list(range(1, 101))
    for size in (1, 5, 10, 50, 100):
        blocks = A.block_means(xs, size)
        assert len(blocks) == 100 // size and statistics.fmean(blocks) == statistics.fmean(xs)


def test_hash_variation_coefficient_follows_the_inverse_square_root_of_the_cell_size():
    tilings, n_edges = A.domino_tilings(6, 6)
    matrix = A.tiling_matrix(tilings, n_edges)
    rng = np.random.default_rng(9)
    for m in (3, 5, 7):
        ests = [A.hash_estimate(matrix, m, rng) for _ in range(400)]
        cv = A.mean_cv(ests)[1]
        cell = len(tilings) / 2 ** m
        assert 0.6 / cell ** 0.5 < cv < 1.6 / cell ** 0.5, m


def test_analysis_is_deterministic_for_a_fixed_seed_and_changes_with_the_seed():
    s = ev.Settings("N-Damen-Suchbaum", 8, 300, "Knuth", 5)
    a, b = ev.analyse(s), ev.analyse(s)
    assert (a.estimate, a.half, a.cv, a.visited) == (b.estimate, b.half, b.cv, b.visited)
    c = ev.analyse(ev.Settings("N-Damen-Suchbaum", 8, 300, "Knuth", 6))
    assert c.estimate != a.estimate and c.exact == a.exact == 2057


def test_running_means_end_at_the_final_estimate_and_use_the_prefix_lengths():
    a = ev.analyse(ev.Settings("N-Damen-Suchbaum", 8, 1000, "Knuth", 3))
    assert [r["N"] for r in a.running] == [10, 30, 100, 300, 1000] and a.running[-1]["Mittel"] == a.estimate and a.running[-1]["halb"] == a.half


def test_exact_size_of_an_analysis_matches_the_algorithm_for_every_tree_task():
    for task in (C.TASK_QUEENS,) + C.TASK_KNAPSACK:
        a = ev.analyse(ev.Settings(task, 9 if task == C.TASK_QUEENS else 12, 30, "Knuth", 4))
        ch, root = ev.build_tree(task, a.n, 4)
        assert a.exact == a.exact_size == A.exact_size(ch, root)
