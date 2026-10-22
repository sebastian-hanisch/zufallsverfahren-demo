"""Verdikte und Zahlenformate an von Hand gesetzten Werten (DEMO-PLAYBOOK §12): jede Zahl im Text und jede Schwelle der Art steht hier.

Ein Verdikt ist eine reine Funktion (Art, Text) und bekommt Zeilen, nicht Seeds. Damit prüft der Test die Grenzen und jede genannte Zahl direkt."""

from fractions import Fraction

import zfv_evaluation as ev


def _matrix(liars=512, total=1024, after_t=Fraction(1, 8), sample=1207, naive=1000, freivalds=900):
    return ev.MatrixPart(((1,),), ((1,),), ((1,),), ((2,),), liars, total, Fraction(liars, total), after_t, sample, naive, freivalds)


def _number(num=561, kind="zusammengesetzt", factors=(3, 11, 17), strong=10, fermat=320, carmichael=True, mults=10):
    share = Fraction(strong, num - 1) if kind != "gerade" else None
    return ev.NumberPart(num, kind, factors, tuple(range(1, strong + 1)), tuple(range(1, fermat + 1)), share, Fraction(fermat, num - 1) if kind != "gerade" else None,
                         share ** 3 if kind == "zusammengesetzt" else None, carmichael, mults if kind != "gerade" else None)


def _analysis(m=None, z=None, t=3, runs=10_000, n=10):
    return ev.Analysis(ev.Settings(n=n, t=t, runs=runs), m or _matrix(), z or _number())


# --- Formate ------------------------------------------------------------------------------------------------------------------------------


def test_number_formats():
    assert ev.fmt_int(131071) == "131.071" and ev.fmt_int(12) == "12"
    assert ev.fmt_num(22.7) == "22,7" and ev.fmt_num(3, 2) == "3,00"
    assert ev.fmt_median(1234) == "1.234" and ev.fmt_median(52.5) == "52,5"


def test_fmt_fraction():
    assert ev.fmt_fraction(Fraction(1, 2)) == "1/2 (0,5)" and ev.fmt_fraction(Fraction(1, 256)) == "1/256 (0,0039)" and ev.fmt_fraction(Fraction(1, 3)) == "1/3 (0,3333)"
    assert ev.fmt_fraction(Fraction(2, 3)) == "2/3 (0,6667)" and ev.fmt_fraction(Fraction(3)) == "3" and ev.fmt_fraction(Fraction(0)) == "0" and ev.fmt_fraction(Fraction(1, 8)) == "1/8 (0,125)"
    assert ev.fmt_fraction(Fraction(1, 10000)) == "1/10000 (0,0001)"                                  # genau an der Grenze: noch Dezimalschreibweise
    assert ev.fmt_fraction(Fraction(1, 10001)) == "1/10001 (1,0 · 10^(−4))"                           # darunter: Zehnerpotenz
    assert ev.fmt_fraction(Fraction(1, 175616)) == "1/175616 (5,7 · 10^(−6))"
    assert ev.fmt_fraction(Fraction(1, 3), digits=2) == "1/3 (0,33)"


def test_fmt_percent():
    assert ev.fmt_percent(Fraction(1, 4)) == "25 %" and ev.fmt_percent(Fraction(4, 7)) == "57,1 %" and ev.fmt_percent(Fraction(1, 1000)) == "0,1 %"
    assert ev.fmt_percent(Fraction(13, 10000), 2) == "0,13 %" and ev.fmt_percent(Fraction(1)) == "100 %"


# --- Verdikte -----------------------------------------------------------------------------------------------------------------------------


def test_verdict_matrix_names_exact_share_amplification_sample_and_cost():
    kind, text = ev.verdict_matrix(_analysis())
    assert kind == "success"
    assert "Von 1.024 Vektoren aus {0, 1}^10 bestehen 512 den Test trotz des Fehlers (Anteil 1/2 (0,5)); der Fehler wird mit Wahrscheinlichkeit 1/2 (0,5) entdeckt." in text
    assert "Nach 3 Runden bleibt er mit Wahrscheinlichkeit 1/8 (0,125) unentdeckt; Stichprobe (10.000 Läufe, Illustration): 1.207 Läufe (12,07 %) unentdeckt." in text
    assert "Aufwand: 900 Multiplikationen gegen 1.000 beim Nachrechnen. Freivalds ist hier billiger." in text


