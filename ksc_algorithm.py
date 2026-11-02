"""Rechenkern: Schätzer von Knuth für die Größe eines Suchbaums und für Zählungen (Rosenbluth-Knuth), Chens geschichtete Probenahme, Hashing mit XOR-Bedingungen und die exakten Gegenstücke.

Ein Baum wird durch eine Funktion `children(knoten) -> Liste der Kinder` und eine Wurzel gegeben. Zufall kommt immer aus einem übergebenen `random.Random` (feste Seeds).
Exakte Rechnungen mit `int` und `Fraction`."""

from __future__ import annotations

import itertools
import math
import random
import statistics
from fractions import Fraction

import numpy as np

MAX_TREE_NODES, MAX_TREE_DEPTH = 300, 30


class TreeTooLarge(ValueError):
    """Der exakte Baum hat mehr Knoten als das Limit."""


# ---------------------------------------------------------------- Schätzer von Knuth
def knuth_probe(children, root, rng):
    """Eine Sondierung vom Blatt aus gesehen: (geschätzte Knotenzahl, Gewicht am Endknoten, Endknoten, Zahl der besuchten Knoten).
    Das Gewicht ist das Produkt der Kinderzahlen auf dem Weg; die Schätzung ist die Summe der Gewichte aller besuchten Knoten (Wurzel: 1)."""
    node, weight, size, visited = root, 1, 1, 1
    while True:
        kids = children(node)
        if not kids:
            return size, weight, node, visited
        weight *= len(kids)
        node = kids[rng.randrange(len(kids))]
        size += weight
        visited += 1


def exact_size(children, root, limit: int = 2_000_000) -> int:
    """Knotenzahl durch Tiefensuche; wirft TreeTooLarge über dem Limit."""
    count, stack = 0, [root]
    while stack:
        node = stack.pop()
        count += 1
        if count > limit:
            raise TreeTooLarge(f"Der Baum hat mehr als {limit} Knoten.")
        stack.extend(children(node))
    return count


def exact_leaf_count(children, root, accept, limit: int = 2_000_000) -> int:
    """Zahl der Blätter, für die `accept(blatt)` gilt (zum Beispiel vollständige Damenstellungen)."""
    count, seen, stack = 0, 0, [root]
    while stack:
        node = stack.pop()
        seen += 1
        if seen > limit:
            raise TreeTooLarge(f"Der Baum hat mehr als {limit} Knoten.")
        kids = children(node)
        if not kids and accept(node):
            count += 1
        stack.extend(kids)
    return count


def enumerate_probes(children, root, limit: int = 100_000) -> list:
    """Alle Sondierungen mit ihrer Wahrscheinlichkeit: Liste von (Fraction, Schätzung, Gewicht am Blatt). Exakte Verteilung des Schätzers."""
    out, stack = [], [(root, Fraction(1), 1, 1)]
    while stack:
        node, prob, weight, size = stack.pop()
        kids = children(node)
        if not kids:
            out.append((prob, size, weight))
            if len(out) > limit:
                raise TreeTooLarge(f"Mehr als {limit} Sondierungen.")
            continue
        d = len(kids)
        for k in kids:
            stack.append((k, prob / d, weight * d, size + weight * d))
    return out


def estimator_moments(dist: list) -> tuple:
    """(Erwartung, Varianz) der Schätzung aus der exakten Verteilung."""
    mean = sum(p * s for p, s, _ in dist)
    var = sum(p * (s - mean) ** 2 for p, s, _ in dist)
    return mean, var


