"""Auswertung: die eingestellte Schätzung mit Wahrheit, Intervall und Aufwand, fünf Experimente, die Spielwiese und die Urteilstexte. Alle Zufallsziehungen laufen mit festen Seeds."""

import functools
import math
import random
import statistics
from dataclasses import dataclass, field
from fractions import Fraction

import numpy as np

import ksc_algorithm as A
import ksc_constants as C

_SUPER = str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻")


@dataclass(frozen=True)
class Settings:
    task: str
    n: int
    probes: int
    method: str
    seed: int


@dataclass
class Analysis:
    settings: Settings
    task: str
    label: str
    n: int
    method: str
    probes: int
    seed: int
    estimate: float
    half: float
    cv: float
    exact: int | None
    exact_size: int | None
    rel_error: float | None
    in_interval: bool | None
    probes_needed: int
    cost_needed: float
    visited: int
    success_rate: float | None
    running: list
    ways: list
    problems: list
    notes: list


# ----------------------------------------------------------------------------- Formatierung
def de(x: float, digits: int = 2) -> str:
    return f"{x:.{digits}f}".replace(".", ",").replace("-", "−")


def big_text(x: int) -> str:
    """Ganze Zahl lesbar: bis 15 Stellen mit Tausenderpunkt, darüber Mantisse mal Zehnerpotenz mit Stellenzahl."""
    if x < 0:
        return "−" + big_text(-x)
    if x < 10 ** 15:
        return f"{x:,}".replace(",", ".")
    d = len(str(x)) if x < 10 ** 4000 else int(math.log10(x)) + 1
    s = str(x // 10 ** (d - 3))
    return f"{s[0]},{s[1:3]}·10{str(d - 1).translate(_SUPER)} ({d} Stellen)"


def num_text(x: float) -> str:
    """Gleitkommazahl lesbar: ganzzahlig mit Tausenderpunkt bis 10^15, darüber Mantisse und Zehnerpotenz."""
    if not math.isfinite(x):
        return "unbegrenzt"
    if abs(x) < 1e15:
        return big_text(round(x))
    mant, exp = f"{x:.2e}".split("e")
    return f"{mant.replace('.', ',')}·10{str(int(exp)).translate(_SUPER)}"


def pct_text(x: float) -> str:
    return de(100 * x, 1) + " %"


def plural(n: int, one: str, many: str) -> str:
    return f"{big_text(n)} {one if n == 1 else many}"


# ----------------------------------------------------------------------------- Eingaben
def effective_settings(s: Settings) -> tuple:
    """(Aufgabe, n, Verfahren, Sondierungen, Hinweise) nach Klemmen auf die Grenzen und Rückfall nicht passender Verfahren."""
    if s.task not in C.TASKS:
        raise ValueError(f"unbekannte Aufgabe {s.task!r}")
    if s.method not in C.METHODS:
        raise ValueError(f"unbekanntes Verfahren {s.method!r}")
    notes: list = []
    lo, hi = C.SIZE_RANGE[s.task]
    n = max(lo, min(s.n, hi))
    if n != s.n:
        notes.append(f"Für diese Aufgabe gibt es Größen von {lo} bis {hi}: gerechnet wird mit {n}.")
    method = s.method
    if method == C.METHOD_CHECK and s.task != C.TASK_PATHS:
        method = "Knuth"
        notes.append("Die Erreichbarkeitsprüfung gibt es nur bei den Wegen im Gitter: gerechnet wird mit dem Verfahren von Knuth.")
    if method == C.METHOD_CHEN and s.task == C.TASK_PATHS:
        method = "Knuth"
        notes.append("Chens Schichtung gibt es nur für Suchbäume, nicht für die Wege im Gitter: gerechnet wird mit dem Verfahren von Knuth.")
    probes = max(1, s.probes)
    cap = C.PROBE_CAP[method]
    if probes > cap:
        notes.append(f"Mit diesem Verfahren rechnet die App höchstens {big_text(cap)} Sondierungen: gerechnet wird mit {big_text(cap)}.")
        probes = cap
    return s.task, n, method, probes, notes


def task_label(task: str, n: int) -> str:
    if task == C.TASK_QUEENS:
        return f"N-Damen, n = {n}"
    if task == C.TASK_PATHS:
        return f"Wege im {n}×{n}-Gitter"
    return f"Rucksack-Baum mit {n} Gegenständen ({'stark korreliert' if task == C.TASK_KNAPSACK[1] else 'zufällig'})"


def build_tree(task: str, n: int, seed: int):
    """(children, Wurzel) für die Baum-Aufgaben."""
    if task == C.TASK_QUEENS:
        return A.queens_children(n), ()
    items, cap = A.knapsack_instance(n, C.KNAPSACK_SEED_BASE + seed, task == C.TASK_KNAPSACK[1])
    target = A.knapsack_opt(items, cap)
    return A.knapsack_children(items, cap, target), (0, 0, 0)


def _row(size, value, way="", check_value="", check=""):
    return {"Größe": size, "Wert": value, "Prüfweg": way, "Prüfwert": check_value, "Prüfung": check}


def _interval_check(est: float, half: float, exact: int):
    return "Wahrheit im Intervall" if abs(est - exact) <= half else "Wahrheit außerhalb des Intervalls (in etwa 5 von 100 Fällen zu erwarten)"


# ----------------------------------------------------------------------------- die eingestellte Schätzung
def analyse(s: Settings) -> Analysis:
    task, n, method, probes, notes = effective_settings(s)
    rng = random.Random(s.seed)
    problems: list = []
    ways: list = []
    values: list = []           # Schätzung der Hauptgröße je Sondierung
    solution_values: list = []  # nur N-Damen: Schätzung der Lösungszahl je Sondierung
    visited = 0
    exact_n = exact_sol = None
    success = None
    if task == C.TASK_PATHS:
        if n < 2:
            raise ValueError("Das Gitter braucht mindestens 2×2 Knoten.")
        nb = A.grid_neighbor_lists(n)
        check = method == C.METHOD_CHECK
        steps_total = 0
        for _ in range(probes):
            w, steps = A.path_probe(n, rng, check, nb)
            values.append(w)
            steps_total += steps + 1
        visited = steps_total
        success = sum(1 for v in values if v) / probes
        exact = C.KNOWN_PATHS[n]
        if n <= C.BRUTE_N_LIMIT:
            brute = A.paths_brute(n)
            if brute != exact:
                problems.append("Die Zahl der Wege weicht von Stück 13 ab")
    else:
        children, root = build_tree(task, n, s.seed)
        try:
            exact_n = A.exact_size(children, root, C.EXACT_NODE_LIMIT)
        except A.TreeTooLarge:
            exact_n = None
        exact = exact_n
        if method == C.METHOD_CHEN:
            for _ in range(probes):
                est, calls = A.chen_probe(children, root, rng, depth_of=(len if task == C.TASK_QUEENS else (lambda node: node[0])))
                values.append(est)
                visited += calls
        else:
            for _ in range(probes):
                est, weight, node, vis = A.knuth_probe(children, root, rng)
                values.append(est)
                visited += vis
                if task == C.TASK_QUEENS:
                    solution_values.append(weight if len(node) == n else 0)
        if task == C.TASK_QUEENS:
            exact_sol = A.queens_solutions(n)
    est, cv = A.mean_cv(values)
    if probes < 2:
        cv = math.inf   # aus einer Sondierung lässt sich keine Streuung bestimmen
    half = A.confidence_halfwidth(values)
    rel = abs(est - exact) / exact if exact else None
    inside = abs(est - exact) <= half if (exact is not None and math.isfinite(half)) else None
    needed = A.probes_for_error(cv, C.ERROR_TARGET) if math.isfinite(cv) else 0
    running = []
    for p in C.PREFIXES:
        if p <= probes:
            part = values[:p]
            running.append({"N": p, "Mittel": statistics.fmean(part), "halb": A.confidence_halfwidth(part)})
    if not running or running[-1]["N"] != probes:
        running.append({"N": probes, "Mittel": est, "halb": half})
    label = task_label(task, n)
    main = "Zahl der einfachen Wege" if task == C.TASK_PATHS else "Knotenzahl des Suchbaums"
    ways.append(_row(main, num_text(est), "Wahrheit" if exact is not None else "Wahrheit", num_text(exact) if exact is not None else "–",
                     _interval_check(est, half, exact) if inside is not None or exact is not None and math.isfinite(half) else ("nur eine Sondierung: kein Intervall" if exact is not None else f"Baum über {big_text(C.EXACT_NODE_LIMIT)} Knoten")))
    ways[-1]["Prüfweg"] = ("Stück 13 (Frontier-Diagramm)" if task == C.TASK_PATHS else "Aufzählen durch Tiefensuche")
    if task == C.TASK_PATHS and n <= C.BRUTE_N_LIMIT:
        ways.append(_row("Zahl der einfachen Wege", big_text(exact), "Rückverfolgung aller Wege", big_text(A.paths_brute(n)), "gleich" if A.paths_brute(n) == exact else "weicht ab"))
    if task == C.TASK_QUEENS and solution_values:
        sol_est, _ = A.mean_cv(solution_values)
        sol_half = A.confidence_halfwidth(solution_values)
        ways.append(_row("Zahl der Lösungen", num_text(sol_est), "Aufzählen durch Tiefensuche", big_text(exact_sol), _interval_check(sol_est, sol_half, exact_sol) if math.isfinite(sol_half) else "nur eine Sondierung: kein Intervall"))
    ways.append(_row("Halbbreite des 95-Prozent-Intervalls", num_text(half) if math.isfinite(half) else "–", "Normalnäherung (1,96 · Standardfehler)", "", "gilt nur bei endlicher, nicht zu schiefer Streuung"))
    ways.append(_row("Variationskoeffizient der Gewichte", de(cv, 2) if math.isfinite(cv) else ("nicht bestimmbar" if probes < 2 else "unbegrenzt"), "Streuung der Einzelschätzungen geteilt durch ihr Mittel", "", ""))
    ways.append(_row(f"Sondierungen für {pct_text(C.ERROR_TARGET)} Standardfehler", big_text(needed), "Variationskoeffizient zum Quadrat durch (0,05)²", "", ""))
    if success is not None:
        ways.append(_row("Anteil der Sondierungen, die das Ziel erreichen", pct_text(success), "Zählen der Gewichte ungleich 0", "", "mit Erreichbarkeitsprüfung immer 100 %" if method == C.METHOD_CHECK else ""))
    unit = "Kinderlisten" if method == C.METHOD_CHEN else "besuchte Knoten"
    if task == C.TASK_PATHS:
        ways.append(_row("Aufwand dieses Laufs", f"{big_text(visited)} Schritte", "Summe der Schritte aller Sondierungen", "", ""))
    else:
        ways.append(_row("Aufwand dieses Laufs", f"{big_text(visited)} {unit}", "Summe über alle Sondierungen", "", ""))
        if exact_n is not None and needed > 0:
            cost = needed * visited / probes
            ways.append(_row(f"Aufwand für {pct_text(C.ERROR_TARGET)} Standardfehler: Schätzen gegen Aufzählen", f"{num_text(cost)} gegen {big_text(exact_n)}", "nötige Sondierungen mal Aufwand je Sondierung gegen Baumgröße", "",
                             "Aufzählen ist billiger" if exact_n < cost else f"Schätzen ist billiger (Faktor {de(exact_n / cost, 1)})"))
    return Analysis(s, task, label, n, method, probes, s.seed, est, half, cv, exact, exact_n, rel, inside, needed, needed * visited / probes, visited, success, running, ways, problems, notes)


def verdict_answers(a: Analysis):
    if a.problems:
        return "error", "Die Rechenwege widersprechen sich: " + "; ".join(a.problems)
    what = "einfachen Wegen" if a.task == C.TASK_PATHS else "Knoten des Suchbaums"
    head = f"{a.label}: Aus {plural(a.probes, 'Sondierung', 'Sondierungen')} ({a.method}, Seed {a.seed}) ergibt sich eine Schätzung von {num_text(a.estimate)} {what}"
    if math.isfinite(a.half):
        head += f" mit Halbbreite {num_text(a.half)} im 95-Prozent-Intervall"
    if a.exact is not None:
        head += f"; die Wahrheit ist {num_text(a.exact)}, der Fehler {pct_text(a.rel_error)}"
    cv_text = de(a.cv, 2) if math.isfinite(a.cv) else ("nicht bestimmbar" if a.probes < 2 else "unbegrenzt")
    head += f". Der Variationskoeffizient der Gewichte ist {cv_text}"
    head += f"; für {pct_text(C.ERROR_TARGET)} Standardfehler brauchte man {plural(a.probes_needed, 'Sondierung', 'Sondierungen')}." if a.probes_needed else "."
    kind = "success"
    if a.exact_size is not None and a.task != C.TASK_PATHS:
        if a.exact_size < a.cost_needed:
            head += f" Der Baum hat nur {big_text(a.exact_size)} Knoten, die nötigen Sondierungen würden etwa {num_text(a.cost_needed)} Schritte kosten: Aufzählen ist billiger."
            kind = "warning"
        else:
            head += f" Die nötigen Sondierungen kosten etwa {num_text(a.cost_needed)} Schritte, das Aufzählen aller {big_text(a.exact_size)} Knoten mehr: Schätzen ist hier billiger."
    if a.rel_error is not None and a.rel_error > 0.25:
        head += " Die Schätzung liegt weit daneben."
        kind = "warning"
    return kind, head


# ----------------------------------------------------------------------------- Experiment 1: Fehler gegen Zahl der Sondierungen (N-Damen)
@functools.cache
def error_rows() -> dict:
    out = {}
    for n in C.EXP_QUEENS_NS:
        children, root = A.queens_children(n), ()
        exact = A.exact_size(children, root)
        rng = random.Random(C.EXP_SEED + n)
        pool = [A.knuth_probe(children, root, rng)[0] for _ in range(C.EXP_QUEENS_POOL)]
        rows = []
        for N in C.EXP_QUEENS_BLOCKS:
            errs = sorted(abs(m - exact) / exact for m in A.block_means(pool, N))
            rows.append({"N": N, "Blöcke": len(errs), "Mittel": statistics.fmean(errs), "Median": statistics.median(errs), "Quantil95": errs[min(len(errs) - 1, int(0.95 * len(errs)))]})
        xs = [math.log(r["N"]) for r in rows]
        ys = [math.log(r["Median"]) for r in rows]
        mx, my = statistics.fmean(xs), statistics.fmean(ys)
        slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
        out[n] = {"exakt": exact, "Lösungen": A.queens_solutions(n), "cv": A.mean_cv(pool)[1], "Reihe": rows, "Steigung": slope}
    return out


def verdict_error(res: dict):
    r10 = res[10]
    last = r10["Reihe"][-1]
    ok = all(-0.7 < r["Steigung"] < -0.3 for r in res.values())
    return ("success" if ok else "error"), (f"Der Schätzer ist unverzerrt, sein Fehler fällt wie 1/√N: die Steigung des Medianfehlers im doppeltlogarithmischen Bild ist {de(res[8]['Steigung'], 2)} (n = 8) und {de(r10['Steigung'], 2)} (n = 10). "
                                            f"Beim Suchbaum der zehn Damen ({big_text(r10['exakt'])} Knoten, Variationskoeffizient {de(r10['cv'], 2)}) liegt das Mittel aus {big_text(last['N'])} Sondierungen im Median {pct_text(last['Median'])} daneben, im 95-Prozent-Quantil {pct_text(last['Quantil95'])} (aus {big_text(last['Blöcke'])} Blöcken, also ungefähr).")


# ----------------------------------------------------------------------------- Experiment 2: Wege gegen die Wahrheit aus Stück 13
@functools.cache
def path_rows() -> list:
    rows = []
    for n in C.EXP_PATH_NS:
        rng = random.Random(C.EXP_SEED + 100 + n)
        nb = A.grid_neighbor_lists(n)
        ws = [A.path_probe(n, rng, True, nb)[0] for _ in range(C.EXP_PATH_PROBES)]
        est, cv = A.mean_cv(ws)
        half = A.confidence_halfwidth(ws)
        truth = C.KNOWN_PATHS[n]
        rows.append({"n": n, "Wahrheit": truth, "Schätzung": est, "Halb": half, "Verhältnis": est / truth, "im Intervall": abs(est - truth) <= half, "cv": cv, "nötig": A.probes_for_error(cv, C.ERROR_TARGET)})
    return rows


def verdict_paths(rows: list):
    last = rows[-1]
    inside = sum(r["im Intervall"] for r in rows)
    outside = [r["n"] for r in rows if not r["im Intervall"]]
    ok = all(0.25 < r["Verhältnis"] < 4 for r in rows)
    tail = f"; das Intervall verfehlt die Wahrheit in dieser Messung bei n = {', '.join(str(n) for n in outside)} (mögliche Ursache: schwere Ausläufer der Gewichte, bei denen wenige seltene, sehr große das Mittel tragen)" if outside else ""
    return ("success" if ok else "error"), (f"Der Schätzer trifft die exakten Zahlen aus Stück 13 mit {big_text(C.EXP_PATH_PROBES)} Sondierungen je Gitter ungefähr: von {len(rows)} Gittern liegt die Wahrheit in {inside} im 95-Prozent-Intervall{tail}. "
                                            f"Beim {last['n']}×{last['n']}-Gitter ({num_text(last['Wahrheit'])} Wege) beträgt das Verhältnis Schätzung zu Wahrheit {de(last['Verhältnis'], 3)}. "
                                            f"Der Variationskoeffizient wächst von {de(rows[0]['cv'], 2)} (n = {rows[0]['n']}) auf {de(last['cv'], 2)} (n = {last['n']}); für 5 Prozent Standardfehler braucht man dann {big_text(last['nötig'])} statt {big_text(rows[0]['nötig'])} Sondierungen.")


# ----------------------------------------------------------------------------- Experiment 3: Wissen einspeisen
@functools.cache
def check_rows() -> list:
    with_check = {r["n"]: r for r in path_rows()}
    rows = []
    for n in C.EXP_CHECK_NS:
        rng = random.Random(C.EXP_SEED + 200 + n)
        nb = A.grid_neighbor_lists(n)
        pool = [A.path_probe(n, rng, False, nb)[0] for _ in range(C.EXP_CHECK_POOL)]
        est, cv = A.mean_cv(pool)
        truth = C.KNOWN_PATHS[n]
        covered = []
        for i in range(0, C.EXP_CHECK_POOL - C.EXP_CHECK_BLOCK + 1, C.EXP_CHECK_BLOCK):
            block = pool[i:i + C.EXP_CHECK_BLOCK]
            covered.append(abs(statistics.fmean(block) - truth) <= A.confidence_halfwidth(block))
        rows.append({"n": n, "Erfolgsrate": sum(1 for w in pool if w) / len(pool), "cv_ohne": cv, "cv_mit": with_check[n]["cv"], "Faktor": cv / with_check[n]["cv"],
                     "Verhältnis ohne": est / truth, "Überdeckung": sum(covered) / len(covered), "Blöcke": len(covered)})
    return rows


def verdict_check(rows: list):
    first, last = rows[0], rows[-1]
    ok = all(r["Faktor"] > 1 for r in rows)
    return ("success" if ok else "error"), (f"Die Erreichbarkeitsprüfung (ein Schritt Vorausschau) macht jede Sondierung erfolgreich und senkt den Variationskoeffizienten beim {last['n']}×{last['n']}-Gitter von {de(last['cv_ohne'], 2)} auf {de(last['cv_mit'], 2)} (Faktor {de(last['Faktor'], 1)}); "
                                            f"ohne Prüfung enden {pct_text(1 - last['Erfolgsrate'])} der Sondierungen in einer Sackgasse. Das 95-Prozent-Intervall ohne Prüfung überdeckt die Wahrheit in {pct_text(min(r['Überdeckung'] for r in rows))} bis {pct_text(max(r['Überdeckung'] for r in rows))} "
                                            f"der Blöcke zu je {big_text(C.EXP_CHECK_BLOCK)} Sondierungen (n = {first['n']} bis {last['n']}).")


# ----------------------------------------------------------------------------- Experiment 4: Rucksack-Bäume
@functools.cache
def knapsack_rows() -> list:
    rows = []
    for n, seed, corr in C.EXP_KNAP_INSTANCES:
        items, cap = A.knapsack_instance(n, C.KNAPSACK_SEED_BASE + seed, corr)
        opt = A.knapsack_opt(items, cap)
        children = A.knapsack_children(items, cap, opt)
        size = A.exact_size(children, (0, 0, 0))
        rng = random.Random(C.EXP_SEED + 300 + n)
        pool, vis = [], 0
        for _ in range(C.EXP_KNAP_POOL):
            e, w, node, v = A.knuth_probe(children, (0, 0, 0), rng)
            pool.append(e)
            vis += v
        cv = A.mean_cv(pool)[1]
        errs = {N: statistics.median(abs(m - size) / size for m in A.block_means(pool, N)) for N in C.EXP_KNAP_BLOCKS}
        needed = A.probes_for_error(cv, C.ERROR_TARGET)
        rows.append({"n": n, "korreliert": corr, "Knoten": size, "voll": 2 ** (n + 1) - 1, "cv": cv, "Fehler": errs, "nötig": needed, "Besucht je Sondierung": vis / C.EXP_KNAP_POOL, "Aufzählen billiger": needed * vis / C.EXP_KNAP_POOL > size})
    return rows


def verdict_knapsack(rows: list):
    worst = max(rows, key=lambda r: r["cv"])
    cheaper = [r for r in rows if r["Aufzählen billiger"]]
    thin = [r for r in rows if r["cv"] < 1]
    n100, n1000 = C.EXP_KNAP_BLOCKS
    return "warning", (f"Bei Branch-and-Bound-Bäumen hängt der Schätzer an der Gestalt des Baums: beim Rucksack mit {worst['n']} Gegenständen ({'stark korreliert' if worst['korreliert'] else 'zufällig'}) hat der Baum {big_text(worst['Knoten'])} Knoten (voller Baum {big_text(worst['voll'])}), "
                       f"der Variationskoeffizient ist {de(worst['cv'], 1)}, der Median-Fehler nach {big_text(n100)} Sondierungen {pct_text(worst['Fehler'][n100])} und nach {big_text(n1000)} noch {pct_text(worst['Fehler'][n1000])}. "
                       f"Bei {len(cheaper)} von {len(rows)} Bäumen wäre das Aufzählen billiger als die nötigen Sondierungen; {len(thin)} Bäume sind dünn (Variationskoeffizient unter 1) und werden fast fehlerlos geschätzt.")


# ----------------------------------------------------------------------------- Experiment 5: Chen und Hashing
@functools.cache
def better_rows() -> dict:
    chen_rows = []
    for n in C.EXP_BETTER_NS:
        children = A.queens_children(n)
        size = A.exact_size(children, ())
        rng = random.Random(C.EXP_SEED + 400 + n)
        chen = [A.chen_probe(children, (), rng) for _ in range(C.EXP_BETTER_REPS)]
        chen_cost = statistics.fmean(c[1] for c in chen)
        knuth_one = [A.knuth_probe(children, (), rng) for _ in range(C.EXP_BETTER_REPS * 4)]
        visited = statistics.fmean(k[3] for k in knuth_one)
        k = max(1, round(chen_cost / visited))
        equal = [statistics.fmean(A.knuth_probe(children, (), rng)[0] for _ in range(k)) for _ in range(C.EXP_BETTER_REPS)]
        chen_cv = A.mean_cv([c[0] for c in chen])[1]
        knuth_cv = A.mean_cv([x[0] for x in knuth_one])[1]
        chen_rows.append({"n": n, "Knoten": size, "Chen cv": chen_cv, "Chen Kosten": chen_cost, "Knuth cv": knuth_cv, "Knuth Kosten": visited, "k": k, "Knuth gleicher Aufwand cv": A.mean_cv(equal)[1]})
    rows, cols = C.EXP_HASH_BOARD
    tilings, n_edges = A.domino_tilings(rows, cols)
    matrix = A.tiling_matrix(tilings, n_edges)
    rng = np.random.default_rng(C.EXP_SEED)
    hash_rows = []
    for m in C.EXP_HASH_MS:
        ests = [A.hash_estimate(matrix, m, rng) for _ in range(C.EXP_HASH_REPS)]
        mean, cv = A.mean_cv(ests)
        cell = len(tilings) / 2 ** m
        hash_rows.append({"m": m, "Zelle": cell, "Mittel": mean, "cv": cv, "1/Wurzel": 1 / math.sqrt(cell), "im Faktor 1,5": sum(1 for e in ests if len(tilings) / 1.5 <= e <= len(tilings) * 1.5) / len(ests)})
    return {"chen": chen_rows, "hash": hash_rows, "Parkettierungen": len(tilings), "Kanten": n_edges, "Brett": f"{rows}×{cols}"}


def verdict_better(res: dict):
    c10 = next(r for r in res["chen"] if r["n"] == 10)
    h = res["hash"]
    worse = sum(1 for r in res["chen"] if r["Chen cv"] > r["Knuth gleicher Aufwand cv"])
    last = h[-1]
    return "success", (f"Chens Schichtung senkt die Streuung je Sondierung (n = 10: Variationskoeffizient {de(c10['Chen cv'], 2)} gegen {de(c10['Knuth cv'], 2)}), kostet aber {de(c10['Chen Kosten'], 0)} statt {de(c10['Knuth Kosten'], 1)} Kinderlisten je Sondierung; "
                       f"bei gleichem Aufwand ist Knuth mit {c10['k']} Sondierungen bei {worse} von {len(res['chen'])} Bäumen besser (n = 10: {de(c10['Knuth gleicher Aufwand cv'], 2)}). "
                       f"Beim Hashing auf den {big_text(res['Parkettierungen'])} Parkettierungen des {res['Brett']}-Bretts ist das Mittel der Schätzung 2^m · Zelle unverzerrt, und ihr Variationskoeffizient folgt 1/√Zellgröße (bei kleinen m liegt er darunter): bei m = {last['m']} (Zelle im Mittel {de(last['Zelle'], 1)}) {de(last['cv'], 3)} gegen {de(last['1/Wurzel'], 3)}. "
                       "Das Orakel zählt dabei alle Lösungen auf; der Nutzen des Hashings liegt dort, wo ein Löser die Zelle ohne Aufzählen findet.")


# ----------------------------------------------------------------------------- Spielwiese: eigener Baum
def play_tree(text: str) -> dict:
    try:
        children, root, n = A.parse_tree(text)
    except ValueError as err:
        return {"error": str(err)}
    dist = A.enumerate_probes(children, root)
    mean, var = A.estimator_moments(dist)
    outcomes: dict = {}
    for p, size, _ in dist:
        outcomes[size] = outcomes.get(size, Fraction(0)) + p
    cv = math.sqrt(var) / float(mean) if mean else 0.0
    needed = A.probes_for_error(cv, C.ERROR_TARGET) if cv > 0 else 1
    return {"Knoten": n, "Blätter": len(dist), "Erwartung": mean, "Varianz": var, "cv": cv, "nötig": needed, "Ergebnisse": sorted(outcomes.items())}


def verdict_play(res: dict):
    if "error" in res:
        return "warning", res["error"]
    outs = ", ".join(f"{s} mit Wahrscheinlichkeit {p.numerator}/{p.denominator}" if p.denominator != 1 else f"{s}" for s, p in res["Ergebnisse"])
    unbiased = res["Erwartung"] == res["Knoten"]
    return ("success" if unbiased else "error"), (f"Der Baum hat {res['Knoten']} Knoten und {plural(res['Blätter'], 'Blatt', 'Blätter')}. Jede Sondierung gibt {outs}: die Erwartung ist {res['Erwartung']}, die Varianz {res['Varianz']}, "
                                                  f"der Variationskoeffizient {de(res['cv'], 2)}; für 5 Prozent Standardfehler reichen {plural(res['nötig'], 'Sondierung', 'Sondierungen')}.")
