"""Urteilstexte (Schicht 3): die Texte, die die App zeigt, mit genauem Wortlaut für alle Voreinstellungen und Experimente, damit jede Zahl darin geprüft ist."""

import ksc_constants as C
import ksc_evaluation as ev

S = ev.Settings


def answer(name):
    return ev.verdict_answers(ev.analyse(S(**C.PRESETS[name])))


def test_answer_standard_case_exact():
    assert answer("Standardfall: N-Damen n = 10") == ("success",
        "N-Damen, n = 10: Aus 10.000 Sondierungen (Knuth, Seed 7) ergibt sich eine Schätzung von 35.792 Knoten des Suchbaums mit Halbbreite 458 im 95-Prozent-Intervall; die Wahrheit ist 35.539, der Fehler 0,7 %. "
        "Der Variationskoeffizient der Gewichte ist 0,65; für 5,0 % Standardfehler brauchte man 171 Sondierungen. Die nötigen Sondierungen kosten etwa 1.496 Schritte, das Aufzählen aller 35.539 Knoten mehr: Schätzen ist hier billiger.")


def test_answer_paths_exact():
    assert answer("Wege im 8×8-Gitter mit Erreichbarkeitsprüfung") == ("success",
        "Wege im 8×8-Gitter: Aus 1.000 Sondierungen (Knuth mit Erreichbarkeitsprüfung, Seed 7) ergibt sich eine Schätzung von 714.220.393.223 einfachen Wegen mit Halbbreite 167.082.114.817 im 95-Prozent-Intervall; die Wahrheit ist 789.360.053.252, der Fehler 9,5 %. "
        "Der Variationskoeffizient der Gewichte ist 3,77; für 5,0 % Standardfehler brauchte man 5.693 Sondierungen.")
    assert answer("Wege im 8×8-Gitter ohne Prüfung") == ("warning",
        "Wege im 8×8-Gitter: Aus 10.000 Sondierungen (Knuth, Seed 7) ergibt sich eine Schätzung von 1.042.690.361.410 einfachen Wegen mit Halbbreite 369.673.155.991 im 95-Prozent-Intervall; die Wahrheit ist 789.360.053.252, der Fehler 32,1 %. "
        "Der Variationskoeffizient der Gewichte ist 18,09; für 5,0 % Standardfehler brauchte man 130.867 Sondierungen. Die Schätzung liegt weit daneben.")
    assert answer("Wege im 10×10-Gitter: 4,1·10¹⁹") == ("success",
        "Wege im 10×10-Gitter: Aus 1.000 Sondierungen (Knuth mit Erreichbarkeitsprüfung, Seed 7) ergibt sich eine Schätzung von 3,52·10¹⁹ einfachen Wegen mit Halbbreite 1,35·10¹⁹ im 95-Prozent-Intervall; die Wahrheit ist 4,10·10¹⁹, der Fehler 14,3 %. "
        "Der Variationskoeffizient der Gewichte ist 6,20; für 5,0 % Standardfehler brauchte man 15.389 Sondierungen.")


def test_answer_knapsack_and_chen_exact():
    assert answer("Rucksack-Baum n = 24: der schwierige Fall") == ("warning",
        "Rucksack-Baum mit 24 Gegenständen (stark korreliert): Aus 10.000 Sondierungen (Knuth, Seed 3) ergibt sich eine Schätzung von 9.397 Knoten des Suchbaums mit Halbbreite 4.226 im 95-Prozent-Intervall; die Wahrheit ist 7.496, der Fehler 25,4 %. "
        "Der Variationskoeffizient der Gewichte ist 22,95; für 5,0 % Standardfehler brauchte man 210.607 Sondierungen. Der Baum hat nur 7.496 Knoten, die nötigen Sondierungen würden etwa 5.126.659 Schritte kosten: Aufzählen ist billiger. Die Schätzung liegt weit daneben.")
    assert answer("N-Damen n = 10 mit Chens Schichtung") == ("success",
        "N-Damen, n = 10: Aus 1.000 Sondierungen (Chen-Schichtung, Seed 7) ergibt sich eine Schätzung von 34.720 Knoten des Suchbaums mit Halbbreite 906 im 95-Prozent-Intervall; die Wahrheit ist 35.539, der Fehler 2,3 %. "
        "Der Variationskoeffizient der Gewichte ist 0,42; für 5,0 % Standardfehler brauchte man 71 Sondierungen. Die nötigen Sondierungen kosten etwa 5.106 Schritte, das Aufzählen aller 35.539 Knoten mehr: Schätzen ist hier billiger.")


