# Knuth-Schätzer – wenn Zählen zu schwer ist, schätzen – Streamlit-Demo

**[→ Demo live ausprobieren](https://sebastianhanisch-knuth-schaetzer-demo.streamlit.app/)**

Stück 15 von 16 der Reihe **„Abzählen und erzeugende Funktionen“** in der „Konzepte“-Reihe für die Website „Sebastian Hanisch – Operations Research und Machine Learning“ (die Linie wird erst vollständig veröffentlicht; Stück 15 war als gelb markiert und wurde nach Stück 14 zum Bauen entschieden). Vorgänger sind `aufzaehlen-rekursion-demo` (Stück 1), `rationale-ef-demo` (Stück 2), `symbolische-methode-demo` (Stück 3), `semiring-rekursion-demo` (Stück 4), `multimengen-partitionen-demo` (Stück 5), `beschriftete-strukturen-demo` (Stück 6), `siebformel-demo` (Stück 7), `zaehlen-nach-parameter-demo` (Stück 8), `asymptotik-demo` (Stück 9), `gleichverteilt-ziehen-demo` (Stück 10), `burnside-polya-demo` (Stück 11), `isomorphieausschluss-demo` (Stück 12), `frontier-diagramm-demo` (Stück 13) und `tutte-polynom-demo` (Stück 14); die letzten haben **exakt gezählt**. Diese Demo **schätzt**, wenn das nicht mehr zu bezahlen ist: ein **Zufallsabstieg** durch den Suchbaum (eine **Sondierung**) multipliziert die Zahl der Wahlmöglichkeiten, und das Gewicht hat als Erwartung genau die gesuchte Zahl (**Knuth 1975** für die Größe eines Suchbaums, **Rosenbluth und Rosenbluth 1955** für selbstvermeidende Wege). Wie genau das Mittel ist, sagt der **Variationskoeffizient** des Gewichts; das Diagramm aus Stück 13 liefert die **Wahrheit**, an der man den Schätzer prüft.

## Warum dieses Problem

Wer die Größe eines Suchbaums oder die Zahl der Lösungen nicht aufzählen kann (Branch-and-Bound, Wege, Parkettierungen), braucht eine Schätzung mit einer Aussage, wie viel sie wert ist. Der Schätzer ist einfach und unverzerrt; sein Preis ist die **Streuung**. Die Demo zeigt, wo er glänzt (ausgeglichene Bäume: die zehn Damen, Wege im Gitter mit Vorausschau), wo er versagt (unausgeglichene Bäume, kleine Bäume) und was ihm hilft (Vorwissen, Schichtung, Hashing).

## Befunde und Korrekturen gegenüber dem Plan

- **Hook bestätigt, aber anders gewichtet:** Bei ausgeglichenen Bäumen funktioniert der Schätzer gut (zehn Damen, 35.539 Knoten: Variationskoeffizient 0,65, Median-Fehler etwa 1 Prozent nach 3.000 Sondierungen; die App zeigt 1,1 aus nur 10 Blöcken, mit mehr Blöcken liegt der Wert eher bei 0,7); bei **unausgeglichenen** Bäumen bricht er (ein Rucksack mit 24 Gegenständen, 7.496 Knoten, Seed 3: Variationskoeffizient etwa 24,5, Median-Fehler gut 50 Prozent nach 1.000 Sondierungen; die App zeigt aus einer Probe 24,9 und 56,6; andere Instanzen sind weniger schief); bei **kleinen** Bäumen ist Aufzählen billiger.
- **Die Intervalle halten nicht immer:** Mit 600 Sondierungen verfehlt das 95-Prozent-Intervall die Wahrheit in dieser Messung bei den Wegen im 8×8- und 10×10-Gitter (Verhältnis Schätzung zu Wahrheit 0,731 und 0,606). Wiederholungen mit anderen Seeds (unabhängige Prüfung) geben bis 8×8 eine Überdeckung von etwa 95 Prozent, bei 9×9 und 10×10 von etwa 88 bis 90 Prozent: das Verfehlen bei 8×8 ist ein Zufallstreffer, echte Unterdeckung zeigt sich erst bei den größten Gittern. Als Ursache passen schwere Ausläufer der Gewichte (wenige seltene, sehr große tragen das Mittel); gesondert nachgewiesen sind sie nicht. Phase 0 hatte mit 8.000 Sondierungen für n = 10 noch 0,964 gemessen.
- **Phase 0 hat den Aufwand von Chens Verfahren zu niedrig gezählt:** Es zählte nur die Kinderlisten der Vertreter (14 bis 21 je Sondierung); richtig gezählt sind es 40 bis 72 (alle Kinder, deren Typ man braucht). Dann ist Chens Streuung je Sondierung kleiner (Variationskoeffizient 0,37 gegen 0,67 bei n = 10), aber Knuth mit gleichem Aufwand (acht Sondierungen) ist **besser** (0,25). Der Plan sagte „bescheiden besser“; die App sagt „bei gleichem Aufwand schlechter“.
- **Der Aufwandsvergleich muss die nötige Zahl der Sondierungen nehmen, nicht die gewählte:** Beim Baum der zehn Damen kosten 10.000 Sondierungen 87.504 Knoten (mehr als die 35.539 des Baums), aber für 5 Prozent Standardfehler reichen 171 Sondierungen mit 1.496 Schritten (Schätzen ist 23,8-mal billiger; 5 Prozent Standardfehler entsprechen beim 95-Prozent-Intervall etwa ±10 Prozent, und die Zahl der Sondierungen folgt aus dem Variationskoeffizienten der Probe eines Seeds). Beim Rucksack-Baum mit 7.496 Knoten sind es 5.126.659 Schritte: Aufzählen ist billiger.
- **Hashing mit dem 6×6-Brett statt 6×8:** Das Brett mit 6.728 Parkettierungen rechnet in der App in Sekunden (6×8 mit 167.089 braucht für die Matrixprodukte etwa zehnmal so lange; Phase 0 hatte es gemessen: Variationskoeffizient bei Zellgröße 163: 0,079 gegen 0,078 für 1/√Zellgröße).
- **Eigene Fehler im Bau (nicht in der Messung):** (1) Mit einer einzigen Sondierung war der Variationskoeffizient 0 und die nötige Zahl 0: Division durch null im Aufwandsvergleich; der Randfalltest fand es, jetzt „nicht bestimmbar“. (2) Zwei Handwerte in Tests waren falsch (der Rucksack-Baum des Handbeispiels hat 6 Knoten, nicht 4); der Code war richtig. (3) Der erste Test von Chens Verfahren prüfte einen Baum, dessen Typen alle Knoten trennen (kein Zufall übrig): ersetzt durch einen Baum, in dem zwei Typen zusammenfallen (Schätzung 7 oder 11, Erwartung 9). (4) Drei Preset-Texte sagten „wenige Prozent“, wo der Fehler 9,5 und 14,3 Prozent beträgt. (5) „Chen (geschichtet)“ in Klammern im Urteilstext: jetzt „Chen-Schichtung“.
- **Präfix `ksc_`, Port 9328; Repo `knuth-schaetzer-demo`** (`schaetzen-demo` ist die kausale Demo).

## Modell

**Schätzer (`knuth_probe`):** Von der Wurzel aus wird an jedem Knoten ein Kind gleichverteilt gewählt; das Gewicht ist das Produkt der Kinderzahlen auf dem Weg, die Schätzung der Knotenzahl die Summe der Gewichte aller besuchten Knoten (Wurzel: 1). **Wege (`path_probe`):** Gewicht = Produkt der Zahl der Möglichkeiten je Schritt beim Erreichen der Ecke, 0 in einer Sackgasse; mit Erreichbarkeitsprüfung zählen nur Schritte, von denen das Ziel noch erreichbar ist (Breitensuche).

**Aufgaben:** Suchbaum der N-Damen (Knotenzahl und Zahl der Lösungen), einfache Wege von Ecke zu Ecke im n×n-Gitter, Branch-and-Bound-Baum eines Rucksacks mit **festem Zielwert** (dem Optimum, bestimmt durch Tabellierung): Kinder sind „nehmen“ und „weglassen“, gestrichen, wenn es nicht passt oder die Schranke des fraktionalen Rucksacks unter dem Zielwert liegt. **Wahrheit:** Tiefensuche (Bäume), Zahlen aus Stück 13 (Wege, bis n = 5 durch Rückverfolgung geprüft), Aufzählen (Hashing).

**Verbesserungen:** `chen_probe` (je Ebene bleibt je Typ aus Tiefe und Kinderzahl ein zufälliger Vertreter mit der Summe der Gewichte); `hash_estimate` (m zufällige XOR-Bedingungen über die Kanten einer Parkettierung, Schätzung 2^m mal Zahl der erfüllenden Parkettierungen). **Exakte Verteilung:** `enumerate_probes` zählt alle Sondierungen eines kleinen Baums mit Wahrscheinlichkeiten in Brüchen auf und gibt Erwartung und Varianz exakt.

## Methodik

- **Prüfungen in der App:** Schätzung gegen die Wahrheit mit 95-Prozent-Intervall (Normalnäherung; das Intervall verfehlt die Wahrheit in etwa 5 von 100 Fällen, bei schweren Ausläufern öfter); bei den Wegen bis n = 5 zusätzlich Rückverfolgung gegen die Zahl aus Stück 13; bei den Damen auch die Zahl der Lösungen. Ein Widerspruch zwischen den exakten Wegen ist ein Fehler, eine verfehlte Schätzung nicht.
- **Eingabe:** Aufgabe (vier), Größe (je Aufgabe geklemmt), Zahl der Sondierungen (10 bis 30.000; mit Erreichbarkeitsprüfung höchstens 1.000, mit Chen höchstens 3.000), Verfahren (nicht passende fallen mit Hinweis auf Knuth zurück), Seed. Die Adresszeile spiegelt die Einstellung.
- **Fünf Experimente:** (1) Fehler gegen Zahl der Sondierungen bei den Damen, (2) Wege gegen die Wahrheit aus Stück 13, (3) Erreichbarkeitsprüfung und Überdeckung, (4) Rucksack-Bäume, (5) Chen und Hashing. Dazu eine Spielwiese: ein eigener Baum in Klammerschreibweise mit exakter Erwartung und Varianz. Alle Zufallsziehungen laufen mit festem Seed (20261102 in den Experimenten); Fehlerkurven stammen aus Blöcken einer langen Folge, nicht aus unabhängigen Wiederholungen.

## Befunde (gemessen, keine Behauptungen)

Jede Zahl steht in `tests/test_claims.py`, `tests/test_verdicts.py`, `tests/test_algorithm.py` oder `tests/test_oracle_ksc.py`. Zeiten stehen in keinem Test.

| Frage | Befund |
|---|---|
| Handbaum ((()()())(())) | 7 Knoten, 4 Blätter; Sondierung gibt 9 mit Wahrscheinlichkeit 1/2 (über das Kind mit drei Blättern: 3 · 1/6) oder 5 mit 1/2; Erwartung 7, Varianz 4, Variationskoeffizient 0,29, 33 Sondierungen für 5 Prozent |
| N-Damen-Suchbaum: n, Knoten, Lösungen | 6: 153, 4; 8: 2.057, 92; 9: 8.394, 352; 10: 35.539, 724 |
| Fehler des Mittels (Median, 95-Prozent-Quantil) bei N = 10 / 100 / 1.000 / 3.000 Sondierungen | n = 8: 11,1 % (32,9 %) / 3,4 % (9,9 %) / 1,3 % (3,8 %) / 0,85 % (2,4 %), Steigung −0,45; n = 10: 13,6 % (39,6 %) / 4,6 % (13,2 %) / 1,2 % (4,1 %) / 1,1 % (2,2 %), Steigung −0,48; Variationskoeffizient 0,52 und 0,65 (eine Realisierung: die Werte bei 3.000 Sondierungen stammen aus nur 10 Blöcken und sind ungefähr, die Steigungen streuen um die theoretische −0,5) |
| Standardfall (zehn Damen, Seed 7, 10.000 Sondierungen) | Schätzung 35.792 (Wahrheit 35.539, Fehler 0,7 %), 714 Lösungen (Wahrheit 724), Halbbreite 458, 171 Sondierungen für 5 Prozent, Aufwand dafür 1.496 gegen 35.539 Knoten (Faktor 23,8) |
| Wege im Gitter mit Erreichbarkeitsprüfung, 600 Sondierungen: Verhältnis Schätzung zu Wahrheit (Variationskoeffizient, Sondierungen für 5 %) | n = 4: 0,977 (0,70, 198); 5: 1,043 (1,19, 566); 6: 0,958 (1,70, 1.155); 7: 0,971 (2,35, 2.207); 8: 0,731 (3,36, 4.524); 9: 0,804 (4,29, 7.377); 10: 0,606 (5,36, 11.505); das Intervall verfehlt n = 8 und 10 |
| Ohne Prüfung (30.000 Sondierungen): Erfolgsrate, Variationskoeffizient ohne gegen mit | n = 4: 56,7 %, 1,48 gegen 0,70; 5: 43,6 %, 3,00 gegen 1,19; 6: 33,6 %, 5,66 gegen 1,70; 7: 25,2 %, 10,41 gegen 2,35; 8: 19,6 %, 19,04 gegen 3,36 (Faktor 5,7) |
| Überdeckung des 95-Prozent-Intervalls ohne Prüfung, 30 Blöcke zu 1.000 Sondierungen | n = 4 bis 8: 96,7 %, 100 %, 96,7 %, 96,7 %, 86,7 % |
| Voreinstellungen Wege (Seed 7) | 8×8 mit Prüfung, 1.000 Sondierungen: 714.220.393.223 (Wahrheit 789.360.053.252, Fehler 9,5 %, Variationskoeffizient 3,77); 8×8 ohne Prüfung, 10.000: 1.042.690.361.410 (Fehler 32,1 %, 20,2 % Erfolgsrate, Variationskoeffizient 18,09); 10×10 mit Prüfung, 1.000: 3,52·10¹⁹ (Wahrheit 4,10·10¹⁹, Fehler 14,3 %, Variationskoeffizient 6,20) |
| Rucksack-Bäume (Gegenstände, Knoten, Variationskoeffizient, Median-Fehler nach 100 / 1.000 Sondierungen) | korreliert 16: 441, 5,03, 35 % / 6,8 %; 20: 35, 0,23, 1,4 % / 0,1 %; 24: 7.496 (voller Baum 33.554.431), 24,95, 77,4 % / 56,6 %; 28: 29, 0,00, 0 % / 0 %; zufällig 24: 39, 0,31, 1,7 % / 0,6 %; Preset (Seed 3, 10.000 Sondierungen): 9.397 gegen 7.496, Variationskoeffizient 22,95, 210.607 Sondierungen für 5 Prozent mit 5.126.659 Schritten |
| Chen gegen Knuth (n = 8, 9, 10) | Variationskoeffizient je Sondierung 0,30, 0,38, 0,37 gegen 0,52, 0,61, 0,67; Kinderlisten je Sondierung 40, 55, 72 gegen 7,2, 8,0, 8,8; Knuth mit gleichem Aufwand (6, 7, 8 Sondierungen): 0,22, 0,22, 0,25 |
| Hashing, 6×6-Brett, 6.728 Parkettierungen, 60 Kanten, 200 Wiederholungen | m = 0 bis 8: Mittel 6.728, 6.725, 6.715, 6.760, 6.712, 6.697, 6.732, 6.708, 6.742; Variationskoeffizient 0,000, 0,009, 0,024, 0,037, 0,042, 0,060, 0,086, 0,147, 0,199 gegen 1/√Zelle 0,012, 0,017, 0,024, 0,034, 0,049, 0,069, 0,098, 0,138, 0,195 (bei kleinem m liegt der Variationskoeffizient darunter, und 200 Wiederholungen streuen bei diskreten Schätzwerten stark) |
| Wahrheit der Wege (Stück 13) | n = 2 bis 10: 2, 12, 184, 8.512, 1.262.816, 575.780.564, 789.360.053.252, 3.266.598.486.981.642, 41.044.208.702.632.496.804; bis n = 5 durch Rückverfolgung gleich |
| Handinstanzen der Wege | 2×2: zwei Wege, jede Sondierung wiegt 2 (Erwartung 2); 3×3 und 4×4: Erwartung über alle Sondierungen exakt 12 und 184, mit und ohne Prüfung; mit Prüfung kleinere Varianz |
| Phase 0 (andere Seeds, nicht in der App neu gerechnet) | 6×8-Brett mit 167.089 Parkettierungen: Variationskoeffizient 0,079 bei Zellgröße 163 (1/√163 = 0,078); Wege im 10×10-Gitter mit 8.000 Sondierungen: Verhältnis 0,964; Überdeckung bei 2.000 Sondierungen und n = 5 bis 8: 0,94, 0,97, 0,97, 0,96 |

## Ehrliche Grenzen

- **Literaturwerte aus dem Gedächtnis:** Knuth 1975, Rosenbluth und Rosenbluth 1955, Chen 1992, Stockmeyer 1983, Chakraborty, Meel und Vardi 2013 wurden nicht an einer Quelle gelesen; die Zahlen der Wege kommen aus Stück 13 (Diagramm), unabhängig bis n = 5 durch Rückverfolgung bestätigt.
- **Fester Baum:** Der Rucksack-Baum hat einen **festen** Zielwert (das Optimum). Der Baum eines Lösers ändert sich mit der besten bekannten Lösung; ihn zu schätzen ist schwerer und hier nicht gebaut.
- **Hashing mit Orakel:** Die Zelle wird durch Aufzählen aller Parkettierungen gefunden. Ohne Löser sieht man nur die Statistik, nicht den Nutzen; eine (ε, δ)-Garantie ist nicht gerechnet.
- **Kleine Stichproben:** Die Fehlerkurven stammen aus Blöcken einer langen Folge (10 bis 3.000 Blöcke je N), die Überdeckungen aus 30 Blöcken: ±5 Prozentpunkte Rauschen. Der Variationskoeffizient aus der Probe ist bei schweren Ausläufern selbst unsicher. Ein Seed ist ein Einzelwert: bei 1.000 Sondierungen mit Prüfung liegt der Fehler je nach Seed bei 8×8 zwischen 1 und 19 Prozent (Median 7,6), bei 10×10 zwischen 3 und 45 Prozent (Median 14,6); die Voreinstellungen (Seed 7: 9,5 und 14,3) liegen dabei im typischen Bereich.
- **Aufwand als besuchte Knoten, Schritte und Kinderlisten**, nicht als Zeit; der erste Aufruf braucht etwa eine halbe Minute, weil die Experimente einmal rechnen (danach zwischengespeichert).
- **Browser:** Seitentext, Zahlen, Diagrammbreiten, Preset-Klick im Browser geprüft; Handy-Breite nicht.
- Alles gerechnet, keine echten Daten.

## Verifikation

- **Kern:** Handbaum (alle Sondierungen mit Brüchen: Erwartung 7, Varianz 4), vollständiger Baum (Varianz 0), Ketten, Blattbaum; Zufallsfolge mit festen Antworten gegen die Handrechnung; Parkettierungen gegen bekannte Zahlen; Wege gegen Rückverfolgung; Rucksack-Optimum gegen Brute Force; Rucksack-Baum von Hand (6 Knoten).
- **Orakel:** **exakte Unverzerrtheit** auf 40 zufälligen Bäumen (Erwartung aller Sondierungen in Brüchen gleich der Knotenzahl), des Lösungsschätzers der Damen und des Wege-Schätzers (3×3, 4×4, mit und ohne Prüfung); des Hash-Schätzers über **alle** Bedingungen eines kleinen Bretts; Suchbaumgrößen der Damen gegen das Zählen aller Präfixe mit `itertools`; Lösungen gegen Permutationen; Schätzungen gegen die Wahrheit auf festen Seeds innerhalb 3,5 Standardfehlern.
- **Eigenschaften:** Gewicht gleich Kehrwert der Wahrscheinlichkeit jeder Sondierung; Wahrscheinlichkeiten summieren sich zu 1, jedes Blatt kommt einmal vor; Fehler fällt mit der Zahl der Sondierungen (Faktor 2 bis 5 je Zehnerschritt); Erreichbarkeitsprüfung entfernt Sackgassen und senkt den Variationskoeffizienten; dieser wächst mit der Gittergröße; nötige Sondierungen wachsen mit dem Quadrat des Variationskoeffizienten; Hash-Streuung folgt 1/√Zellgröße; Analysen sind bei festem Seed deterministisch.
- **Randfälle:** Größen und Verfahren außerhalb der Aufgabe (Klemmen, Rückfall mit Hinweis), Obergrenzen je Verfahren, eine einzige Sondierung (kein Intervall, Variationskoeffizient nicht bestimmbar), Baum über dem Limit (keine Wahrheit, trotzdem Schätzung), Ketten, ein Knoten, Bäume mit Müll, Formatierung.
- **Urteilstexte:** genauer Wortlaut für alle Voreinstellungen und Experimente, Fehlerfälle.
- **Oberfläche:** AppTest-Rauchtest (jeder Button, jeder Regler an Minimum und Maximum), jedes Preset, jede Aufgabe mit jedem Verfahren, Permalink mit Müll, Spielwiese (auch mit Fehler), PDF für jede Aufgabe und jedes Verfahren, eindeutige Diagrammschlüssel; Footer-Test; Layout-Test.
- **Nicht gemacht:** Mutationstests (seit 2026-10-28 nicht mehr verlangt), Docker-Lauf der Linux-CI (Docker fehlt auf diesem Rechner; die CI nach dem Push entscheidet).

116 Tests (`pytest tests`).

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App: Ergebnis, Kernfrage, fünf Experimente, Spielwiese, Grenzen, Formeln |
| `ksc_algorithm.py` | Kern: Schätzer von Knuth, Bäume, N-Damen, Wege, Rucksack-Baum, Chen, Hashing, Statistik |
| `ksc_constants.py` | Regler-Grenzen, Obergrenzen, Experiment-Konstanten, Farben, Presets |
| `ksc_evaluation.py` | Analyse, Experimente, Urteilstexte, Formatierung |
| `ksc_layout.py` | Fester Kopf (Stylesheet) |
| `ksc_pdf_export.py` | PDF der aktuellen Schätzung (fpdf2) |
| `ksc_presets.py` | Permalink (Begrenzen), Presets (Schnellstart in der Seitenleiste, aktives Preset hervorgehoben) |
| `ksc_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `requirements-dev.txt` | Laufzeit plus pytest |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt; numpy für das Hashing) |
| `tests/` | Handwerte, Orakel, Eigenschaften, Randfälle, Urteilstexte, Claims, Presets, Layout, AppTest, Footer, Laufzeit-Importe |

## Bewusst nicht umgesetzt

- **MCMC, Kopplung, (ε, δ)-Garantien (FPRAS, Jerrum, Sinclair, Vigoda für die Permanente):** nur genannt.
- **Sequentielle Monte-Carlo-Methoden mit Wiederverwendung, Annealed Importance Sampling:** nur genannt.
- **ApproxMC mit SAT-Löser:** hier nur die Idee der Hash-Zellen mit vollständiger Aufzählung als Orakel.
- **Schätzer für den dynamischen Branch-and-Bound-Baum eines Lösers** und die vorhergesagte Rechenzeit von MIP-Lösern: der Baum hier hat einen festen Zielwert.
- **Verwandte Demos:** `gleichverteilt-ziehen-demo` (Ziehen aus bekannten Zählungen), `frontier-diagramm-demo` (die Wahrheit für die Wege), `tutte-polynom-demo` (Zufallsziehen der Zuverlässigkeit als Gegenprobe), `branch-bound-demo`, `branch-cut-demo`, `dynamic-programming-demo` (Suchbaum und Schranken), `mcts-demo`, `posterior-sampling-demo` (Baumsuche und Bandits), `schaetzen-demo` (Schätzen von Wirkungen, kausale Linie); nur Verweise.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

Streamlit Cloud: Python-Version nach der Voreinstellung der Plattform (lokal `3.14`, CI `3.12`); der Code nutzt nur Merkmale, die in `3.12` laufen.

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly, fpdf2 und NumPy.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zur Reihe: [Abzählen: von der Rekursion zur Verfahrenswahl](https://sebastianhanisch.net/konzepte-abzaehlen.html).
