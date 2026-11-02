"""Jede Zahl aus der README und aus den Texten der App, nachgerechnet (DEMO-PLAYBOOK §4). Zufallsziehungen laufen mit festen Seeds und sind deterministisch; Zeiten kommen nicht vor."""

from pathlib import Path

import ksc_algorithm as A
import ksc_constants as C
import ksc_evaluation as ev

README = (Path(__file__).resolve().parent.parent / "README.md").read_text(encoding="utf-8")
S = ev.Settings


def f(x, d):
    return f"{x:.{d}f}"


def test_readme_hand_tree_row():
    ch, root, n = A.parse_tree("((()()())(()))")
    dist = A.enumerate_probes(ch, root)
    assert (n, len(dist), A.estimator_moments(dist)) == (7, 4, (7, 4))
    res = ev.play_tree("((()()())(()))")
    assert f(res["cv"], 2) == "0.29" and res["nötig"] == 33 and res["Ergebnisse"][0][0] == 5


def test_readme_queens_rows():
    assert [(A.exact_size(A.queens_children(n), ()), A.queens_solutions(n)) for n in (6, 8, 9, 10)] == [(153, 4), (2057, 92), (8394, 352), (35539, 724)]


def test_readme_error_rows():
    res = ev.error_rows()
    expected = {8: [(11.1, 32.9), (3.4, 9.9), (1.3, 3.8), (0.85, 2.4)], 10: [(13.6, 39.6), (4.6, 13.2), (1.2, 4.1), (1.1, 2.2)]}
    for n, vals in expected.items():
        rows = {r["N"]: r for r in res[n]["Reihe"]}
        got = [(100 * rows[N]["Median"], 100 * rows[N]["Quantil95"]) for N in (10, 100, 1000, 3000)]
        assert [(round(a, 2 if a < 1 else 1), round(b, 1)) for a, b in got] == vals, n
    assert (round(res[8]["Steigung"], 2), round(res[10]["Steigung"], 2)) == (-0.45, -0.48) and (f(res[8]["cv"], 2), f(res[10]["cv"], 2)) == ("0.52", "0.65")


def test_readme_standard_case_row():
    a = ev.analyse(S(**C.PRESETS["Standardfall: N-Damen n = 10"]))
    assert (round(a.estimate), a.exact, f(100 * a.rel_error, 1), round(a.half), a.probes_needed) == (35792, 35539, "0.7", 458, 171)
    assert round(a.cost_needed) == 1496 and f(35539 / a.cost_needed, 1) == "23.8" and a.visited == 87504
    assert [w["Wert"] for w in a.ways if w["Größe"] == "Zahl der Lösungen"] == ["714"]


def test_readme_path_rows():
    rows = {r["n"]: r for r in ev.path_rows()}
    expected = {4: (0.977, 0.70, 198), 5: (1.043, 1.19, 566), 6: (0.958, 1.70, 1155), 7: (0.971, 2.35, 2207), 8: (0.731, 3.36, 4524), 9: (0.804, 4.29, 7377), 10: (0.606, 5.36, 11505)}
    for n, (ratio, cv, needed) in expected.items():
        assert (round(rows[n]["Verhältnis"], 3), round(rows[n]["cv"], 2), rows[n]["nötig"]) == (ratio, cv, needed), n
    assert [n for n, r in rows.items() if not r["im Intervall"]] == [8, 10]


def test_readme_check_rows():
    rows = {r["n"]: r for r in ev.check_rows()}
    assert [f(100 * rows[n]["Erfolgsrate"], 1) for n in range(4, 9)] == ["56.7", "43.6", "33.6", "25.2", "19.6"]
    assert [f(rows[n]["cv_ohne"], 2) for n in range(4, 9)] == ["1.48", "3.00", "5.66", "10.41", "19.04"]
    assert [f(rows[n]["cv_mit"], 2) for n in range(4, 9)] == ["0.70", "1.19", "1.70", "2.35", "3.36"] and f(rows[8]["Faktor"], 1) == "5.7"
    assert [f(100 * rows[n]["Überdeckung"], 1) for n in range(4, 9)] == ["96.7", "100.0", "96.7", "96.7", "86.7"] and {r["Blöcke"] for r in rows.values()} == {30}


