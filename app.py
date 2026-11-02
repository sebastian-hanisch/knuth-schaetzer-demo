"""Knuth-Schätzer – wenn Zählen zu schwer ist, schätzen - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Stück 15 der Reihe „Abzählen und erzeugende Funktionen“: Wenn das exakte Zählen nicht mehr zu bezahlen ist, steigt man zufällig durch den Suchbaum und multipliziert die Zahl der Wahlmöglichkeiten (Knuth, Rosenbluth).
Das Gewicht hat als Erwartung genau die gesuchte Zahl; wie genau das Mittel ist, sagt der Variationskoeffizient. Das Diagramm aus Stück 13 liefert die Wahrheit.
Aufbau und Regeln: DEMO-PLAYBOOK.md (§2).

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import ksc_constants as C
from ksc_evaluation import (
    Settings,
    analyse,
    better_rows,
    big_text,
    check_rows,
    de,
    error_rows,
    knapsack_rows,
    num_text,
    path_rows,
    pct_text,
    play_tree,
    verdict_answers,
    verdict_better,
    verdict_check,
    verdict_error,
    verdict_knapsack,
    verdict_paths,
    verdict_play,
)
from ksc_layout import dunkles_design, kopf_css
from ksc_pdf_export import build_pdf
from ksc_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    sidebar_presets,
    sync_query_params,
)
from ksc_visualization import build_check, build_error, build_hash, build_knapsack, build_paths, build_play, build_running

st.set_page_config(page_title="Knuth-Schätzer – Sebastian Hanisch", layout="wide")

SPINNER = "Die Experimente werden einmal gerechnet …"


@st.cache_data(show_spinner="Die Sondierungen werden gerechnet …")
def _analysis(settings):
    return analyse(settings)


@st.cache_data(show_spinner=SPINNER)
def _errors():
    return error_rows()


@st.cache_data(show_spinner=SPINNER)
def _paths():
    return path_rows()


@st.cache_data(show_spinner=SPINNER)
def _checks():
    return check_rows()


@st.cache_data(show_spinner=SPINNER)
def _knapsack():
    return knapsack_rows()


@st.cache_data(show_spinner=SPINNER)
def _better():
    return better_rows()


@st.cache_data(show_spinner=False)
def _play(text):
    return play_tree(text)


def verdict(pair):
    kind, text = pair
    getattr(st, kind)(text)


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in ksc_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🎲 Knuth-Schätzer – wenn Zählen zu schwer ist, schätzen")
st.markdown(
    """
**Was tun, wenn das exakte Zählen nicht mehr zu bezahlen ist?** Man **schätzt**: Man steigt **zufällig** ein Mal durch den Suchbaum hinab (eine **Sondierung**), multipliziert an jedem Knoten die Zahl der Wahlmöglichkeiten und erhält ein **Gewicht**, dessen **Erwartungswert genau die gesuchte Zahl** ist
(Knuth 1975 für die Größe eines Suchbaums, Rosenbluth und Rosenbluth 1955 für selbstvermeidende Wege). Das Mittel aus N Sondierungen ist **unverzerrt**, sein Fehler fällt wie 1/√N, **wenn die Streuung endlich und klein ist**: wie klein, sagt der **Variationskoeffizient** des Gewichts.
Bei ausgeglichenen Bäumen ist er klein, bei unausgeglichenen riesig; dann hilft Vorwissen (**Erreichbarkeitsprüfung**), manchmal Schichtung (**Chen**) und bei kleinen Bäumen nur das Aufzählen. Das **Diagramm aus Stück 13** liefert die Wahrheit, an der man den Schätzer prüft.

Weiter unten: **fünf Experimente** (**🔬**), eine **🎲 Spielwiese** mit eigenem Baum, **🚧 Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**.
"""
)

with st.expander("So funktioniert der Schätzer", expanded=True):
    st.markdown(
        """