def test_verdict_matrix_grammar_for_a_single_liar():
    m = _matrix(liars=1, after_t=Fraction(1, 1024) ** 3, sample=0)
    text = ev.verdict_matrix(_analysis(m=m))[1]
    assert "Von 1.024 Vektoren aus {0, 1}^10 besteht 1 den Test trotz des Fehlers (Anteil 1/1024 (0,001))" in text and "1023/1024 (0,999) entdeckt" in text
    assert "bestehen 2 den Test" in ev.verdict_matrix(_analysis(m=_matrix(liars=2)))[1]


def test_verdict_matrix_cost_boundary_and_the_bound():
    kind, text = ev.verdict_matrix(_analysis(m=_matrix(naive=900, freivalds=900)))
    assert kind == "info" and "Nachrechnen nicht teurer" in text and "billiger" not in text.replace("nicht teurer", "")
    assert ev.verdict_matrix(_analysis(m=_matrix(naive=901, freivalds=900)))[0] == "success"
    kind, text = ev.verdict_matrix(_analysis(m=_matrix(liars=513)))
    assert kind == "error" and "überschreitet die Schranke 1/2" in text
    assert ev.verdict_matrix(_analysis(m=_matrix(liars=512)))[0] != "error"                              # genau 1/2 ist erlaubt


def test_verdict_number_for_even_numbers():
    kind, text = ev.verdict_number(_analysis(z=_number(num=100, kind="gerade", factors=(2, 2, 5, 5), carmichael=False)))
    assert kind == "info" and text.startswith("100 ist gerade: zusammengesetzt (Teiler 2)")
    assert ev.verdict_number(_analysis(z=_number(num=2, kind="gerade", factors=(2,), carmichael=False)))[1] == "2 ist gerade und prim."


def test_verdict_number_for_primes_and_composites():
    kind, text = ev.verdict_number(_analysis(z=_number(num=563, kind="prim", factors=(563,), strong=562, fermat=562, carmichael=False, mults=11)))
    assert kind == "info" and "563 ist prim: sie besteht den Miller–Rabin-Test zu **jeder** der 562 Basen" in text and "Basis 2 kostet 11 Multiplikationen" in text
    kind, text = ev.verdict_number(_analysis())
    assert kind == "warning"
    assert "561 = 3 · 11 · 17 ist zusammengesetzt. Den Miller–Rabin-Test bestehen 10 von 560 Basen (Anteil 1,8 %, Schranke 25 %), den Fermat-Test 320 (Anteil 57,1 %)." in text
    assert "Nach 3 zufälligen Basen hält Miller–Rabin die Zahl höchstens mit Wahrscheinlichkeit 1/175616 (5,7 · 10^(−6)) für prim." in text and "Eine Carmichael-Zahl (Korselt)" in text
    plain = ev.verdict_number(_analysis(z=_number(num=15, factors=(3, 5), strong=2, fermat=4, carmichael=False)))[1]
    assert "15 = 3 · 5 ist zusammengesetzt" in plain and "Carmichael" not in plain


def _sweep_rows():
    rows = []
    for n in (6, 10):
        for kind in ("one", "two_row", "two_rows", "row", "random"):
            half = kind in ("one", "two_row")
            rows.append({"n": n, "kind": kind, "pairs": 200, "min": Fraction(1, 2) if half else Fraction(1, 2 ** n), "mean": Fraction(1, 2) if half else Fraction(1, 2 ** n),
                         "max": Fraction(1, 2) if half else Fraction(1, 2 ** n), "at_half": 200 if half else 0, "above_half": 0})
    return rows


