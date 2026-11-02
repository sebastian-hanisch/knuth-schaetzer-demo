"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import math

import plotly.graph_objects as go

import ksc_constants as C


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=340):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=50, b=10), legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def build_running(running: list, exact, label: str):
    """Laufendes Mittel der Schätzung mit 95-Prozent-Intervall gegen die Zahl der Sondierungen, mit der Wahrheit als Linie."""
    fig = go.Figure()
    xs = [r["N"] for r in running]
    fig.add_trace(go.Scatter(x=xs, y=[r["Mittel"] for r in running], mode="lines+markers", name="Schätzung (Mittel)", line=dict(color=C.COLOR_MAIN),
                             error_y=dict(type="data", array=[r["halb"] if math.isfinite(r["halb"]) else 0 for r in running], color=C.COLOR_MAIN, thickness=1.2)))
    if exact is not None:
        fig.add_hline(y=exact, line=dict(color=C.COLOR_WARN, dash="dash"), annotation_text="Wahrheit", annotation_position="top left")
    fig.update_xaxes(title_text="Zahl der Sondierungen", type="log")
    fig.update_yaxes(title_text=label)
    return _base(fig, 320)


def build_error(res: dict):
    """Median und 95-Prozent-Quantil des relativen Fehlers gegen die Zahl der Sondierungen (doppeltlogarithmisch) mit der Linie 1/√N."""
    fig = go.Figure()
    for (n, r), color in zip(res.items(), (C.COLOR_LINE, C.COLOR_MAIN)):
        xs = [row["N"] for row in r["Reihe"]]
        fig.add_trace(go.Scatter(x=xs, y=[row["Median"] for row in r["Reihe"]], mode="lines+markers", name=f"n = {n}: Median", line=dict(color=color)))
        fig.add_trace(go.Scatter(x=xs, y=[row["Quantil95"] for row in r["Reihe"]], mode="lines+markers", name=f"n = {n}: 95-Prozent-Quantil", line=dict(color=color, dash="dot")))
    first = res[max(res)]["Reihe"]
    ref = first[0]["Median"]
    fig.add_trace(go.Scatter(x=[row["N"] for row in first], y=[ref * math.sqrt(first[0]["N"] / row["N"]) for row in first], mode="lines", name="Steigung −1/2", line=dict(color=C.COLOR_ALL, dash="dash")))
    fig.update_xaxes(title_text="Zahl der Sondierungen N", type="log")
    fig.update_yaxes(title_text="relativer Fehler des Mittels", type="log")
    return _base(fig, 360)


def build_paths(rows: list):
    """Verhältnis Schätzung zu Wahrheit mit 95-Prozent-Intervall je Gitter."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[r["n"] for r in rows], y=[r["Verhältnis"] for r in rows], mode="markers", name="Schätzung / Wahrheit", marker=dict(color=C.COLOR_MAIN, size=9),
                             error_y=dict(type="data", array=[r["Halb"] / r["Wahrheit"] for r in rows], color=C.COLOR_MAIN, thickness=1.2)))
    fig.add_hline(y=1, line=dict(color=C.COLOR_WARN, dash="dash"))
    fig.update_xaxes(title_text="Seitenlänge n des n×n-Gitters", dtick=1)
    fig.update_yaxes(title_text="Schätzung geteilt durch Wahrheit")
    return _base(fig, 320)


def build_check(rows: list):
    """Variationskoeffizient ohne und mit Erreichbarkeitsprüfung je Gitter (logarithmische Achse)."""
    fig = go.Figure()
    xs = [r["n"] for r in rows]
    fig.add_trace(go.Bar(x=xs, y=[r["cv_ohne"] for r in rows], name="ohne Prüfung", marker_color=C.COLOR_WARN))
    fig.add_trace(go.Bar(x=xs, y=[r["cv_mit"] for r in rows], name="mit Erreichbarkeitsprüfung", marker_color=C.COLOR_MAIN))
    fig.update_xaxes(title_text="Seitenlänge n des n×n-Gitters", dtick=1)
    fig.update_yaxes(title_text="Variationskoeffizient des Gewichts", type="log")
    fig.update_layout(barmode="group")
    return _base(fig, 320)


def build_knapsack(rows: list):
    """Median-Fehler nach wenigen und vielen Sondierungen je Rucksack-Baum (logarithmische Achse; ohne Fehler fehlt der Balken)."""
    fig = go.Figure()
    xs = [f"{r['n']} {'korreliert' if r['korreliert'] else 'zufällig'} ({r['Knoten']} Knoten)" for r in rows]
    for N, color in zip(C.EXP_KNAP_BLOCKS, (C.COLOR_WARN, C.COLOR_MAIN)):
        fig.add_trace(go.Bar(x=xs, y=[r["Fehler"][N] or None for r in rows], name=f"Median-Fehler nach {N} Sondierungen", marker_color=color))
    fig.update_yaxes(title_text="relativer Fehler", type="log")
    fig.update_layout(barmode="group")
    return _base(fig, 360)


def build_hash(res: dict):
    """Variationskoeffizient der Hash-Schätzung gegen die Zellgröße (doppeltlogarithmisch) mit der Linie 1/√Zellgröße."""
    rows = [r for r in res["hash"] if r["m"] > 0]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[r["Zelle"] for r in rows], y=[r["cv"] for r in rows], mode="markers", name="gemessen", marker=dict(color=C.COLOR_MAIN, size=9)))
    fig.add_trace(go.Scatter(x=[r["Zelle"] for r in rows], y=[r["1/Wurzel"] for r in rows], mode="lines", name="1/√Zellgröße", line=dict(color=C.COLOR_WARN, dash="dash")))
    fig.update_xaxes(title_text="Zellgröße (Lösungen pro Zelle im Mittel)", type="log")
    fig.update_yaxes(title_text="Variationskoeffizient der Schätzung", type="log")
    return _base(fig, 320)


def build_play(res: dict):
    """Verteilung der Schätzung aus allen Sondierungen des eigenen Baums."""
    fig = go.Figure()
    fig.add_trace(go.Bar(x=[str(s) for s, _ in res["Ergebnisse"]], y=[float(p) for _, p in res["Ergebnisse"]], name="Wahrscheinlichkeit", marker_color=C.COLOR_MAIN))
    fig.update_xaxes(title_text="Schätzung einer Sondierung")
    fig.update_yaxes(title_text="Wahrscheinlichkeit", range=[0, 1.02])
    return _base(fig, 280)
