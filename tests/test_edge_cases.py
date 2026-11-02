"""Randfälle: Klemmen der Eingaben, Rückfälle, Obergrenzen, Fehler bei unbekannten Werten, Bäume mit Müll, Baum über dem Limit."""

import random

import pytest

import ksc_algorithm as A
import ksc_constants as C
import ksc_evaluation as ev

S = ev.Settings


def test_sizes_are_clamped_per_task_with_a_note():
    a = ev.analyse(S(C.TASK_QUEENS, 28, 30, "Knuth", 1))
    assert a.n == 10 and any("von 4 bis 10" in n for n in a.notes)
    b = ev.analyse(S(C.TASK_QUEENS, 2, 30, "Knuth", 1))
    assert b.n == 4 and b.exact == b.exact_size == 17
    c = ev.analyse(S(C.TASK_PATHS, 28, 30, "Knuth", 1))
    assert c.n == 10 and c.exact == 41044208702632496804
    d = ev.analyse(S(C.TASK_PATHS, 2, 30, "Knuth", 1))
    assert d.n == 2 and d.notes == [] and d.exact == 2 and d.estimate == 2.0
    e = ev.analyse(S(C.TASK_KNAPSACK[1], 2, 30, "Knuth", 1))
    assert e.n == 8 and any("von 8 bis 28" in n for n in e.notes)


def test_methods_fall_back_with_a_note_when_they_do_not_fit_the_task():
    a = ev.analyse(S(C.TASK_QUEENS, 6, 30, C.METHOD_CHECK, 1))
    assert a.method == "Knuth" and any("nur bei den Wegen" in n for n in a.notes)
    b = ev.analyse(S(C.TASK_PATHS, 4, 30, C.METHOD_CHEN, 1))
    assert b.method == "Knuth" and any("nur für Suchbäume" in n for n in b.notes)


def test_probe_caps_apply_per_method_with_a_note():
    a = ev.analyse(S(C.TASK_PATHS, 3, 30000, C.METHOD_CHECK, 1))
    assert a.probes == 1000 and any("höchstens 1.000" in n for n in a.notes)
    b = ev.analyse(S(C.TASK_QUEENS, 5, 10000, C.METHOD_CHEN, 1))
    assert b.probes == 3000 and any("höchstens 3.000" in n for n in b.notes)
    c = ev.analyse(S(C.TASK_QUEENS, 5, 30000, "Knuth", 1))
    assert c.probes == 30000 and c.notes == []


def test_unknown_task_and_method_raise():
    with pytest.raises(ValueError):
        ev.analyse(S("Zauber", 6, 30, "Knuth", 1))
    with pytest.raises(ValueError):
        ev.analyse(S(C.TASK_QUEENS, 6, 30, "Zauber", 1))


def test_ten_probes_give_an_interval_and_a_single_probe_does_not():
    a = ev.analyse(S(C.TASK_QUEENS, 6, 10, "Knuth", 1))
    assert a.probes == 10 and a.half < float("inf") and len(a.running) == 1 and a.running[0]["N"] == 10
    one = ev.analyse(S(C.TASK_QUEENS, 6, 0, "Knuth", 1))     # 0 wird auf 1 angehoben
    assert one.probes == 1 and one.half == float("inf") and any(w["Prüfung"] == "nur eine Sondierung: kein Intervall" for w in one.ways)


def test_tree_over_the_limit_has_no_truth_but_still_an_estimate(monkeypatch):
    monkeypatch.setattr(C, "EXACT_NODE_LIMIT", 50)
    a = ev.analyse(S(C.TASK_QUEENS, 8, 100, "Knuth", 1))
    assert a.exact is None and a.exact_size is None and a.rel_error is None and a.in_interval is None
    assert a.ways[0]["Prüfung"].startswith("Baum über 50 Knoten") and a.ways[0]["Prüfwert"] == "–"
    kind, text = ev.verdict_answers(a)
    assert kind == "success" and "die Wahrheit ist" not in text


def test_exact_size_limit_raises_a_dedicated_error():
    with pytest.raises(A.TreeTooLarge):
        A.exact_size(A.queens_children(8), (), limit=100)
    with pytest.raises(A.TreeTooLarge):
        A.exact_leaf_count(A.queens_children(8), (), lambda c: len(c) == 8, limit=100)
    with pytest.raises(A.TreeTooLarge):
        A.enumerate_probes(A.queens_children(8), (), limit=3)


def test_chain_and_single_node_trees():
    ch, root, n = A.parse_tree("(" * 12 + ")" * 12)
    assert n == 12 and A.estimator_moments(A.enumerate_probes(ch, root)) == (12, 0)
    ch, root, n = A.parse_tree("()")
    assert n == 1 and A.knuth_probe(ch, root, random.Random(1)) == (1, 1, 0, 1)


def test_play_tree_reports_errors_instead_of_raising():
    assert ev.play_tree("")["error"].startswith("Der Baum ist leer") and "runde Klammern" in ev.play_tree("(x)")["error"] and "mehr als eine Wurzel" in ev.play_tree("()()")["error"]
    assert ev.verdict_play({"error": "kaputt"}) == ("warning", "kaputt")
    big = "(" + "()" * 299 + ")"
    res = ev.play_tree(big)
    assert res["Knoten"] == 300 and res["Blätter"] == 299 and res["Erwartung"] == 300 and res["cv"] == 0.0 and res["nötig"] == 1


def test_formatting_helpers():
    assert ev.de(1.5, 2) == "1,50" and ev.de(-0.25, 1) == "−0,2" and ev.pct_text(0.1234) == "12,3 %"
    assert ev.big_text(999999999999999) == "999.999.999.999.999" and ev.big_text(10 ** 15) == "1,00·10¹⁵ (16 Stellen)" and ev.big_text(-1234) == "−1.234"
    assert ev.num_text(35538.6) == "35.539" and ev.num_text(3.52e19) == "3,52·10¹⁹" and ev.num_text(float("inf")) == "unbegrenzt"
    assert ev.plural(1, "Sondierung", "Sondierungen") == "1 Sondierung" and ev.plural(0, "Blatt", "Blätter") == "0 Blätter"