def test_answer_single_probe_and_error():
    a = ev.analyse(S(C.TASK_QUEENS, 6, 1, "Knuth", 1))
    kind, text = ev.verdict_answers(a)
    assert kind == "success" and "Variationskoeffizient der Gewichte ist nicht bestimmbar." in text and "Halbbreite" not in text and "Sondierungen für" not in text
    a.problems.append("zwei Wege weichen ab")
    assert ev.verdict_answers(a) == ("error", "Die Rechenwege widersprechen sich: zwei Wege weichen ab")


def test_ways_table_of_the_standard_case():
    a = ev.analyse(S(**C.PRESETS["Standardfall: N-Damen n = 10"]))
    assert [(w["Größe"], w["Wert"], w["Prüfweg"], w["Prüfwert"], w["Prüfung"]) for w in a.ways] == [
        ("Knotenzahl des Suchbaums", "35.792", "Aufzählen durch Tiefensuche", "35.539", "Wahrheit im Intervall"),
        ("Zahl der Lösungen", "714", "Aufzählen durch Tiefensuche", "724", "Wahrheit im Intervall"),
        ("Halbbreite des 95-Prozent-Intervalls", "458", "Normalnäherung (1,96 · Standardfehler)", "", "gilt nur bei endlicher, nicht zu schiefer Streuung"),
        ("Variationskoeffizient der Gewichte", "0,65", "Streuung der Einzelschätzungen geteilt durch ihr Mittel", "", ""),
        ("Sondierungen für 5,0 % Standardfehler", "171", "Variationskoeffizient zum Quadrat durch (0,05)²", "", ""),
        ("Aufwand dieses Laufs", "87.504 besuchte Knoten", "Summe über alle Sondierungen", "", ""),
        ("Aufwand für 5,0 % Standardfehler: Schätzen gegen Aufzählen", "1.496 gegen 35.539", "nötige Sondierungen mal Aufwand je Sondierung gegen Baumgröße", "", "Schätzen ist billiger (Faktor 23,8)")]
    b = ev.analyse(S(C.TASK_PATHS, 4, 100, "Knuth", 1))
    assert [(w["Größe"], w["Prüfweg"], w["Prüfwert"], w["Prüfung"]) for w in b.ways[:2]] == [
        ("Zahl der einfachen Wege", "Stück 13 (Frontier-Diagramm)", "184", "Wahrheit im Intervall"), ("Zahl der einfachen Wege", "Rückverfolgung aller Wege", "184", "gleich")]


def test_error_verdict_exact():
    assert ev.verdict_error(ev.error_rows()) == ("success",
        "Der Schätzer ist unverzerrt, sein Fehler fällt wie 1/√N: die Steigung des Medianfehlers im doppeltlogarithmischen Bild ist −0,45 (n = 8) und −0,48 (n = 10). "
        "Beim Suchbaum der zehn Damen (35.539 Knoten, Variationskoeffizient 0,65) liegt das Mittel aus 3.000 Sondierungen im Median 1,1 % daneben, im 95-Prozent-Quantil 2,2 %.")


def test_paths_verdict_exact():
    assert ev.verdict_paths(ev.path_rows()) == ("success",
        "Der Schätzer trifft die exakten Zahlen aus Stück 13 mit 600 Sondierungen je Gitter ungefähr: von 7 Gittern liegt die Wahrheit in 5 im 95-Prozent-Intervall; das Intervall verfehlt die Wahrheit bei n = 8, 10 (schwere Ausläufer der Gewichte: wenige seltene, sehr große tragen das Mittel). "
        "Beim 10×10-Gitter (4,10·10¹⁹ Wege) beträgt das Verhältnis Schätzung zu Wahrheit 0,606. Der Variationskoeffizient wächst von 0,70 (n = 4) auf 5,36 (n = 10); für 5 Prozent Standardfehler braucht man dann 11.505 statt 198 Sondierungen.")


