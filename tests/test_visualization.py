"""Abbildungen: Reihen, Farben, gesperrte Achsen; der PDF-Bau mit Umlauten."""

from fractions import Fraction

import numpy as np

import zfv_algorithm as A
import zfv_constants as C
import zfv_evaluation as ev
import zfv_visualization as V
from zfv_pdf_export import build_pdf


def _locked(fig):
    assert fig.layout.xaxis.fixedrange and fig.layout.yaxis.fixedrange


def test_vectors_grid_has_one_cell_per_vector():
    a = ev.analyse(ev.Settings(n=6))
    _, mask = A.liar_vectors(a.matrix.a, a.matrix.b, a.matrix.c_wrong)
    fig = V.build_vectors(mask, 6)
    z = np.array(fig.data[0].z)
    assert z.shape == (8, 8) and int(z.sum()) == a.matrix.liars and fig.data[0].colorscale[1][1] == C.COLOR_STRONG
    _locked(fig)


def test_vectors_grid_for_odd_and_smallest_n():
    for n in (2, 3, 7, 12):
        mask = [True] * (1 << n)
        z = np.array(V.build_vectors(mask, n).data[0].z)
        assert z.size == 1 << n and z.shape[0] == 1 << (n // 2)


def test_amplification_has_bound_exact_and_sample_series():
    fig = V.build_amplification(Fraction(1, 2), 12, 3, 0.13)
    assert [t.name for t in fig.data] == ["Schranke (1/2)^t", "exakt: Anteil^t", "Stichprobe (Illustration)"]
    assert list(fig.data[0].x) == list(range(13)) and abs(fig.data[1].y[3] - 0.125) < 1e-12 and list(fig.data[2].x) == [3] and fig.layout.yaxis.type == "log"
    _locked(fig)
    assert [t.name for t in V.build_amplification(Fraction(1, 4), 12, 3, 0).data] == ["Schranke (1/2)^t", "exakt: Anteil^t"]            # Stichprobe ohne Treffer: nicht auf der Log-Achse


def test_bases_strips_show_both_tests():
    fig = V.build_bases(561, A.strong_liars(561), A.fermat_liars(561))
    assert [t.name for t in fig.data] == ["Fermat-Lügner", "starke Lügner"] and len(fig.data[0].x) == 320 and len(fig.data[1].x) == 10
    assert fig.data[0].marker.color == C.COLOR_FERMAT and fig.data[1].marker.color == C.COLOR_STRONG and tuple(fig.layout.xaxis.range) == (0, 561)
    _locked(fig)


def test_freivalds_sweep_chart_has_one_bar_series_per_size():
    rows = ev.sweep_freivalds(sizes=(3, 4), pairs=3, seed=5)
    fig = V.build_freivalds_sweep(rows)
    assert [t.name for t in fig.data] == ["n = 3", "n = 4"] and all(len(t.x) == len(C.KINDS) for t in fig.data) and fig.layout.yaxis.type == "log"
    assert list(fig.data[0].x) == list(C.KINDS.values())
    assert [t.y for t in fig.data][0][0] == 0.5                                                          # „ein Eintrag falsch“: genau 1/2
    _locked(fig)


def test_liars_chart_marks_the_eight_worst():
    res = ev.sweep_liars(limit=300)
    fig = V.build_liars(res)
    assert [t.name for t in fig.data] == ["Zusammengesetzte Zahlen", "die acht schlimmsten"] and len(fig.data[0].x) == res["count"] and len(fig.data[1].x) == 8
    assert min(fig.data[0].y) >= 1e-5
    _locked(fig)


def test_carmichael_and_bpp_charts():
    rows = ev.carmichael_table(3000)
    fig = V.build_carmichael(rows)
    assert [t.name for t in fig.data] == ["Fermat-Lügner", "starke Lügner (Miller–Rabin)"] and list(fig.data[0].x) == ["561", "1105", "1729", "2465", "2821"]
    assert abs(fig.data[0].y[0] - 100 * 320 / 560) < 1e-9
    _locked(fig)
    res = ev.bpp_table()
    fig = V.build_bpp(res)
    assert [t.name for t in fig.data] == ["zweiseitig 1/3, Mehrheit (BPP)", "einseitig 1/2 (RP, Freivalds)", "einseitig 1/4 (Miller–Rabin)"] and list(fig.data[0].x) == list(C.BPP_TS)
    assert abs(fig.data[0].y[1] - 7 / 27) < 1e-12 and abs(fig.data[2].y[2] - 0.25 ** 5) < 1e-15 and fig.layout.yaxis.type == "log"
    _locked(fig)


def test_pdf_builds_with_umlauts_for_every_class_of_number():
    for num in (561, 13, 100, 9):
        pdf = build_pdf(ev.analyse(ev.Settings(num=num, n=4)))
        assert pdf[:5] == b"%PDF-" and len(pdf) > 1500