def test_readme_preset_path_rows():
    a = ev.analyse(S(**C.PRESETS["Wege im 8×8-Gitter mit Erreichbarkeitsprüfung"]))
    assert (round(a.estimate), a.exact, f(100 * a.rel_error, 1), f(a.cv, 2)) == (714220393223, 789360053252, "9.5", "3.77")
    b = ev.analyse(S(**C.PRESETS["Wege im 8×8-Gitter ohne Prüfung"]))
    assert (round(b.estimate), f(100 * b.rel_error, 1), f(100 * b.success_rate, 1), f(b.cv, 2)) == (1042690361410, "32.1", "20.2", "18.09")
    c = ev.analyse(S(**C.PRESETS["Wege im 10×10-Gitter: 4,1·10¹⁹"]))
    assert (f"{c.estimate:.3g}", c.exact, f(100 * c.rel_error, 1), f(c.cv, 2)) == ("3.52e+19", 41044208702632496804, "14.3", "6.20")


def test_readme_knapsack_rows():
    rows = {(r["n"], r["korreliert"]): r for r in ev.knapsack_rows()}
    expected = {(16, True): (441, "5.03", 35.0, 6.8), (20, True): (35, "0.23", 1.4, 0.1), (24, True): (7496, "24.95", 77.4, 56.6), (28, True): (29, "0.00", 0.0, 0.0), (24, False): (39, "0.31", 1.7, 0.6)}
    for key, (size, cv, e100, e1000) in expected.items():
        r = rows[key]
        assert (r["Knoten"], f(r["cv"], 2), round(100 * r["Fehler"][100], 1), round(100 * r["Fehler"][1000], 1)) == (size, cv, e100, e1000), key
    assert rows[(24, True)]["voll"] == 33554431
    p = ev.analyse(S(**C.PRESETS["Rucksack-Baum n = 24: der schwierige Fall"]))
    assert (round(p.estimate), p.exact, f(p.cv, 2), p.probes_needed, round(p.cost_needed)) == (9397, 7496, "22.95", 210607, 5126659)


def test_readme_chen_rows():
    rows = {r["n"]: r for r in ev.better_rows()["chen"]}
    assert [f(rows[n]["Chen cv"], 2) for n in (8, 9, 10)] == ["0.30", "0.38", "0.37"] and [f(rows[n]["Knuth cv"], 2) for n in (8, 9, 10)] == ["0.52", "0.61", "0.67"]
    assert [round(rows[n]["Chen Kosten"]) for n in (8, 9, 10)] == [40, 55, 72] and [f(rows[n]["Knuth Kosten"], 1) for n in (8, 9, 10)] == ["7.2", "8.0", "8.8"]
    assert [rows[n]["k"] for n in (8, 9, 10)] == [6, 7, 8] and all(rows[n]["Knuth gleicher Aufwand cv"] < rows[n]["Chen cv"] for n in rows)
    assert [f(rows[n]["Knuth gleicher Aufwand cv"], 2) for n in (8, 9, 10)] == ["0.22", "0.22", "0.25"]


def test_readme_hash_rows():
    res = ev.better_rows()
    assert (res["Parkettierungen"], res["Kanten"], res["Brett"]) == (6728, 60, "6×6")
    rows = res["hash"]
    assert [round(r["Mittel"]) for r in rows] == [6728, 6725, 6715, 6760, 6712, 6697, 6732, 6708, 6742]
    assert [f(r["cv"], 3) for r in rows] == ["0.000", "0.009", "0.024", "0.037", "0.042", "0.060", "0.086", "0.147", "0.199"]
    assert [f(r["1/Wurzel"], 3) for r in rows] == ["0.012", "0.017", "0.024", "0.034", "0.049", "0.069", "0.098", "0.138", "0.195"]


