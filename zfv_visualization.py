"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import numpy as np
import plotly.graph_objects as go

import zfv_constants as C


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=340):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.25), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def build_vectors(mask, n):
    """Alle 2^n Vektoren als Gitter: grün = besteht den Test trotz des Fehlers (Lügner), grau = entlarvt den Fehler. Zeile = erste Hälfte der Komponenten, Spalte = zweite Hälfte (Reihenfolge der Aufzählung)."""
    rows = 1 << (n // 2)
    grid = np.array(mask, dtype=int).reshape(rows, -1)
    fig = go.Figure(go.Heatmap(z=grid, colorscale=[[0, "rgba(150,150,150,0.35)"], [1, C.COLOR_STRONG]], showscale=False, xgap=1, ygap=1,
                               hovertemplate="Zeile %{y}, Spalte %{x}: %{z}<extra>1 = lügt</extra>"))
    fig.update_yaxes(visible=False, autorange="reversed")
    fig.update_xaxes(visible=False)
    return _base(fig, 300)


def build_amplification(share, t_max, t_chosen, sample_share):
    """Wahrscheinlichkeit, dass der Fehler nach t Runden unentdeckt bleibt (logarithmisch): exakt (Anteil^t), die Schranke (1/2)^t und der Wert der Stichprobe bei der gewählten Rundenzahl."""
    ts = list(range(0, t_max + 1))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ts, y=[0.5 ** t for t in ts], mode="lines", name="Schranke (1/2)^t", line=dict(color=C.COLOR_BOUND, dash="dash")))
    fig.add_trace(go.Scatter(x=ts, y=[float(share) ** t for t in ts], mode="lines+markers", name="exakt: Anteil^t", line=dict(color=C.COLOR_EXACT)))
    if sample_share > 0:
        fig.add_trace(go.Scatter(x=[t_chosen], y=[sample_share], mode="markers", name="Stichprobe (Illustration)", marker=dict(symbol="diamond-open", size=14, color=C.COLOR_SAMPLE, line=dict(width=2))))
    fig.update_xaxes(title="Runden t", dtick=1)
    fig.update_yaxes(type="log", title="Fehler bleibt unentdeckt")
    return _base(fig)


def build_bases(num, strong, fermat):
    """Alle Basen 1 bis n − 1 als Streifen: Fermat-Lügner (gelb) und starke Lügner (grün); jeder starke Lügner ist auch Fermat-Lügner."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=list(fermat), y=["Fermat-Test"] * len(fermat), mode="markers", name="Fermat-Lügner", marker=dict(color=C.COLOR_FERMAT, size=5, symbol="line-ns-open")))
    fig.add_trace(go.Scatter(x=list(strong), y=["Miller–Rabin"] * len(strong), mode="markers", name="starke Lügner", marker=dict(color=C.COLOR_STRONG, size=9, symbol="line-ns-open", line=dict(width=2))))
    fig.update_xaxes(title=f"Basis a (1 bis {num - 1})", range=[0, num])
    return _base(fig, 220)


def build_freivalds_sweep(rows):
    """Größter gemessener Anteil lügender Vektoren je Fehlerart und Größe (logarithmisch) gegen die Schranke 1/2."""
    kinds = list(C.KINDS)
    fig = go.Figure()
    for color, n in zip(C.COLOR_SERIES, sorted({r["n"] for r in rows})):
        by = {r["kind"]: r for r in rows if r["n"] == n}
        fig.add_trace(go.Bar(x=[C.KINDS[k] for k in kinds], y=[float(by[k]["max"]) for k in kinds], name=f"n = {n}", marker_color=color))
    fig.add_hline(y=0.5, line=dict(color=C.COLOR_BOUND, dash="dash"), annotation_text="Schranke 1/2", annotation_position="top right")
    fig.update_layout(barmode="group")
    fig.update_yaxes(type="log", title="größter Anteil lügender Vektoren")
    return _base(fig, 380)


def build_liars(res):
    """Anteil starker Lügner je ungerader Zusammengesetzter Zahl (logarithmisch) gegen die Schranke 1/4."""
    rows = res["rows"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[r["n"] for r in rows], y=[max(float(r["strong_share"]), 1e-5) for r in rows], mode="markers", name="Zusammengesetzte Zahlen", marker=dict(color=C.COLOR_STRONG, size=4, opacity=0.6),
                             hovertemplate="n = %{x}<br>Anteil %{y:.4f}<extra></extra>"))
    worst = res["worst"]
    fig.add_trace(go.Scatter(x=[r["n"] for r in worst], y=[float(r["strong_share"]) for r in worst], mode="markers", name="die acht schlimmsten", marker=dict(color=C.COLOR_BOUND, size=9, symbol="diamond-open", line=dict(width=2))))
    fig.add_hline(y=0.25, line=dict(color=C.COLOR_BOUND, dash="dash"), annotation_text="Schranke 1/4", annotation_position="top right")
    fig.update_xaxes(title="Zahl n")
    fig.update_yaxes(type="log", title="Anteil starker Lügner (Basen 1 bis n − 1)")
    return _base(fig, 380)


def build_carmichael(rows):
    """Anteil der Fermat-Lügner und der starken Lügner an allen Basen, je Carmichael-Zahl."""
    ns = [str(r["n"]) for r in rows]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=ns, y=[100 * float(r["fermat_share"]) for r in rows], name="Fermat-Lügner", marker_color=C.COLOR_FERMAT))
    fig.add_trace(go.Bar(x=ns, y=[100 * float(r["strong_share"]) for r in rows], name="starke Lügner (Miller–Rabin)", marker_color=C.COLOR_STRONG))
    fig.update_layout(barmode="group")
    fig.update_xaxes(title="Carmichael-Zahl", type="category")
    fig.update_yaxes(title="Anteil der Basen in %")
    return _base(fig, 360)


def build_bpp(res):
    """Fehler über die Zahl der Läufe (logarithmisch): Mehrheitsentscheid bei zweiseitigem Fehler 1/3 gegen einseitigen Fehler 1/2 und 1/4 (Miller–Rabin)."""
    rows = res["rows"]
    ts = [r["t"] for r in rows]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ts, y=[float(r["majority"]) for r in rows], mode="lines+markers", name="zweiseitig 1/3, Mehrheit (BPP)", line=dict(color=C.COLOR_BOUND)))
    fig.add_trace(go.Scatter(x=ts, y=[float(r["one_sided"]) for r in rows], mode="lines+markers", name="einseitig 1/2 (RP, Freivalds)", line=dict(color=C.COLOR_EXACT)))
    fig.add_trace(go.Scatter(x=ts, y=[0.25 ** t for t in ts], mode="lines+markers", name="einseitig 1/4 (Miller–Rabin)", line=dict(color=C.COLOR_STRONG)))
    fig.update_xaxes(title="Läufe t")
    fig.update_yaxes(type="log", title="Gesamtfehler")
    return _base(fig, 360)
