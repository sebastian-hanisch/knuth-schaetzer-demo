"""Konstanten: Regler-Grenzen, feste Annahmen, Farben und Presets."""

TASKS = ("N-Damen-Suchbaum", "Einfache Wege im Gitter", "Rucksack-Baum (zufällig)", "Rucksack-Baum (stark korreliert)")
DEFAULT_TASK = "N-Damen-Suchbaum"
TASK_PATHS, TASK_QUEENS = "Einfache Wege im Gitter", "N-Damen-Suchbaum"
TASK_KNAPSACK = ("Rucksack-Baum (zufällig)", "Rucksack-Baum (stark korreliert)")
METHODS = ("Knuth", "Knuth mit Erreichbarkeitsprüfung", "Chen-Schichtung")
DEFAULT_METHOD = "Knuth"
METHOD_CHECK, METHOD_CHEN = METHODS[1], METHODS[2]

SIZE_RANGE = {"N-Damen-Suchbaum": (4, 10), "Einfache Wege im Gitter": (2, 10), "Rucksack-Baum (zufällig)": (8, 28), "Rucksack-Baum (stark korreliert)": (8, 28)}
N_MIN, N_MAX, DEFAULT_N = 2, 28, 10
PROBE_CHOICES = (10, 30, 100, 300, 1000, 3000, 10000, 30000)
DEFAULT_PROBES = 10000
PROBE_CAP = {"Knuth": 30000, "Knuth mit Erreichbarkeitsprüfung": 1000, "Chen-Schichtung": 3000}
SEED_MIN, SEED_MAX, DEFAULT_SEED = 1, 99, 7

EXACT_NODE_LIMIT = 2_000_000       # exakte Baumgröße durch Tiefensuche bis zu so vielen Knoten
BRUTE_N_LIMIT = 5                  # Zählen der Wege durch Rückverfolgung bis 5×5
KNAPSACK_SEED_BASE = 20261102
ERROR_TARGET = 0.05                # Standardfehler, für den die Zahl der nötigen Sondierungen angegeben wird
PREFIXES = (10, 30, 100, 300, 1000, 3000, 10000, 30000)

KNOWN_PATHS = {2: 2, 3: 12, 4: 184, 5: 8512, 6: 1262816, 7: 575780564, 8: 789360053252, 9: 3266598486981642, 10: 41044208702632496804}   # aus Stück 13 (Frontier-Diagramm), bis n = 5 durch Rückverfolgung geprüft

EXP_QUEENS_NS = (8, 10)
EXP_QUEENS_POOL, EXP_QUEENS_BLOCKS = 30000, (10, 30, 100, 300, 1000, 3000)
EXP_PATH_NS, EXP_PATH_PROBES = (4, 5, 6, 7, 8, 9, 10), 600
EXP_CHECK_NS, EXP_CHECK_POOL, EXP_CHECK_BLOCK = (4, 5, 6, 7, 8), 30000, 1000
EXP_KNAP_INSTANCES = ((16, 1, True), (20, 2, True), (24, 3, True), (28, 4, True), (24, 3, False))   # (Gegenstände, Seed, stark korreliert)
EXP_KNAP_POOL, EXP_KNAP_BLOCKS = 10000, (100, 1000)
EXP_BETTER_NS, EXP_BETTER_REPS = (8, 9, 10), 300
EXP_HASH_BOARD, EXP_HASH_MS, EXP_HASH_REPS = (6, 6), (0, 1, 2, 3, 4, 5, 6, 7, 8), 200
EXP_SEED = 20261102
PLAY_TREE_DEFAULT = "((()()())(()))"
PLAY_MAX_NODES = 300

COLOR_MAIN = "#2F6B65"
COLOR_ALL = "rgba(150,150,150,0.75)"
COLOR_WARN = "#c0504d"
COLOR_LINE = "#4c78a8"

PRESETS = {
    "Standardfall: N-Damen n = 10": {"task": "N-Damen-Suchbaum", "n": 10, "probes": 10000, "method": "Knuth", "seed": 7},
    "Wege im 8×8-Gitter mit Erreichbarkeitsprüfung": {"task": "Einfache Wege im Gitter", "n": 8, "probes": 1000, "method": "Knuth mit Erreichbarkeitsprüfung", "seed": 7},
    "Wege im 8×8-Gitter ohne Prüfung": {"task": "Einfache Wege im Gitter", "n": 8, "probes": 10000, "method": "Knuth", "seed": 7},
    "Wege im 10×10-Gitter: 4,1·10¹⁹": {"task": "Einfache Wege im Gitter", "n": 10, "probes": 1000, "method": "Knuth mit Erreichbarkeitsprüfung", "seed": 7},
    "Rucksack-Baum n = 24: der schwierige Fall": {"task": "Rucksack-Baum (stark korreliert)", "n": 24, "probes": 10000, "method": "Knuth", "seed": 3},
    "N-Damen n = 10 mit Chens Schichtung": {"task": "N-Damen-Suchbaum", "n": 10, "probes": 1000, "method": "Chen-Schichtung", "seed": 7},
}
PRESET_HELP = {
    "Standardfall: N-Damen n = 10": "Der Suchbaum der zehn Damen hat 35.539 Knoten; 10.000 Zufallsabstiege schätzen ihn auf weniger als 1 Prozent genau, der Variationskoeffizient einer Sondierung ist 0,65; für 5 Prozent Standardfehler reichten schon 171.",
    "Wege im 8×8-Gitter mit Erreichbarkeitsprüfung": "789.360.053.252 einfache Wege (Stück 13): 1.000 Sondierungen mit Vorausschau schätzen sie auf rund 10 Prozent genau; jede Sondierung erreicht das Ziel.",
    "Wege im 8×8-Gitter ohne Prüfung": "Ohne Vorausschau enden etwa vier von fünf Sondierungen in einer Sackgasse (Gewicht 0), der Variationskoeffizient ist knapp fünfmal so groß wie mit Prüfung.",
    "Wege im 10×10-Gitter: 4,1·10¹⁹": "41.044.208.702.632.496.804 Wege (Stück 13): der Schätzer kommt mit 1.000 Sondierungen auf etwa 15 Prozent heran; ein Aufzählen aller Wege wäre unmöglich.",
    "Rucksack-Baum n = 24: der schwierige Fall": "Der Branch-and-Bound-Baum hat nur 7.496 Knoten (von 33.554.431 im vollen Baum), aber sehr ungleich verteilt: der Variationskoeffizient ist 25, und auch 10.000 Sondierungen liegen noch weit daneben, mehr Aufwand als das Aufzählen.",
    "N-Damen n = 10 mit Chens Schichtung": "Chens Verfahren behält je Ebene und Typ einen Vertreter: kleinere Streuung je Sondierung, aber mehr Aufwand je Sondierung.",
}