# ---------------------------------------------------------------- Bäume in Klammerschreibweise
def parse_tree(text: str, max_nodes: int = MAX_TREE_NODES, max_depth: int = MAX_TREE_DEPTH) -> tuple:
    """Baum aus Klammern: "(()())" ist eine Wurzel mit zwei Blättern. Gibt (children, Wurzel 0, Knotenzahl) zurück; wirft ValueError mit deutscher Meldung."""
    s = "".join(text.split())
    if not s:
        raise ValueError("Der Baum ist leer: zum Beispiel ((()()())(())).")
    if set(s) - {"(", ")"}:
        raise ValueError("Erlaubt sind nur runde Klammern: zum Beispiel ((()()())(())).")
    kids: dict = {}
    stack: list = []
    n = 0
    for i, ch in enumerate(s):
        if ch == "(":
            node = n
            n += 1
            if n > max_nodes:
                raise ValueError(f"Höchstens {max_nodes} Knoten.")
            kids[node] = []
            if stack:
                kids[stack[-1]].append(node)
            elif i > 0:
                raise ValueError("Der Baum hat mehr als eine Wurzel: alles muss in einem äußeren Klammerpaar stehen.")
            stack.append(node)
            if len(stack) > max_depth + 1:
                raise ValueError(f"Höchstens Tiefe {max_depth}.")
        else:
            if not stack:
                raise ValueError("Zu viele schließende Klammern.")
            stack.pop()
    if stack:
        raise ValueError("Es fehlen schließende Klammern.")
    return (lambda node: kids[node]), 0, n


# ---------------------------------------------------------------- N-Damen
def queens_children(n: int):
    if n < 1:
        raise ValueError("Mindestens eine Dame.")

    def children(cols):
        r = len(cols)
        if r == n:
            return []
        return [cols + (c,) for c in range(n) if all(c != c0 and abs(c - c0) != r - r0 for r0, c0 in enumerate(cols))]
    return children


def queens_solutions(n: int) -> int:
    ch = queens_children(n)
    return exact_leaf_count(ch, (), lambda cols: len(cols) == n)


# ---------------------------------------------------------------- einfache Wege im Gitter (Rosenbluth-Knuth)
def grid_neighbor_lists(n: int) -> list:
    out = []
    for v in range(n * n):
        r, c = divmod(v, n)
        out.append([(r + dr) * n + c + dc for dr, dc in ((0, 1), (1, 0), (0, -1), (-1, 0)) if 0 <= r + dr < n and 0 <= c + dc < n])
    return out


def path_reachable(nb: list, start: int, target: int, blocked: int) -> bool:
    """Gibt es von `start` einen Weg nach `target` über Knoten, die nicht in der Bitmaske `blocked` stehen?"""
    seen = 1 << start
    stack = [start]
    while stack:
        v = stack.pop()
        if v == target:
            return True
        for w in nb[v]:
            bit = 1 << w
            if not (blocked | seen) & bit:
                seen |= bit
                stack.append(w)
    return False


def path_probe(n: int, rng: random.Random, check: bool, nb: list | None = None) -> tuple:
    """Eine Sondierung für einfache Wege von Ecke (0,0) nach Ecke (n−1,n−1): (Gewicht, Schritte). Gewicht = Produkt der Zahl der Möglichkeiten je Schritt, 0 bei Sackgasse.
    Mit `check` zählen nur Schritte, von denen aus das Ziel noch erreichbar ist."""
    if n < 2:
        raise ValueError("Das Gitter braucht mindestens 2×2 Knoten.")
    nb = nb or grid_neighbor_lists(n)
    target = n * n - 1
    v, visited, weight, steps = 0, 1, 1, 0
    while v != target:
        options = [w for w in nb[v] if not visited >> w & 1 and (w == target or not check or path_reachable(nb, w, target, visited | 1 << w))]
        if not options:
            return 0, steps
        weight *= len(options)
        v = options[rng.randrange(len(options))]
        visited |= 1 << v
        steps += 1
    return weight, steps


def path_distribution(n: int, check: bool) -> list:
    """Alle Sondierungen des Wege-Schätzers mit ihrer Wahrscheinlichkeit (exakt, nur für kleine Gitter): Liste von (Fraction, Gewicht)."""
    if n < 2 or n > 4:
        raise ValueError("Die vollständige Aufzählung gibt es nur für 2×2 bis 4×4.")
    nb = grid_neighbor_lists(n)
    target = n * n - 1
    out = []

    def rec(v, visited, prob, weight):
        if v == target:
            out.append((prob, weight))
            return
        options = [w for w in nb[v] if not visited >> w & 1 and (w == target or not check or path_reachable(nb, w, target, visited | 1 << w))]
        if not options:
            out.append((prob, 0))
            return
        for w in options:
            rec(w, visited | 1 << w, prob / len(options), weight * len(options))

    rec(0, 1, Fraction(1), 1)
    return out


