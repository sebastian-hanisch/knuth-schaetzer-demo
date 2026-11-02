"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen, jedes Preset zeigt etwas anderes."""

import ksc_constants as C
import ksc_evaluation as ev
import ksc_presets as P


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_regler_bounds():
    for name, preset in C.PRESETS.items():
        assert preset["task"] in C.TASKS and preset["method"] in C.METHODS and preset["probes"] in C.PROBE_CHOICES, name
        lo, hi = C.SIZE_RANGE[preset["task"]]
        assert lo <= preset["n"] <= hi, name
        assert C.SEED_MIN <= preset["seed"] <= C.SEED_MAX
        assert preset["probes"] <= C.PROBE_CAP[preset["method"]], name


def test_default_preset_equals_default_settings_and_comes_first():
    first = next(iter(C.PRESETS.values()))
    for field, key in P.PRESET_KEYS.items():
        assert first[field] == P.SETTING_SPECS[key].default


def test_every_preset_passes_the_checker_without_notes_or_problems():
    for name, preset in C.PRESETS.items():
        a = ev.analyse(ev.Settings(**preset))
        assert a.problems == [] and a.notes == [], name


def test_presets_differ_from_each_other():
    seen = set()
    for name, preset in C.PRESETS.items():
        key = tuple(preset[f] for f in P.PRESET_KEYS)
        assert key not in seen, name
        seen.add(key)


def test_every_task_and_every_method_appears_in_a_preset():
    assert {p["task"] for p in C.PRESETS.values()} >= {C.TASK_QUEENS, C.TASK_PATHS, C.TASK_KNAPSACK[1]}
    assert {p["method"] for p in C.PRESETS.values()} == set(C.METHODS)


def test_setting_specs_cover_every_preset_key():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)
    assert P.SETTING_SPECS["task_select"].choices == C.TASKS and P.SETTING_SPECS["method_select"].choices == C.METHODS and P.SETTING_SPECS["probes_select"].choices == C.PROBE_CHOICES
