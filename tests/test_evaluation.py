"""Auswertung: Kennzahlen an Handwerten, jeder Zweig von validation_errors (mit Grenzfällen), Messreihen gegen eine unabhängige Nachrechnung."""

import itertools
import math
from dataclasses import replace
from fractions import Fraction

import pytest

import zfv_algorithm as A
import zfv_constants as C
import zfv_evaluation as ev
from zfv_rng import SplitMix64
from zfv_scenario import random_matrix


def _base(**kw):
    return ev.analyse(ev.Settings(**kw))


def _errors(a):
    return ev.validation_errors(a)


# --- Kennzahlen an Handwerten --------------------------------------------------------------------------------------------------------------


def test_lehrbeispiel_matrix_part():
    m = ev.analyse_matrix(3, "one", 2, 2, 1000)
    assert (m.total, m.liars, m.share, m.after_t) == (8, 4, Fraction(1, 2), Fraction(1, 4))
    assert (m.mults_naive, m.mults_freivalds) == (27, 54)
    assert 0 <= m.sample_fails <= 1000


def test_number_part_for_561():
    z = ev.analyse_number(561, 3)
    assert (z.kind, z.factors, z.carmichael) == ("zusammengesetzt", (3, 11, 17), True)
    assert (len(z.strong), len(z.fermat)) == (10, 320) and z.strong_share == Fraction(10, 560) and z.fermat_share == Fraction(320, 560)
    assert z.after_t == Fraction(1, 56) ** 3 and z.mults_base_two == 10                      # 2^35 mod 561 mit 7 Multiplikationen, dann 3 Quadrate


def test_number_part_for_prime_even_and_nine():
    p = ev.analyse_number(13, 3)
    assert p.kind == "prim" and len(p.strong) == len(p.fermat) == 12 and p.after_t is None and not p.carmichael
    e = ev.analyse_number(100, 3)
    assert e.kind == "gerade" and e.factors == (2, 2, 5, 5) and e.strong == () and e.strong_share is None and e.mults_base_two is None
    nine = ev.analyse_number(9, 3)
    assert nine.strong == (1, 8) and nine.strong_share == Fraction(1, 4) and nine.after_t == Fraction(1, 64)


def test_analysis_uses_all_settings():
    a = _base(n=4, seed=7, kind="row", t=5, num=91, runs=1000)
    assert len(a.matrix.a) == 4 and a.matrix.total == 16 and a.matrix.mults_freivalds == 5 * 3 * 16 and a.number.num == 91 and a.number.after_t == a.number.strong_share ** 5


# --- validation_errors: Grundfall und jeder Zweig ----------------------------------------------------------------------------------------------


@pytest.mark.parametrize("kw", [{}, {"n": 2, "kind": "two_row"}, {"num": 13}, {"num": 100}, {"num": 9}, {"num": 2}, {"num": 3}, {"num": 1729, "kind": "random"}, {"n": 12, "kind": "row"}])
def test_valid_analyses_have_no_errors(kw):
    assert _errors(_base(**kw)) == []


def test_wrong_product_must_differ_and_c_true_must_be_the_product():
    a = _base()
    m = a.matrix
    assert any("nicht falsch" in e for e in _errors(replace(a, matrix=replace(m, c_wrong=m.c_true))))
    broken = tuple(tuple(x + (i == j == 0) for j, x in enumerate(row)) for i, row in enumerate(m.c_true))
    errs = _errors(replace(a, matrix=replace(m, c_true=broken)))
    assert any("nicht falsch" in e for e in errs) and any("richtiges Produkt besteht nicht jeden Vektor" in e for e in errs)


def test_liar_count_is_checked_against_the_second_route():
    a = _base()
    m = a.matrix
    assert any("zweiten Rechnung" in e for e in _errors(replace(a, matrix=replace(m, liars=m.liars + 1))))
    assert any("zweiten Rechnung" in e for e in _errors(replace(a, matrix=replace(m, liars=m.liars - 1))))
    assert any("zweiten Rechnung" in e for e in _errors(replace(a, matrix=replace(m, total=m.total + 1))))


def test_share_bound_one_half_is_allowed_but_not_more():
    a = _base()                                                                                  # Standardfall: genau 1/2
    assert a.matrix.share == Fraction(1, 2) and _errors(a) == []
    errs = _errors(replace(a, matrix=replace(a.matrix, share=Fraction(1, 2) + Fraction(1, 1024))))
    assert any("größer als 1/2" in e for e in errs)


def test_sample_must_lie_within_the_runs():
    a = _base(runs=1000)
    m = a.matrix
    assert any("mehr Fehlschläge als Läufe" in e for e in _errors(replace(a, matrix=replace(m, sample_fails=1001))))
    assert any("mehr Fehlschläge als Läufe" in e for e in _errors(replace(a, matrix=replace(m, sample_fails=-1))))
    assert not any("mehr Fehlschläge" in e for e in _errors(replace(a, matrix=replace(m, sample_fails=1000))))