1. **Sondierung:** Von der Wurzel aus wählt man an jedem Knoten ein Kind gleichverteilt und merkt sich die Zahl der Kinder. Das **Gewicht** ist das Produkt dieser Zahlen auf dem Weg.
2. **Schätzung der Knotenzahl:** Die Summe der Gewichte aller besuchten Knoten (Wurzel: 1). Jeder Baum-Knoten wird mit Wahrscheinlichkeit (1 / Gewicht) besucht und zählt dann mit dem Gewicht: im Erwartungswert genau einmal.
3. **Schätzung einer Zahl von Lösungen:** Das Gewicht am Ziel (bei Sackgassen 0) schätzt die Zahl der Wege oder Lösungen.
4. **Genauigkeit:** Das Mittel aus N Sondierungen hat den Standardfehler (Streuung / √N); der **Variationskoeffizient** (Streuung geteilt durch Mittel) bestimmt, wie viele Sondierungen nötig sind: **cv² / ε²** für den relativen Standardfehler ε.
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.markdown("**Aufgabe**")
    task = st.selectbox("Aufgabe", list(C.TASKS), key="task_select", help="Suchbaum der N-Damen (Zahl der Knoten), einfache Wege von Ecke zu Ecke im Gitter (Zahl der Wege) oder der Branch-and-Bound-Baum eines Rucksacks (Knoten bis zum Beweis des Optimums).")
    n = st.slider("Größe n", *bounds("n_slider"), key="n_slider", help="N-Damen 4 bis 10, Gitter 2 bis 10 Knoten je Seite, Rucksack 8 bis 28 Gegenstände; außerhalb der Grenzen der Aufgabe wird geklemmt.")
    st.markdown("**Verfahren**")
    probes = st.select_slider("Sondierungen", options=list(C.PROBE_CHOICES), key="probes_select", help="Zahl der Zufallsabstiege. Mit Erreichbarkeitsprüfung höchstens 1.000, mit Chens Schichtung höchstens 3.000.")
    method = st.selectbox("Verfahren", list(C.METHODS), key="method_select", help="Knuth: ein Zufallsabstieg je Sondierung. Mit Erreichbarkeitsprüfung (nur Wege): nur Schritte, von denen das Ziel noch erreichbar ist. Chen (nur Suchbäume): je Ebene und Typ ein Vertreter.")
    seed = st.slider("Seed", *bounds("seed_slider"), key="seed_slider", help="Bestimmt alle Zufallsziehungen; beim Rucksack auch die Gegenstände.")

sync_query_params({"task_select": task, "n_slider": int(n), "probes_select": int(probes), "method_select": method, "seed_slider": int(seed)})

settings = Settings(task, int(n), int(probes), method, int(seed))
a = _analysis(settings)
for note in a.notes:
    st.info(note)

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Ergebnis")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Schätzung", num_text(a.estimate), help="Mittel der Gewichte aller Sondierungen.")
m2.metric("Wahrheit", "–" if a.exact is None else num_text(a.exact), help="Exakte Zahl: Tiefensuche (Suchbäume) oder Stück 13 (Wege).")
m3.metric("Fehler", "–" if a.rel_error is None else pct_text(a.rel_error), help="Betrag der Abweichung geteilt durch die Wahrheit.")
m4.metric("Variationskoeffizient", de(a.cv, 2) if a.cv != float("inf") else "unbegrenzt", help="Streuung der einzelnen Gewichte geteilt durch ihr Mittel: bestimmt die nötige Zahl der Sondierungen.")
st.plotly_chart(build_running(a.running, a.exact, "Zahl der einfachen Wege" if a.task == C.TASK_PATHS else "Knotenzahl des Suchbaums"), width="stretch", key="main_chart")
st.caption("Das Mittel der ersten N Sondierungen mit seinem 95-Prozent-Intervall; die gestrichelte Linie ist die Wahrheit.")
st.dataframe(a.ways, hide_index=True, width="stretch")

if st.button("📄 PDF der aktuellen Schätzung erstellen", key="pdf_make"):
    st.session_state["pdf_made"] = (settings, build_pdf(a))
made = st.session_state.get("pdf_made")
if made and made[0] == settings:
    st.download_button("⬇️ PDF herunterladen", data=made[1], file_name="knuth-schaetzer.pdf", mime="application/pdf", key="pdf_download")

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage: Wie genau darf geschätzt werden, wenn exaktes Zählen zu schwer ist?")
verdict(verdict_answers(a))

st.markdown("---")

