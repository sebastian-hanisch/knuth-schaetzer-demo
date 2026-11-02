"""Gemeinsame Fixtures: die Mini-Instanzen, an denen jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture
def hand_tree():
    """Baum ((()()())(())): Wurzel mit Kind a (drei Blätter) und Kind b (ein Blatt): 1 + 2 + 3 + 1 = 7 Knoten, 4 Blätter.
    Sondierungen: über a zu einem der drei Blätter, je Wahrscheinlichkeit 1/2 · 1/3 = 1/6, Gewichte 1, 2, 2 · 3 = 6: Schätzung 1 + 2 + 6 = 9;
    über b, Wahrscheinlichkeit 1/2, Gewichte 1, 2, 2 · 1 = 2: Schätzung 1 + 2 + 2 = 5. Erwartung (3/6) · 9 + (1/2) · 5 = 4,5 + 2,5 = 7; Varianz (1/2)(9 − 7)² + (1/2)(5 − 7)² = 4."""
    return {"text": "((()()())(()))", "nodes": 7, "leaves": 4, "mean": 7, "var": 4, "outcomes": {9: (1, 2), 5: (1, 2)}}


@pytest.fixture
def complete_tree():
    """Vollständiger Baum mit Verzweigung 2 und Tiefe 2: 1 + 2 + 4 = 7 Knoten; jede Sondierung gibt 1 + 2 + 4 = 7: Varianz 0."""
    return {"text": "((()())(()()))", "nodes": 7}
