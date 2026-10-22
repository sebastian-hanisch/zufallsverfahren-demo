"""Jede Zahl der README steht hier und wird über dieselben Auswertungsfunktionen wie in der App nachgerechnet (DEMO-PLAYBOOK §4).

Alle Matrizen kommen aus dem eigenen SplitMix64-Generator (plattform- und versionsunabhängig); alle Anteile sind exakte Brüche, Zähler exakte Werte. Die Stichprobe ist Illustration: ihre Zahl steht nur als Einzelwert."""

from fractions import Fraction as F

import pytest

import zfv_algorithm as A
import zfv_constants as C
import zfv_evaluation as ev

# --- Befund 1: Wie scharf ist die Schranke 1/2? ------------------------------------------------------------------------------------------------

# (n, Fehlerart): (kleinster, mittlerer, größter Anteil, Paare mit genau 1/2, Paare über 1/2); je 200 Paare, alle 2^n Vektoren aufgezählt
FREIVALDS = {
    (6, "one"): (F(1, 2), F(1, 2), F(1, 2), 200, 0), (6, "two_row"): (F(1, 2), F(1, 2), F(1, 2), 200, 0), (6, "two_rows"): (F(1, 4), F(231, 800), F(1, 2), 31, 0),
    (6, "row"): (F(1, 64), F(53, 3200), F(1, 32), 0, 0), (6, "random"): (F(1, 64), F(1, 64), F(1, 64), 0, 0),
    (8, "one"): (F(1, 2), F(1, 2), F(1, 2), 200, 0), (8, "two_row"): (F(1, 2), F(1, 2), F(1, 2), 200, 0), (8, "two_rows"): (F(1, 4), F(227, 800), F(1, 2), 27, 0),
    (8, "row"): (F(1, 256), F(203, 51200), F(1, 128), 0, 0), (8, "random"): (F(1, 256), F(1, 256), F(1, 256), 0, 0),
    (10, "one"): (F(1, 2), F(1, 2), F(1, 2), 200, 0), (10, "two_row"): (F(1, 2), F(1, 2), F(1, 2), 200, 0), (10, "two_rows"): (F(1, 4), F(221, 800), F(1, 2), 21, 0),
    (10, "row"): (F(1, 1024), F(1, 1024), F(1, 1024), 0, 0), (10, "random"): (F(1, 1024), F(1, 1024), F(1, 1024), 0, 0),
}


@pytest.fixture(scope="module")
def freivalds():
    return ev.sweep_freivalds()


def test_claim_freivalds_table(freivalds):
    """README, Befund 1: je Größe und Fehlerart 200 feste Paare; kleinster / mittlerer / größter Anteil lügender Vektoren, Paare mit genau 1/2, Paare über 1/2."""
    assert {(r["n"], r["kind"]): (r["min"], r["mean"], r["max"], r["at_half"], r["above_half"]) for r in freivalds} == FREIVALDS
    assert all(r["pairs"] == 200 for r in freivalds) and len(freivalds) == 15


def test_claim_the_bound_is_never_exceeded_and_exactly_met_for_errors_in_one_row(freivalds):
    """README: 3.000 Instanzen (3 Größen · 5 Fehlerarten · 200 Paare), nie über 1/2; genau 1/2 bei jedem Paar für „ein Eintrag falsch“ und „zwei Einträge einer Zeile“; bei „zwei Zeilen, je ein Eintrag“ bei 31 / 27 / 21 von 200."""
    assert sum(r["pairs"] for r in freivalds) == 3000 and sum(r["above_half"] for r in freivalds) == 0
    text = ev.verdict_freivalds_sweep(freivalds)[1]
    assert text.startswith("In allen 3.000 Fällen war der Anteil höchstens 1/2") and "ein Eintrag falsch, zwei Einträge einer Zeile (+1, −1)" in text and "1/1024 (0,001)" in text


def test_claim_random_errors_leave_two_to_the_minus_n_liars(freivalds):
    """README: bei einer ganz zufälligen Matrix lügt genau 1 Vektor von 2^n (1/64, 1/256, 1/1024)."""
    assert [next(r["max"] for r in freivalds if r["n"] == n and r["kind"] == "random") for n in (6, 8, 10)] == [F(1, 64), F(1, 256), F(1, 1024)]