def test_sample_tolerance_is_six_sigma_at_exactly_1000_runs():
    a = _base(runs=1000, kind="one", t=3)                                                       # p = 1/8
    p = 1 / 8
    limit = p * 1000 + 6 * math.sqrt(p * (1 - p) * 1000)
    inside, outside = math.floor(limit), math.floor(limit) + 1
    assert outside > limit >= inside
    assert not any("Standardabweichungen" in e for e in _errors(replace(a, matrix=replace(a.matrix, sample_fails=inside))))
    assert any("Standardabweichungen" in e for e in _errors(replace(a, matrix=replace(a.matrix, sample_fails=outside))))
    low = math.ceil(p * 1000 - 6 * math.sqrt(p * (1 - p) * 1000))
    assert not any("Standardabweichungen" in e for e in _errors(replace(a, matrix=replace(a.matrix, sample_fails=low))))
    assert any("Standardabweichungen" in e for e in _errors(replace(a, matrix=replace(a.matrix, sample_fails=low - 1))))


def test_sample_is_not_checked_below_1000_runs():
    a = _base(runs=999)
    assert not any("Standardabweichungen" in e for e in _errors(replace(a, matrix=replace(a.matrix, sample_fails=999))))


def test_sample_check_with_zero_probability_still_works():
    a = _base(runs=1000, num=13)
    zero = replace(a.matrix, share=Fraction(0), after_t=Fraction(0), sample_fails=0)
    assert not any("Standardabweichungen" in e for e in _errors(replace(a, matrix=zero)))        # 6σ = 0: eine Abweichung wird bei p = 0 erst ab 1 Lauf gemeldet
    assert any("Standardabweichungen" in e for e in _errors(replace(a, matrix=replace(zero, sample_fails=1))))


def test_class_is_checked_against_trial_division():
    a = _base(num=561)
    assert any("Probedivision" in e for e in _errors(replace(a, number=replace(a.number, kind="prim"))))
    b = _base(num=13)
    assert any("Probedivision" in e for e in _errors(replace(b, number=replace(b.number, kind="zusammengesetzt"))))
    c = _base(num=100)
    assert any("Probedivision" in e for e in _errors(replace(c, number=replace(c.number, kind="zusammengesetzt"))))
    d = _base(num=15)
    assert any("Probedivision" in e for e in _errors(replace(d, number=replace(d.number, kind="gerade"))))


def test_primes_must_pass_every_base():
    a = _base(num=13)
    z = a.number
    assert any("jede Basis" in e for e in _errors(replace(a, number=replace(z, strong=z.strong[:-1]))))
    assert any("jede Basis" in e for e in _errors(replace(a, number=replace(z, fermat=z.fermat[:-1]))))


def test_composite_share_bound_one_quarter_is_allowed_but_not_more_also_for_nine():
    a = _base(num=561)
    z = a.number
    assert not any("1/4" in e for e in _errors(replace(a, number=replace(z, strong_share=Fraction(1, 4)))))
    assert any("1/4" in e for e in _errors(replace(a, number=replace(z, strong_share=Fraction(1, 4) + Fraction(1, 10000)))))
    nine = _base(num=9)
    assert nine.number.strong_share == Fraction(1, 4) and _errors(nine) == []                                  # n = 9 erreicht die Schranke genau
    assert any("1/4" in e for e in _errors(replace(nine, number=replace(nine.number, strong_share=Fraction(1, 2)))))        # keine Ausnahme für n = 9
    ten = _base(num=15)
    assert any("1/4" in e for e in _errors(replace(ten, number=replace(ten.number, strong_share=Fraction(1, 3)))))


def test_every_strong_liar_must_be_a_fermat_liar():
    a = _base(num=561)
    z = a.number
    assert any("kein Fermat-Lügner" in e for e in _errors(replace(a, number=replace(z, fermat=z.fermat[1:]))))                    # Basis 1 fehlt


def test_carmichael_flag_must_agree_with_korselt_and_with_the_coprime_bases():
    a = _base(num=561)
    z = a.number
    assert any("Korselt" in e for e in _errors(replace(a, number=replace(z, carmichael=False))))
    b = _base(num=15)
    assert any("Korselt" in e for e in _errors(replace(b, number=replace(b.number, carmichael=True))))
    assert any("teilerfremden" in e for e in _errors(replace(a, number=replace(z, fermat=tuple(x for x in z.fermat if x != 2)))))
    assert not any("teilerfremden" in e for e in _errors(replace(b, number=replace(b.number, carmichael=False))))                  # nur bei Carmichael-Zahlen