# --- Experimente ---------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment 1: Unverzerrt, aber streuend")
st.caption("Beim Suchbaum der N-Damen (Knotenzahl exakt bekannt): der relative Fehler des Mittels aus N Sondierungen gegen N, aus Blöcken einer einzigen langen Folge von Sondierungen. Die gestrichelte Linie hat die Steigung −1/2.")
errs = _errors()
st.plotly_chart(build_error(errs), width="stretch", key="error_chart")
st.dataframe([{"n": n_, "Knoten": big_text(r["exakt"]), "Lösungen": big_text(r["Lösungen"]), "Variationskoeffizient": de(r["cv"], 2), "N": row["N"], "Blöcke": row["Blöcke"], "mittlerer Fehler": pct_text(row["Mittel"]), "Median-Fehler": pct_text(row["Median"]),
               "95-Prozent-Quantil": pct_text(row["Quantil95"])} for n_, r in errs.items() for row in r["Reihe"]], hide_index=True, width="stretch")
verdict(verdict_error(errs))

st.markdown("---")

st.subheader("🔬 Experiment 2: Wege im Gitter gegen die Wahrheit aus Stück 13")
st.caption(f"Einfache Wege von Ecke zu Ecke im n×n-Gitter, geschätzt mit {big_text(C.EXP_PATH_PROBES)} Sondierungen mit Erreichbarkeitsprüfung; die exakten Zahlen kommen aus dem Frontier-Diagramm (Stück 13).")
paths = _paths()
st.plotly_chart(build_paths(paths), width="stretch", key="paths_chart")
st.dataframe([{"n": r["n"], "Wahrheit": num_text(r["Wahrheit"]), "Schätzung": num_text(r["Schätzung"]), "Halbbreite": num_text(r["Halb"]), "Verhältnis": de(r["Verhältnis"], 3), "Wahrheit im Intervall": "ja" if r["im Intervall"] else "nein",
               "Variationskoeffizient": de(r["cv"], 2), "Sondierungen für 5 %": big_text(r["nötig"])} for r in paths], hide_index=True, width="stretch")
verdict(verdict_paths(paths))

st.markdown("---")

st.subheader("🔬 Experiment 3: Wissen einspeisen")
st.caption("Ohne Vorausschau enden viele Sondierungen in Sackgassen (Gewicht 0). Mit der Erreichbarkeitsprüfung (ein Schritt Vorausschau mit Breitensuche) erreicht jede das Ziel. Die Überdeckung zählt, in wie vielen Blöcken zu je 1.000 Sondierungen ohne Prüfung das 95-Prozent-Intervall die Wahrheit enthält.")
checks = _checks()
st.plotly_chart(build_check(checks), width="stretch", key="check_chart")
st.dataframe([{"n": r["n"], "Erfolgsrate ohne Prüfung": pct_text(r["Erfolgsrate"]), "Variationskoeffizient ohne": de(r["cv_ohne"], 2), "Variationskoeffizient mit": de(r["cv_mit"], 2), "Faktor": de(r["Faktor"], 1),
               "Überdeckung ohne Prüfung": f"{pct_text(r['Überdeckung'])} ({r['Blöcke']} Blöcke)"} for r in checks], hide_index=True, width="stretch")
verdict(verdict_check(checks))

st.markdown("---")

st.subheader("🔬 Experiment 4: Wenn der Baum unausgeglichen ist")
st.caption("Branch-and-Bound-Bäume eines Rucksacks (fester Zielwert = Optimum): wenige Gegenstände mit sehr verschiedenem Gewicht lassen den Baum dünn und schief werden. Der Median-Fehler stammt aus Blöcken zu 100 und 1.000 Sondierungen.")
knap = _knapsack()
st.plotly_chart(build_knapsack(knap), width="stretch", key="knapsack_chart")
st.dataframe([{"Gegenstände": r["n"], "Art": "stark korreliert" if r["korreliert"] else "zufällig", "Baumknoten": big_text(r["Knoten"]), "voller Baum": big_text(r["voll"]), "Variationskoeffizient": de(r["cv"], 2),
               "Median-Fehler (100)": pct_text(r["Fehler"][100]), "Median-Fehler (1.000)": pct_text(r["Fehler"][1000]), "Sondierungen für 5 %": big_text(r["nötig"]), "Aufzählen billiger": "ja" if r["Aufzählen billiger"] else "nein"} for r in knap],
             hide_index=True, width="stretch")
verdict(verdict_knapsack(knap))

st.markdown("---")