def test_readme_path_truth_row_and_hand_distributions():
    assert [C.KNOWN_PATHS[n] for n in range(2, 11)] == [2, 12, 184, 8512, 1262816, 575780564, 789360053252, 3266598486981642, 41044208702632496804]
    assert [A.paths_brute(n) for n in (2, 3, 4, 5)] == [2, 12, 184, 8512]
    for n, truth in ((2, 2), (3, 12), (4, 184)):
        for check in (False, True):
            assert sum(p * w for p, w in A.path_distribution(n, check)) == truth
    assert {w for _, w in A.path_distribution(2, False)} == {2}


def test_preset_help_numbers_match_the_computation():
    h = C.PRESET_HELP
    std = ev.analyse(S(**C.PRESETS["Standardfall: N-Damen n = 10"]))
    assert all(x in h["Standardfall: N-Damen n = 10"] for x in ("35.539", "weniger als 1 Prozent", "0,65", "171")) and std.exact == 35539 and f(std.cv, 2) == "0.65" and std.rel_error < 0.01 and std.probes_needed == 171
    pc = ev.analyse(S(**C.PRESETS["Wege im 8×8-Gitter mit Erreichbarkeitsprüfung"]))
    assert all(x in h["Wege im 8×8-Gitter mit Erreichbarkeitsprüfung"] for x in ("789.360.053.252", "1.000", "rund 10 Prozent")) and 0.05 < pc.rel_error < 0.15 and pc.success_rate == 1.0
    pn = ev.analyse(S(**C.PRESETS["Wege im 8×8-Gitter ohne Prüfung"]))
    assert "etwa vier von fünf" in h["Wege im 8×8-Gitter ohne Prüfung"] and 0.78 < 1 - pn.success_rate < 0.82 and 4.5 < pn.cv / pc.cv < 5.0
    p10 = ev.analyse(S(**C.PRESETS["Wege im 10×10-Gitter: 4,1·10¹⁹"]))
    assert all(x in h["Wege im 10×10-Gitter: 4,1·10¹⁹"] for x in ("41.044.208.702.632.496.804", "etwa 15 Prozent")) and 0.10 < p10.rel_error < 0.20
    kn = ev.analyse(S(**C.PRESETS["Rucksack-Baum n = 24: der schwierige Fall"]))
    assert all(x in h["Rucksack-Baum n = 24: der schwierige Fall"] for x in ("7.496", "33.554.431", "25")) and kn.exact == 7496 and 2 ** 25 - 1 == 33554431 and round(kn.cv) == 23 and kn.cost_needed > kn.exact * 100
    ch = ev.analyse(S(**C.PRESETS["N-Damen n = 10 mit Chens Schichtung"]))
    assert ch.cv < std.cv and ch.visited / ch.probes > std.visited / std.probes


def test_limits_table_numbers():
    assert (C.SIZE_RANGE[C.TASK_QUEENS][1], C.SIZE_RANGE[C.TASK_PATHS][1], C.SIZE_RANGE[C.TASK_KNAPSACK[0]][1]) == (10, 10, 28)
    assert (C.PROBE_CAP["Knuth"], C.PROBE_CAP[C.METHOD_CHECK], C.PROBE_CAP[C.METHOD_CHEN]) == (30000, 1000, 3000)
    a = ev.analyse(S(**C.PRESETS["Standardfall: N-Damen n = 10"]))
    assert f(a.exact_size / a.cost_needed, 0) == "24" and f(a.exact_size / a.cost_needed, 1) == "23.8"


def test_readme_mentions_every_module_file():
    root = Path(__file__).resolve().parent.parent
    for p in root.glob("ksc_*.py"):
        assert f"`{p.name}`" in README, p.name
    assert "`app.py`" in README and "Stück 15 von 16" in README