# --- Befund 2: Verstärkung und Aufwand ---------------------------------------------------------------------------------------------------------


def test_claim_amplification_is_share_to_the_t():
    """README: (1/2)^t für t = 1, 2, 3, 4, 5, 8 = 1/2, 1/4, 1/8, 1/16, 1/32, 1/256; bei Anteil 1/2 gilt Anteil^t = (1/2)^t."""
    assert [A.error_after_rounds(F(1, 2), t) for t in (1, 2, 3, 4, 5, 8)] == [F(1, 2), F(1, 4), F(1, 8), F(1, 16), F(1, 32), F(1, 256)]


def test_claim_cost_freivalds_against_recomputing():
    """README: Freivalds kostet t · 3n² Multiplikationen, Nachrechnen n³; Gleichstand bei t = n / 3 (n = 12, t = 4: je 1.728; n = 30, t = 10: je 27.000); n = 100: 1.000.000 gegen 30.000 / 150.000 / 300.000 für t = 1 / 5 / 10."""
    for n, t in ((12, 4), (30, 10), (9, 3)):
        assert t * 3 * n * n == n ** 3
    assert [t * 3 * 100 * 100 for t in (1, 5, 10)] == [30_000, 150_000, 300_000] and 100 ** 3 == 1_000_000
    a = ev.analyse(ev.Settings(n=12, t=4))
    assert (a.matrix.mults_freivalds, a.matrix.mults_naive) == (1728, 1728)
    assert ev.verdict_matrix(a)[0] == "info"
    b = ev.analyse(ev.Settings(n=12, t=3))
    assert (b.matrix.mults_freivalds, b.matrix.mults_naive) == (1296, 1728) and ev.verdict_matrix(b)[0] == "success"


# --- Befund 3: Lügner der Zusammengesetzten ----------------------------------------------------------------------------------------------------

WORST = [(9, 2, 2), (1891, 450, 900), (703, 162, 324), (91, 18, 36), (2701, 486, 1296), (25, 4, 4), (1541, 242, 484), (341, 50, 100)]    # (n, starke Lügner, Fermat-Lügner)


@pytest.fixture(scope="module")
def liars():
    return ev.sweep_liars()


def test_claim_liar_sweep(liars):
    """README, Befund 3: 1.831 ungerade Zusammengesetzte von 9 bis 5.000, alle Basen 1 bis n − 1; die acht größten Anteile; Schranke 1/4 an keiner Zahl überschritten (n = 9 genau 1/4); 5 Zahlen mit Fermat-Anteil über 1/2."""
    assert (liars["count"], liars["limit"], liars["violations"]) == (1831, 5000, [])
    assert [(r["n"], r["strong"], r["fermat"]) for r in liars["worst"]] == WORST
    assert [r["strong_share"] for r in liars["worst"]][:4] == [F(1, 4), F(5, 21), F(3, 13), F(1, 5)]
    assert max(r["strong_share"] for r in liars["rows"] if r["n"] > 9) == F(5, 21)
    assert liars["fermat_over_half"] == [561, 1105, 1729, 2465, 2821]


def test_claim_typical_composites_have_almost_no_liars(liars):
    """README: Median 1/753 (0,13 %), Mittel 0,65 %; bei 1.261 von 1.831 Zahlen sind nur die beiden trivialen Basen 1 und n − 1 Lügner."""
    assert liars["median"] == F(1, 753) and ev.fmt_percent(liars["median"], 2) == "0,13 %" and ev.fmt_percent(liars["mean"], 2) == "0,65 %"
    assert sum(1 for r in liars["rows"] if r["strong"] == 2) == 1261


def test_claim_nine_is_exactly_one_quarter():
    """README: n = 9: die Basen 1 und 8 bestehen, 2 von 8 = 1/4 (die Schranke wird genau erreicht)."""
    assert A.strong_liars(9) == [1, 8] and F(len(A.strong_liars(9)), 8) == F(1, 4)


def test_claim_liar_verdict_text(liars):
    text = ev.verdict_liars(liars)[1]
    assert "Die schlimmsten: 9 (25 %), 1.891 (23,8 %), 703 (23,1 %), 91 (20 %)." in text and "Median 0,13 %, Mittel 0,65 %" in text and "bei 5 Zahlen über 1/2" in text