def paths_brute(n: int) -> int:
    """Zahl der einfachen Wege von Ecke zu Ecke durch Rückverfolgung (Orakel, nur für n ≤ 5)."""
    if n < 2 or n > 5:
        raise ValueError("Das Zählen durch Rückverfolgung gibt es nur für 2×2 bis 5×5.")
    nb = grid_neighbor_lists(n)
    target = n * n - 1

    def rec(v, visited):
        if v == target:
            return 1
        return sum(rec(w, visited | 1 << w) for w in nb[v] if not visited >> w & 1)

    return rec(0, 1)


# ---------------------------------------------------------------- Rucksack, Branch-and-Bound-Baum mit festem Zielwert
def knapsack_instance(n: int, seed: int, correlated: bool) -> tuple:
    """(Gegenstände (Wert, Gewicht) nach fallendem Wert je Gewicht, Kapazität = halbe Gewichtssumme)."""
    if n < 1:
        raise ValueError("Mindestens ein Gegenstand.")
    rng = random.Random(seed)
    if correlated:
        items = []
        for _ in range(n):
            w = rng.randint(10, 60)
            items.append((w + 10, w))
    else:
        items = [(rng.randint(5, 40), rng.randint(5, 40)) for _ in range(n)]
    items.sort(key=lambda it: -it[0] / it[1])
    return items, sum(w for _, w in items) // 2


def knapsack_opt(items: list, cap: int) -> int:
    best = [0] * (cap + 1)
    for v, w in items:
        for c in range(cap, w - 1, -1):
            best[c] = max(best[c], best[c - w] + v)
    return best[cap]


def knapsack_brute(items: list, cap: int) -> int:
    best = 0
    for mask in range(1 << len(items)):
        w = sum(items[i][1] for i in range(len(items)) if mask >> i & 1)
        if w <= cap:
            best = max(best, sum(items[i][0] for i in range(len(items)) if mask >> i & 1))
    return best


def fractional_bound(items: list, cap: int, i: int, value: int, weight: int) -> float:
    room = cap - weight
    for v, w in items[i:]:
        if w <= room:
            value += v
            room -= w
        else:
            return value + v * room / w
    return value


def knapsack_children(items: list, cap: int, target: int):
    """Kinder eines Knotens (i, Wert, Gewicht): nehmen oder weglassen; gestrichen, wenn es nicht passt oder die Schranke unter dem Zielwert liegt. Der Baum ist fest, weil der Zielwert (das Optimum) fest ist."""
    def children(node):
        i, value, weight = node
        if i == len(items):
            return []
        v, w = items[i]
        out = []
        for take in (1, 0):
            nv, nw = (value + v, weight + w) if take else (value, weight)
            if nw <= cap and fractional_bound(items, cap, i + 1, nv, nw) >= target:
                out.append((i + 1, nv, nw))
        return out
    return children


# ---------------------------------------------------------------- Chen: geschichtete Probenahme
def chen_probe(children, root, rng: random.Random, depth_of=len) -> tuple:
    """Eine geschichtete Sondierung nach Chen: je Ebene bleibt je Typ (Tiefe, Zahl der Kinder) ein zufälliger Vertreter, der die Summe der Gewichte seines Typs trägt.
    Gibt (Schätzung der Knotenzahl, Zahl der berechneten Kinderlisten) zurück. Knoten müssen hashbar sein; `depth_of(knoten)` liefert die Tiefe."""
    cache: dict = {}

    def kids_of(node):
        if node not in cache:
            cache[node] = children(node)
        return cache[node]

    level = [(root, 1)]
    total = 1
    while level:
        buckets: dict = {}
        for node, w in level:
            for k in kids_of(node):
                buckets.setdefault((depth_of(k), len(kids_of(k))), []).append((k, w))
        level = []
        for members in buckets.values():
            wsum = sum(w for _, w in members)
            x = rng.random() * wsum
            acc = 0
            for k, w in members:
                acc += w
                if x < acc:
                    break
            level.append((k, wsum))
            total += wsum
    return total, len(cache)


