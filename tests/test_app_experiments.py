"""Oberfläche: jede Aufgabe, jedes Verfahren, jedes Preset, Permalink mit Müll, die Spielwiese und das PDF laufen ohne Ausnahme und zeigen die erwarteten Texte."""

import os
from pathlib import Path

from streamlit.testing.v1 import AppTest

import ksc_constants as C
import ksc_evaluation as ev
import ksc_visualization as V

APP = str(Path(__file__).resolve().parent.parent / "app.py")
TIMEOUT = int(os.environ.get("APPTEST_TIMEOUT", "300"))


def _run(query=None, **state):
    at = AppTest.from_file(APP, default_timeout=TIMEOUT)
    for key, value in (query or {}).items():
        at.query_params[key] = value
    at.run()
    for key, value in state.items():
        at.session_state[key] = value
    if state:
        at.run()
    assert not at.exception, [str(e) for e in at.exception]
    return at


def _texts(at):
    return [e.value for e in at.success] + [e.value for e in at.warning] + [e.value for e in at.info] + [e.value for e in at.error]


def test_standard_case_shows_all_five_experiments_and_the_answer():
    at = _run()
    heads = [s.value for s in at.subheader]
    assert [h for h in heads if h.startswith("🔬 Experiment")] == [
        "🔬 Experiment 1: Unverzerrt, aber streuend", "🔬 Experiment 2: Wege im Gitter gegen die Wahrheit aus Stück 13", "🔬 Experiment 3: Wissen einspeisen",
        "🔬 Experiment 4: Wenn der Baum unausgeglichen ist", "🔬 Experiment 5: Chen und Hashing"]
    assert any(t.startswith("N-Damen, n = 10: Aus 10.000 Sondierungen") for t in _texts(at)) and not at.error


def test_metrics_of_the_standard_case():
    at = _run()
    assert [(m.label, m.value) for m in at.metric] == [("Schätzung", "35.792"), ("Wahrheit", "35.539"), ("Fehler", "0,7 %"), ("Variationskoeffizient", "0,65")]


def test_every_preset_runs_and_shows_its_task():
    for name, p in C.PRESETS.items():
        at = _run(task_select=p["task"], n_slider=p["n"], probes_select=p["probes"], method_select=p["method"], seed_slider=p["seed"])
        assert at.selectbox(key="task_select").value == p["task"], name
        assert not at.error, name


def test_every_task_with_every_method_runs_on_a_small_size():
    for task in C.TASKS:
        for method in C.METHODS:
            at = _run(task_select=task, n_slider=8, probes_select=30, method_select=method)
            assert not at.error, (task, method)


def test_fallback_notes_are_shown():
    at = _run(task_select=C.TASK_QUEENS, method_select=C.METHOD_CHECK, probes_select=30)
    assert any("nur bei den Wegen im Gitter" in t for t in _texts(at))
    at = _run(task_select=C.TASK_PATHS, n_slider=28, probes_select=30)
    assert any("von 2 bis 10" in t for t in _texts(at))


def test_permalink_garbage_falls_back_to_defaults():
    at = _run(query={"task": "Unsinn", "n": "abc", "probes": "7", "method": "Zauber", "seed": "0"})
    assert at.selectbox(key="task_select").value == C.DEFAULT_TASK and at.slider(key="n_slider").value == C.DEFAULT_N
    assert at.select_slider(key="probes_select").value == C.DEFAULT_PROBES and at.selectbox(key="method_select").value == C.DEFAULT_METHOD and at.slider(key="seed_slider").value == C.SEED_MIN


def test_play_ground_shows_exact_moments_and_reports_bad_input():
    at = _run()
    assert any(t.startswith("Der Baum hat 7 Knoten und 4 Blätter.") for t in _texts(at)) and "play_chart" in [c.key for c in at.get("plotly_chart")]
    bad = _run(play_tree="(()")
    assert any("fehlen schließende Klammern" in w.value for w in bad.warning) and "play_chart" not in [c.key for c in bad.get("plotly_chart")]
    full = _run(play_tree="((()())(()()))")
    assert any("die Varianz 0" in t for t in _texts(full))


def test_pdf_button_makes_a_download():
    at = _run()
    at.button(key="pdf_make").click().run(timeout=TIMEOUT)
    assert not at.exception, [str(e) for e in at.exception]
    assert len(at.get("download_button")) == 1


def test_charts_have_unique_keys():
    at = _run()
    keys = [c.key for c in at.get("plotly_chart")]
    assert len(keys) == len(set(keys)) and set(keys) == {"main_chart", "error_chart", "paths_chart", "check_chart", "knapsack_chart", "hash_chart", "play_chart"}


def test_pdf_builds_for_every_task_and_method():
    from ksc_pdf_export import build_pdf
    for task in C.TASKS:
        for method in C.METHODS:
            a = ev.analyse(ev.Settings(task, 8, 30, method, 3))
            assert build_pdf(a)[:4] == b"%PDF", (task, method)


def test_chart_builders_return_locked_axes():
    a = ev.analyse(ev.Settings(C.TASK_QUEENS, 8, 100, "Knuth", 1))
    play = ev.play_tree(C.PLAY_TREE_DEFAULT)
    for fig in (V.build_running(a.running, a.exact, "x"), V.build_error(ev.error_rows()), V.build_paths(ev.path_rows()), V.build_check(ev.check_rows()), V.build_knapsack(ev.knapsack_rows()), V.build_hash(ev.better_rows()), V.build_play(play)):
        assert fig.layout.xaxis.fixedrange and fig.layout.yaxis.fixedrange