def test_check_verdict_exact():
    assert ev.verdict_check(ev.check_rows()) == ("success",
        "Die Erreichbarkeitsprüfung (ein Schritt Vorausschau) macht jede Sondierung erfolgreich und senkt den Variationskoeffizienten beim 8×8-Gitter von 19,04 auf 3,36 (Faktor 5,7); ohne Prüfung enden 80,4 % der Sondierungen in einer Sackgasse. "
        "Das 95-Prozent-Intervall ohne Prüfung überdeckt die Wahrheit in 86,7 % bis 100,0 % der Blöcke zu je 1.000 Sondierungen (n = 4 bis 8).")


def test_knapsack_verdict_exact():
    assert ev.verdict_knapsack(ev.knapsack_rows()) == ("warning",
        "Bei Branch-and-Bound-Bäumen hängt der Schätzer an der Gestalt des Baums: beim Rucksack mit 24 Gegenständen (stark korreliert) hat der Baum 7.496 Knoten (voller Baum 33.554.431), der Variationskoeffizient ist 24,9, der Median-Fehler nach 100 Sondierungen 77,4 % und nach 1.000 noch 56,6 %. "
        "Bei 4 von 5 Bäumen wäre das Aufzählen billiger als die nötigen Sondierungen; 3 Bäume sind dünn (Variationskoeffizient unter 1) und werden fast fehlerlos geschätzt.")


def test_better_verdict_exact():
    assert ev.verdict_better(ev.better_rows()) == ("success",
        "Chens Schichtung senkt die Streuung je Sondierung (n = 10: Variationskoeffizient 0,37 gegen 0,67), kostet aber 72 statt 8,8 Kinderlisten je Sondierung; bei gleichem Aufwand ist Knuth mit 8 Sondierungen bei 3 von 3 Bäumen besser (n = 10: 0,25). "
        "Beim Hashing auf den 6.728 Parkettierungen des 6×6-Bretts ist das Mittel der Schätzung 2^m · Zelle unverzerrt, und ihr Variationskoeffizient folgt 1/√Zellgröße: bei m = 8 (Zelle im Mittel 26,3) 0,199 gegen 0,195. "
        "Das Orakel zählt dabei alle Lösungen auf; der Nutzen des Hashings liegt dort, wo ein Löser die Zelle ohne Aufzählen findet.")


def test_play_verdict_exact():
    assert ev.verdict_play(ev.play_tree(C.PLAY_TREE_DEFAULT)) == ("success",
        "Der Baum hat 7 Knoten und 4 Blätter. Jede Sondierung gibt 5 mit Wahrscheinlichkeit 1/2, 9 mit Wahrscheinlichkeit 1/2: die Erwartung ist 7, die Varianz 4, der Variationskoeffizient 0,29; für 5 Prozent Standardfehler reichen 33 Sondierungen.")
    assert ev.verdict_play(ev.play_tree("((()())(()()))"))[1].startswith("Der Baum hat 7 Knoten und 4 Blätter. Jede Sondierung gibt 7: die Erwartung ist 7, die Varianz 0")


def test_verdicts_turn_into_errors_when_a_check_fails():
    rows = [dict(r) for r in ev.path_rows()]
    rows[0]["Verhältnis"] = 9.0
    assert ev.verdict_paths(rows)[0] == "error"
    res = {n: {**r, "Steigung": 0.3} for n, r in ev.error_rows().items()}
    assert ev.verdict_error(res)[0] == "error"
    chk = [dict(r) for r in ev.check_rows()]
    chk[0]["Faktor"] = 0.5
    assert ev.verdict_check(chk)[0] == "error"
    bad = ev.play_tree(C.PLAY_TREE_DEFAULT) | {"Erwartung": 8}
    assert ev.verdict_play(bad)[0] == "error"