# --- Befund 4: Fermat gegen Miller–Rabin -------------------------------------------------------------------------------------------------------

CARMICHAEL = [   # n: (Faktoren, Fermat-Lügner, starke Lügner), Fermat-Lügner = φ(n)
    (561, (3, 11, 17), 320, 10), (1105, (5, 13, 17), 768, 30), (1729, (7, 13, 19), 1296, 162), (2465, (5, 17, 29), 1792, 70), (2821, (7, 13, 31), 2160, 270), (6601, (7, 23, 41), 5280, 330),
    (8911, (7, 19, 67), 7128, 1782), (10585, (5, 29, 73), 8064, 630), (15841, (7, 31, 73), 12960, 810), (29341, (13, 37, 61), 25920, 4050), (41041, (7, 11, 13, 41), 28800, 450), (46657, (13, 37, 97), 41472, 810),
]


@pytest.fixture(scope="module")
def carmichael():
    return ev.carmichael_table()


def test_claim_carmichael_table(carmichael):
    """README, Befund 4: die 12 Carmichael-Zahlen bis 50.000 (nach Korselt aus der Definition gerechnet); Fermat-Lügner = φ(n) = alle teilerfremden Basen."""
    assert [(r["n"], r["factors"], r["fermat"], r["strong"]) for r in carmichael] == CARMICHAEL
    assert all(r["fermat"] == r["phi"] and r["fermat_is_coprime"] for r in carmichael)


def test_claim_carmichael_shares(carmichael):
    """README: Fermat-Anteil 57,1 % (561) bis 88,9 % (46.657); starke Lügner 1,1 % (41.041) bis 20 % (8.911); 561: 10 von 560."""
    lo = min(carmichael, key=lambda r: r["fermat_share"])
    hi = max(carmichael, key=lambda r: r["fermat_share"])
    s_lo = min(carmichael, key=lambda r: r["strong_share"])
    s_hi = max(carmichael, key=lambda r: r["strong_share"])
    assert (lo["n"], ev.fmt_percent(lo["fermat_share"]), hi["n"], ev.fmt_percent(hi["fermat_share"])) == (561, "57,1 %", 46657, "88,9 %")
    assert (s_lo["n"], ev.fmt_percent(s_lo["strong_share"]), s_hi["n"], ev.fmt_percent(s_hi["strong_share"])) == (41041, "1,1 %", 8911, "20 %")
    assert ev.verdict_carmichael(carmichael)[1].startswith("Bei den 12 Carmichael-Zahlen bis 46.657 besteht den Fermat-Test ein Anteil von 57,1 % (n = 561) bis 88,9 % (n = 46657)")


# --- Befund 5: ein- gegen zweiseitiger Fehler ------------------------------------------------------------------------------------------------


def test_claim_two_sided_error_costs_more_rounds():
    """README, Befund 5: Mehrheitsentscheid bei Fehler 1/3 je Lauf: t = 1 / 3 / 5 → 1/3, 7/27, 17/81; für höchstens 1 % Fehler 47 Läufe, für 10^(−6) 193 Läufe; einseitig 1/2: 7 bzw. 20 Läufe."""
    res = ev.bpp_table()
    by = {r["t"]: r["majority"] for r in res["rows"]}
    assert (by[1], by[3], by[5]) == (F(1, 3), F(7, 27), F(17, 81))
    assert [ev.fmt_percent(by[t], 2) for t in (11, 21, 51, 101)] == ["12,21 %", "5,57 %", "0,69 %", "0,03 %"]
    need = {n["target"]: (n["majority"], n["one_sided"]) for n in res["needed"]}
    assert need == {F(1, 100): (47, 7), F(1, 1_000_000): (193, 20)}
    assert A.majority_error(47, F(1, 3)) <= F(1, 100) < A.majority_error(45, F(1, 3)) and A.majority_error(193, F(1, 3)) <= F(1, 1_000_000) < A.majority_error(191, F(1, 3))
    assert F(1, 2) ** 7 <= F(1, 100) < F(1, 2) ** 6 and F(1, 2) ** 20 <= F(1, 1_000_000) < F(1, 2) ** 19