def test_verdict_freivalds_sweep_names_the_tight_kinds_and_the_random_one():
    kind, text = ev.verdict_freivalds_sweep(_sweep_rows())
    assert kind == "success"
    assert "In allen 2.000 Fällen war der Anteil höchstens 1/2" in text and "Genau 1/2 war er bei jedem Paar für: ein Eintrag falsch, zwei Einträge einer Zeile (+1, −1)." in text
    assert "Bei einer ganz zufälligen Matrix lag er bei n = 10 bei 1/1024 (0,001)" in text


def test_verdict_freivalds_sweep_lists_the_tight_kinds_of_the_smallest_size_only():
    rows = _sweep_rows()
    for r in rows:
        if r["n"] == 10 and r["kind"] == "row":
            r["at_half"] = r["pairs"]                                                                 # nur bei n = 10 genau 1/2: darf nicht in der Aufzählung stehen
    text = ev.verdict_freivalds_sweep(rows)[1]
    assert "bei jedem Paar für: ein Eintrag falsch, zwei Einträge einer Zeile (+1, −1). Bei einer" in text and "ganze Zeile" not in text


def test_verdict_freivalds_sweep_reports_violations():
    rows = _sweep_rows()
    rows[0] = dict(rows[0], above_half=2)
    kind, text = ev.verdict_freivalds_sweep(rows)
    assert kind == "error" and "in 2 von 2.000 Fällen" in text


def _liars_res(violations=()):
    def row(n, strong):
        return {"n": n, "strong": strong, "fermat": 0, "strong_share": Fraction(strong, n - 1), "fermat_share": Fraction(0)}
    rows = [row(9, 2), row(1891, 450), row(703, 162), row(91, 18), row(15, 2)]
    worst = sorted(rows, key=lambda r: (-r["strong_share"], r["n"]))
    return {"limit": 5000, "count": 1831, "rows": rows, "worst": worst, "median": Fraction(13, 10000), "mean": Fraction(65, 10000), "violations": list(violations), "fermat_over_half": [561, 1105]}


def test_verdict_liars_names_worst_and_typical():
    kind, text = ev.verdict_liars(_liars_res())
    assert kind == "info"
    assert "Alle 1.831 ungeraden Zusammengesetzten von 9 bis 5.000" in text and "höchstens 25 % (n = 9; für n > 9 ist es höchstens 23,8 %)" in text
    assert "Die schlimmsten: 9 (25 %), 1.891 (23,8 %), 703 (23,1 %), 91 (20 %)." in text and "Median 0,13 %, Mittel 0,65 %" in text and "bei 2 Zahlen über 1/2" in text


def test_verdict_liars_reports_violations_as_error():
    kind, text = ev.verdict_liars(_liars_res(violations=(21, 25)))
    assert kind == "error" and "bei 2 Zahlen überschritten" in text


def _carm_rows(coprime=True):
    def row(n, factors, fermat, strong, phi):
        return {"n": n, "factors": factors, "fermat": fermat, "strong": strong, "phi": phi, "fermat_share": Fraction(fermat, n - 1), "strong_share": Fraction(strong, n - 1), "fermat_is_coprime": coprime}
    return [row(561, (3, 11, 17), 320, 10, 320), row(8911, (7, 19, 67), 7128, 1782, 7128), row(46657, (13, 37, 97), 41472, 810, 41472)]


def test_verdict_carmichael_names_extremes():
    kind, text = ev.verdict_carmichael(_carm_rows())
    assert kind == "warning"
    assert "Bei den 3 Carmichael-Zahlen bis 46.657 besteht den Fermat-Test ein Anteil von 57,1 % (n = 561) bis 88,9 % (n = 46657) der Basen" in text
    assert "Miller–Rabin bleibt bei höchstens 20 % (n = 8911)" in text and "genau die zu n teilerfremden Basen" in text
    assert "Nicht überall" in ev.verdict_carmichael(_carm_rows(coprime=False))[1]


def test_verdict_bpp_names_the_price_of_two_sidedness():
    kind, text = ev.verdict_bpp(ev.bpp_table())
    assert kind == "info"
    assert "braucht 47 Läufe für höchstens 1 % Fehler und 193 für höchstens 10^(−6)" in text and "einseitiger Fehler je Lauf 1/2 (RP) genügt mit 7 bzw. 20 Läufen" in text