st.subheader("🔬 Experiment 5: Chen und Hashing")
st.caption("Chens geschichtete Probenahme gegen Knuth bei gleichem Aufwand (Zahl der berechneten Kinderlisten) und die Idee des Hashings: m zufällige XOR-Bedingungen halbieren die Lösungsmenge je Bedingung, die Schätzung ist 2^m mal die Größe der Zelle.")
better = _better()
st.dataframe([{"n": r["n"], "Knoten": big_text(r["Knoten"]), "Chen: Variationskoeffizient": de(r["Chen cv"], 2), "Chen: Kinderlisten je Sondierung": de(r["Chen Kosten"], 0), "Knuth: Variationskoeffizient": de(r["Knuth cv"], 2), "Knuth: Kinderlisten je Sondierung": de(r["Knuth Kosten"], 1),
               "Knuth mit gleichem Aufwand": f"{r['k']} Sondierungen: {de(r['Knuth gleicher Aufwand cv'], 2)}"} for r in better["chen"]], hide_index=True, width="stretch")
st.plotly_chart(build_hash(better), width="stretch", key="hash_chart")
st.dataframe([{"m": r["m"], "Zelle im Mittel": de(r["Zelle"], 1), "Mittel der Schätzung": big_text(round(r["Mittel"])), "Variationskoeffizient": de(r["cv"], 3), "1/√Zelle": de(r["1/Wurzel"], 3), "Anteil im Faktor 1,5": pct_text(r["im Faktor 1,5"])} for r in better["hash"]], hide_index=True, width="stretch")
verdict(verdict_better(better))

st.markdown("---")

# --- Spielwiese ----------------------------------------------------------------------------------------------------------------------------

st.subheader("🎲 Spielwiese: ein eigener Baum")
st.caption(f"Ein Baum in Klammerschreibweise, höchstens {C.PLAY_MAX_NODES} Knoten: (()()) ist eine Wurzel mit zwei Blättern, ((()()())(())) eine Wurzel mit einem Kind mit drei Blättern und einem Kind mit einem Blatt. Die App zählt alle Sondierungen auf und zeigt Erwartung und Varianz exakt.")
play_text = st.text_input("Baum", value=C.PLAY_TREE_DEFAULT, max_chars=400, key="play_tree", help="Nur runde Klammern; alles in einem äußeren Paar.")
play = _play(play_text)
if "error" not in play:
    st.plotly_chart(build_play(play), width="stretch", key="play_chart")