# --- Presets (Einzelinstanzen) -----------------------------------------------------------------------------------------------------------------

# Preset: (lügende Vektoren, Vektoren, Multiplikationen Freivalds, Multiplikationen naiv, Zahl, starke Lügner, Fermat-Lügner, Carmichael, Multiplikationen Basis 2)
PRESETS = {
    "Standardfall (Voreinstellung)": (512, 1024, 900, 1000, 561, 10, 320, True, 10),
    "Lehrbeispiel (3 × 3)": (4, 8, 54, 27, 15, 2, 4, False, 4),
    "Strukturierter Fehler": (512, 1024, 900, 1000, 561, 10, 320, True, 10),
    "Zufälliger Fehler": (1, 1024, 900, 1000, 561, 10, 320, True, 10),
    "Carmichael-Zahl 1.729": (512, 1024, 900, 1000, 1729, 162, 1296, True, 12),
    "Zahl mit vielen Lügnern (1.891)": (512, 1024, 900, 1000, 1891, 450, 900, False, 14),
}


@pytest.mark.parametrize("name", list(PRESETS))
def test_claim_presets_are_single_instances_with_these_values(name):
    a = ev.analyse(ev.Settings(**C.PRESETS[name]))
    m, z = a.matrix, a.number
    assert (m.liars, m.total, m.mults_freivalds, m.mults_naive, z.num, len(z.strong), len(z.fermat), z.carmichael, z.mults_base_two) == PRESETS[name]
    assert ev.validation_errors(a) == []


def test_claim_standard_case_texts():
    """README: Standardfall: 512 von 1.024 Vektoren lügen (1/2), nach 3 Runden 1/8; 561: 10 von 560 (1,8 %) gegen 320 (57,1 %), nach 3 Basen höchstens 1/175616; 900 gegen 1.000 Multiplikationen; Stichprobe 1.207 von 10.000 (Illustration)."""
    a = ev.analyse(ev.Settings())
    kind, text = ev.verdict_matrix(a)
    assert kind == "success" and "512 den Test trotz des Fehlers (Anteil 1/2 (0,5))" in text and "1/8 (0,125)" in text and "1.207 Läufe (12,07 %)" in text and "900 Multiplikationen gegen 1.000" in text
    nkind, ntext = ev.verdict_number(a)
    assert nkind == "warning" and "10 von 560 Basen (Anteil 1,8 %, Schranke 25 %), den Fermat-Test 320 (Anteil 57,1 %)" in ntext and "1/175616 (5,7 · 10^(−6))" in ntext


def test_claim_preset_help_texts_quote_these_numbers():
    h = C.PRESET_HELP
    assert "10 von 560" in h["Standardfall (Voreinstellung)"] and "320" in h["Standardfall (Voreinstellung)"]
    assert "54 gegen 27" in h["Lehrbeispiel (3 × 3)"] and "8 Vektoren, 4 davon" in h["Lehrbeispiel (3 × 3)"]
    assert "1 von 1.024" in h["Zufälliger Fehler"] and "1.296 von 1.728" in h["Carmichael-Zahl 1.729"] and "162" in h["Carmichael-Zahl 1.729"]
    assert "450 von 1.890" in h["Zahl mit vielen Lügnern (1.891)"] and "23,8 %" in h["Zahl mit vielen Lügnern (1.891)"]
    assert ev.analyse(ev.Settings(**C.PRESETS["Zufälliger Fehler"])).matrix.after_t == F(1, 1024) ** 3                                  # 1/1073741824


def test_claim_hand_values_of_the_small_cases():
    """README (Handwerte): 3^13 mod 7 = 3 mit 5 Multiplikationen; 2^35 mod 561 = 263 (7 Multiplikationen), danach 3 Quadrate ohne −1: 561 fällt bei Basis 2 durch (10 Multiplikationen)."""
    assert A.mod_pow(3, 13, 7) == (3, 5) and A.mod_pow(2, 35, 561) == (263, 7)
    assert A.strong_test(561, 2) == (False, 10) and A.decompose(561) == (35, 4)
    assert A.is_carmichael(561) and [p for p in A.factorize(561) if 560 % (p - 1) != 0] == []