# ---------------------------------------------------------------- Hashing mit XOR-Bedingungen
def domino_tilings(rows: int, cols: int) -> tuple:
    """Alle Parkettierungen des Bretts durch Dominosteine als Tupel von Kantennummern; zweiter Wert: Zahl der Kanten."""
    if rows < 1 or cols < 1:
        raise ValueError("Das Brett braucht mindestens eine Zeile und eine Spalte.")
    edges: dict = {}
    for r in range(rows):
        for c in range(cols):
            if c + 1 < cols:
                edges[(r * cols + c, r * cols + c + 1)] = len(edges)
            if r + 1 < rows:
                edges[(r * cols + c, (r + 1) * cols + c)] = len(edges)
    out: list = []

    def rec(pos, covered, chosen):
        while pos < rows * cols and covered >> pos & 1:
            pos += 1
        if pos == rows * cols:
            out.append(tuple(chosen))
            return
        r, c = divmod(pos, cols)
        if c + 1 < cols and not covered >> (pos + 1) & 1:
            rec(pos + 1, covered | 1 << pos | 1 << (pos + 1), chosen + [edges[(pos, pos + 1)]])
        if r + 1 < rows:
            rec(pos + 1, covered | 1 << pos | 1 << (pos + cols), chosen + [edges[(pos, pos + cols)]])

    rec(0, 0, [])
    return out, len(edges)


def tiling_matrix(tilings: list, n_edges: int) -> np.ndarray:
    m = np.zeros((len(tilings), n_edges), dtype=np.uint8)
    for i, t in enumerate(tilings):
        m[i, list(t)] = 1
    return m


def hash_cell_count(matrix: np.ndarray, c: np.ndarray, b: np.ndarray) -> int:
    """Zahl der Lösungen (Zeilen der Matrix), die die XOR-Bedingungen erfüllen: Spalte j von c wählt die Variablen, b[j] ist das Paritätsbit."""
    parity = (matrix @ c) & 1
    return int(np.count_nonzero((parity == b).all(axis=1)))


def hash_estimate(matrix: np.ndarray, m: int, rng: np.random.Generator) -> int:
    """Schätzung 2^m mal Zahl der Lösungen, die m zufällige XOR-Bedingungen (je mit zufälliger Variablenmenge und zufälligem Paritätsbit) erfüllen."""
    if m == 0:
        return len(matrix)
    c = rng.integers(0, 2, size=(matrix.shape[1], m), dtype=np.uint8)
    b = rng.integers(0, 2, size=m, dtype=np.uint8)
    return hash_cell_count(matrix, c, b) * 2 ** m


# ---------------------------------------------------------------- Statistik
def mean_cv(values: list) -> tuple:
    """(Mittel, Variationskoeffizient mit Streuung der Grundgesamtheit der Proben)."""
    m = statistics.fmean(values)
    return m, (statistics.pstdev(values) / m if m else math.inf)


def confidence_halfwidth(values: list, z: float = 1.96) -> float:
    if len(values) < 2:
        return math.inf
    return z * statistics.stdev(values) / math.sqrt(len(values))


def probes_for_error(cv: float, eps: float = 0.05) -> int:
    """Zahl der Sondierungen, für die der Standardfehler des Mittels höchstens `eps` mal das Mittel ist: ⌈cv² / eps²⌉."""
    if not (0 < eps < 1):
        raise ValueError("eps muss zwischen 0 und 1 liegen.")
    return math.ceil(cv ** 2 / eps ** 2)


def block_means(values: list, size: int) -> list:
    """Mittel aus aufeinanderfolgenden, nicht überlappenden Blöcken der Länge `size` (Rest wird verworfen)."""
    if size < 1:
        raise ValueError("Die Blockgröße muss mindestens 1 sein.")
    return [statistics.fmean(values[i:i + size]) for i in range(0, len(values) - size + 1, size)]