# --- sample_failures --------------------------------------------------------------------------------------------------------------------


def test_sample_failures_extremes_and_determinism():
    n, runs = 4, 500
    assert ev.sample_failures([True] * 16, n, 3, runs, 1) == runs
    assert ev.sample_failures([False] * 16, n, 3, runs, 1) == 0
    half = [i % 2 == 0 for i in range(16)]
    assert ev.sample_failures(half, n, 1, runs, 5) == ev.sample_failures(half, n, 1, runs, 5)
    assert ev.sample_failures(half, n, 1, runs, 5) != ev.sample_failures(half, n, 1, runs, 6)
    assert 200 <= ev.sample_failures(half, n, 1, runs, 5) <= 300
    assert ev.sample_failures(half, n, 3, 4000, 5) < ev.sample_failures(half, n, 1, 4000, 5)                                       # mehr Runden, weniger Fehlschläge


def test_sample_failures_draws_every_vector_index():
    seen = set()
    mask_hits = []
    for idx in range(16):
        mask = [i == idx for i in range(16)]
        mask_hits.append(ev.sample_failures(mask, 4, 1, 800, 3))
        seen.add(idx)
    assert all(h > 0 for h in mask_hits)                                                          # jeder der 16 Vektoren wird gezogen
    assert sum(mask_hits) == 800                                                                  # jeder Lauf zieht genau einen Vektor


# --- Messreihen gegen eine unabhängige Nachrechnung -------------------------------------------------------------------------------------------


def _pure_share(a, b, c):
    n = len(a)
    lying = sum(1 for r in itertools.product((0, 1), repeat=n) if A.freivalds_round(a, b, c, list(r))[0])
    return Fraction(lying, 1 << n)


def test_sweep_freivalds_matches_a_pure_python_recount():
    kinds = tuple(C.KINDS)
    rows = ev.sweep_freivalds(sizes=(2, 3, 4), pairs=6, seed=77)
    assert len(rows) == 3 * len(kinds)
    for n in (2, 3, 4):
        rng = SplitMix64(77 + n)
        per = {k: [] for k in kinds}
        for _ in range(6):
            a, b = random_matrix(n, rng), random_matrix(n, rng)
            c = A.product(a, b)
            for k in kinds:
                if k in ("two_row", "two_rows") and n < 2:
                    continue
                per[k].append(_pure_share(a, b, A.corrupt(c, k, rng)))
        for k in kinds:
            row = next(r for r in rows if r["n"] == n and r["kind"] == k)
            v = per[k]
            assert (row["min"], row["max"], row["mean"]) == (min(v), max(v), sum(v) / len(v)), (n, k)
            assert row["at_half"] == sum(x == Fraction(1, 2) for x in v) and row["above_half"] == sum(x > Fraction(1, 2) for x in v) and row["pairs"] == 6


def test_sweep_freivalds_structure_facts():
    rows = ev.sweep_freivalds(sizes=(5,), pairs=20, seed=3)
    by = {r["kind"]: r for r in rows}
    assert by["one"]["at_half"] == 20 and by["two_row"]["at_half"] == 20                         # genau 1/2: ein Eintrag bzw. zwei in einer Zeile
    assert all(r["above_half"] == 0 for r in rows)
    assert by["random"]["max"] < Fraction(1, 2)


def _liars_by_definition(n):
    """Unabhängige Zählung: Miller–Rabin als Definition mit wiederholter Multiplikation (kein pow)."""
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    count = 0
    for a in range(1, n):
        x = 1
        for _ in range(d):
            x = x * a % n
        ok = x in (1, n - 1)
        for _ in range(s - 1):
            if ok:
                break
            x = x * x % n
            ok = x == n - 1
        count += ok
    return count