verdict(verdict_play(play))

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    f"""
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Der Baum ist ausgeglichen** | Der Variationskoeffizient wird riesig: der Rucksack-Baum mit 24 Gegenständen hat einen von 25 und liegt nach tausenden Sondierungen noch weit daneben. Die Erwartung stimmt trotzdem, aber das Mittel konvergiert nicht in brauchbarer Zeit. | Experiment 4 |
| **Die Streuung ist endlich und die Normalnäherung gilt** | Die 95-Prozent-Intervalle beruhen auf der Normalnäherung des Mittels. Bei schweren Ausläufern der Gewichte (Wege im Gitter ab n = 8 mit wenigen Sondierungen) verfehlt das Intervall die Wahrheit öfter als in 5 von 100 Fällen. | Experiment 2 und 3 |
| **Schätzen ist billiger als Zählen** | Bei kleinen Bäumen kostet das Schätzen mehr als das Aufzählen: beim 35.539-Knoten-Baum der zehn Damen lohnt es sich (Faktor 24 bei 5 Prozent Standardfehler), beim Rucksack-Baum mit 7.496 Knoten nicht. | Ergebnis |
| **Die Wahrheit ist bekannt** | Hier gibt es sie (Tiefensuche, Stück 13), bei echten Aufgaben nicht: dann bleibt nur die geschätzte Streuung der Gewichte, und die ist bei schweren Ausläufern selbst unsicher. | Experiment 2 |
| **Der Baum ist fest** | Der Schätzer gilt für einen festen Baum: der Branch-and-Bound-Baum hier hat einen **festen** Zielwert (das Optimum). Der echte Baum eines Lösers ändert sich mit der besten bekannten Lösung. | Experiment 4 |
| **Chens Schichtung lohnt** | Je Sondierung ist die Streuung kleiner, aber der Aufwand viel größer: bei gleichem Aufwand ist hier das einfache Verfahren besser. | Experiment 5 |
| **Hashing hat einen Löser** | Das Orakel zählt alle Lösungen der Zelle auf; ohne Löser sieht man nur die Statistik, nicht den Nutzen. | Experiment 5 |
| **Die Größe ist begrenzt** | N-Damen bis n = {C.SIZE_RANGE[C.TASK_QUEENS][1]}, Wege bis {C.SIZE_RANGE[C.TASK_PATHS][1]}×{C.SIZE_RANGE[C.TASK_PATHS][1]}, Rucksack bis {C.SIZE_RANGE[C.TASK_KNAPSACK[0]][1]} Gegenstände; höchstens {big_text(C.PROBE_CAP['Knuth'])} Sondierungen ({big_text(C.PROBE_CAP['Knuth mit Erreichbarkeitsprüfung'])} mit Prüfung, {big_text(C.PROBE_CAP['Chen-Schichtung'])} bei Chen). | – |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Schätzer von Knuth.** Für einen Baum $T$ mit Wurzel $r$ sei ein Zufallsabstieg $r = v_0, v_1, \dots, v_k$ gegeben, bei dem $v_{i+1}$ gleichverteilt unter den $d_i$ Kindern von $v_i$ gewählt wird, und $w_i = d_0 d_1 \cdots d_{i-1}$ ($w_0 = 1$). Die Schätzung der Knotenzahl ist
$$\hat{N} = \sum_{i=0}^{k} w_i.$$
Ein Knoten $u$ in Tiefe $j$ wird mit Wahrscheinlichkeit $1 / w(u)$ besucht, wobei $w(u)$ das Produkt der Kinderzahlen seiner Vorfahren ist, und trägt dann $w(u)$ bei; also $\mathbb{E}[\hat{N}] = |T|$ (unverzerrt).

**Wege (Rosenbluth).** Das Gewicht $W = \prod_i d_i$ bei Erreichen des Ziels und $W = 0$ bei einer Sackgasse hat $\mathbb{E}[W]$ = Zahl der Wege. Mit Erreichbarkeitsprüfung zählen nur Schritte, von denen aus das Ziel erreichbar ist; die Erwartung bleibt gleich, die Streuung sinkt.

**Genauigkeit.** Aus $N$ unabhängigen Sondierungen ist das Mittel $\bar{W}$ unverzerrt mit Standardfehler $\sigma / \sqrt{N}$; der Variationskoeffizient $\mathrm{cv} = \sigma / \mu$ gibt die nötige Zahl $N \ge \mathrm{cv}^2 / \varepsilon^2$ für einen relativen Standardfehler $\varepsilon$. Das 95-Prozent-Intervall $\bar{W} \pm 1{,}96\, s / \sqrt{N}$ beruht auf der Normalnäherung und kann bei schweren Ausläufern der Gewichte die Wahrheit zu oft verfehlen.

**Chen.** Je Ebene bleibt je Typ $(\text{Tiefe}, \text{Kinderzahl})$ ein zufälliger Vertreter, der die Summe der Gewichte seiner Typgenossen trägt; die Schätzung bleibt unverzerrt, die Streuung ist kleiner.

**Hashing.** Wählt man $m$ zufällige Paritätsbedingungen (jede ein XOR über eine zufällige Teilmenge der Variablen mit zufälligem Paritätsbit), enthält die Zelle der Lösungen $S$, die alle erfüllen, im Mittel $|S| / 2^m$ Lösungen; $2^m \cdot |\text{Zelle}|$ ist unverzerrt, und sein Variationskoeffizient liegt bei etwa $1 / \sqrt{|\text{Zelle}|}$.

**Literatur** (Titel und Fundstelle aus dem Gedächtnis, nicht eingesehen).
D. E. Knuth: *Estimating the efficiency of backtrack programs*, Mathematics of Computation 29, 1975, S. 122–136.
M. N. Rosenbluth und A. W. Rosenbluth: *Monte Carlo calculation of the average extension of molecular chains*, Journal of Chemical Physics 23, 1955, S. 356–359.
P. C. Chen: *Heuristic sampling: a method for predicting the performance of tree searching programs*, SIAM Journal on Computing 21, 1992, S. 295–315.
L. Stockmeyer: *The complexity of approximate counting*, STOC 1983; S. Chakraborty, K. S. Meel und M. Y. Vardi: *A scalable approximate model counter*, CP 2013.
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