def test_sweep_liars_matches_the_definition_and_hand_values():
    res = ev.sweep_liars(limit=300)
    ns = [r["n"] for r in res["rows"]]
    assert ns == [n for n in range(9, 301, 2) if not A.is_prime_trial(n)] and res["count"] == len(ns) and res["limit"] == 300
    for r in res["rows"]:
        assert r["strong"] == _liars_by_definition(r["n"]), r["n"]
        assert r["strong_share"] == Fraction(r["strong"], r["n"] - 1) and r["fermat_share"] == Fraction(r["fermat"], r["n"] - 1)
    first = res["rows"][0]
    assert (first["n"], first["strong"]) == (9, 2) and res["violations"] == []
    assert res["worst"][0]["n"] == 9 and len(res["worst"]) == 8
    shares = sorted(r["strong_share"] for r in res["rows"])
    assert res["median"] == (shares[len(shares) // 2] if len(shares) % 2 else (shares[len(shares) // 2 - 1] + shares[len(shares) // 2]) / 2)
    assert res["mean"] == sum(shares) / len(shares)
    assert [r["strong_share"] for r in res["worst"]] == sorted((r["strong_share"] for r in res["rows"]), reverse=True)[:8]
    over = [n for n in ns if 2 * sum(1 for a in range(1, n) if a ** (n - 1) % n == 1) > n - 1]
    assert res["fermat_over_half"] == over and 15 not in over
    assert 561 in ev.sweep_liars(limit=600)["fermat_over_half"]


def test_sweep_liars_ties_are_ordered_by_n():
    worst = ev.sweep_liars(limit=300)["worst"]
    for x, y in zip(worst, worst[1:]):
        assert (-x["strong_share"], x["n"]) < (-y["strong_share"], y["n"])


def test_carmichael_table_hand_values():
    rows = ev.carmichael_table(3000)
    assert [r["n"] for r in rows] == [561, 1105, 1729, 2465, 2821]
    phi = {561: 2 * 10 * 16, 1105: 4 * 12 * 16, 1729: 6 * 12 * 18, 2465: 4 * 16 * 28, 2821: 6 * 12 * 30}
    for r in rows:
        assert r["phi"] == phi[r["n"]] == r["fermat"] and r["fermat_is_coprime"]
        assert r["fermat_share"] == Fraction(r["fermat"], r["n"] - 1) and r["strong_share"] == Fraction(r["strong"], r["n"] - 1)
        assert r["strong"] == _liars_by_definition(r["n"]) and math.prod(r["factors"]) == r["n"]
    assert rows[0]["strong"] == 10 and rows[2]["strong"] == 162


def test_bpp_table_hand_values():
    res = ev.bpp_table()
    by = {r["t"]: r for r in res["rows"]}
    assert by[1]["majority"] == Fraction(1, 3) and by[3]["majority"] == Fraction(7, 27) and by[5]["majority"] == Fraction(17, 81)
    assert all(r["one_sided"] == Fraction(1, 2 ** r["t"]) for r in res["rows"]) and [r["t"] for r in res["rows"]] == list(C.BPP_TS)
    need = {n["target"]: n for n in res["needed"]}
    assert need[Fraction(1, 100)]["one_sided"] == 7 and need[Fraction(1, 1_000_000)]["one_sided"] == 20
    assert need[Fraction(1, 100)]["majority"] == 47 and need[Fraction(1, 1_000_000)]["majority"] == 193


# --- Zusammenfassung der Lügner-Messreihe an handgesetzten Zeilen ------------------------------------------------------------------------------


def _rows(*triples):
    return [{"n": n, "strong": strong, "fermat": fermat} for n, strong, fermat in triples]


def test_summary_thresholds_are_strict_at_exactly_one_quarter_and_one_half():
    res = ev.summarise_liars(_rows((9, 2, 4), (25, 6, 12), (21, 7, 10), (15, 2, 7), (27, 5, 14)), 27)
    assert res["violations"] == [21]                                           # 9: 2/8 und 25: 6/24 sind genau 1/4 (erlaubt), 21: 7/20 darüber
    assert res["fermat_over_half"] == [27]                                     # 9, 25, 21, 15: genau 1/2 (nicht darüber), 27: 14/26 darüber
    assert res["count"] == 5 and res["limit"] == 27


def test_summary_has_no_exemption_for_nine():
    assert ev.summarise_liars(_rows((9, 3, 4)), 9)["violations"] == [9]
    assert ev.summarise_liars(_rows((9, 2, 4)), 9)["violations"] == []


def test_summary_worst_median_and_mean():
    res = ev.summarise_liars(_rows((9, 2, 2), (15, 2, 4), (21, 4, 6), (25, 4, 4), (27, 3, 3)), 27)
    assert [r["n"] for r in res["worst"]] == [9, 21, 25, 15, 27]               # Anteile 1/4, 1/5, 1/6, 1/7, 3/26 (< 1/7)
    assert res["median"] == Fraction(1, 6) and res["mean"] == (Fraction(1, 4) + Fraction(1, 7) + Fraction(1, 5) + Fraction(1, 6) + Fraction(3, 26)) / 5
    assert len(ev.summarise_liars(_rows(*[(2 * k + 9, 2, 2) for k in range(12)]), 40)["worst"]) == 8


def test_sweep_liars_includes_the_limit_if_it_is_an_odd_composite():
    assert [r["n"] for r in ev.sweep_liars(limit=25)["rows"]][-1] == 25
    assert [r["n"] for r in ev.sweep_liars(limit=24)["rows"]][-1] == 21
    assert [r["n"] for r in ev.sweep_liars(limit=9)["rows"]] == [9]
