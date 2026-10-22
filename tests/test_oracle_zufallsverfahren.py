"""Orakel (ORACLE-PLAYBOOK): unabhängige Gegenrechnungen und Sätze aus der Literatur gegen die ganze Demo.

* Miller–Rabin ein zweites Mal aus der Definition (wiederholte Multiplikation, kein `pow`) für alle ungeraden n bis 400 und alle Basen.
* Satz: Primzahlen bestehen jede Basis; der Anteil starker Lügner einer ungeraden Zusammengesetzten n > 9 ist höchstens 1/4 (Rabin; hier für alle n bis 2.000 gezählt).
* Satz (Korselt): n ist genau dann eine Carmichael-Zahl, wenn jede zu n teilerfremde Basis den Fermat-Test besteht (ungerade zusammengesetzte n bis 2.000).
* Freivalds: die aufgezählte Maske gleicht dem Durchgang `freivalds_round` je Vektor und dem ausmultiplizierten (AB − C)r = 0; ein richtiges Produkt besteht alle Vektoren, ein falsches höchstens die Hälfte.
* Mehrheitsentscheid: Binomialsumme gegen die Aufzählung aller 2^t Ausgänge.
* Die Auswertung (`zfv_evaluation`) läuft über ein Raster von Einstellungen ohne Prüffehler."""

import itertools
import math
from fractions import Fraction

import pytest

import zfv_algorithm as A
import zfv_constants as C
import zfv_evaluation as ev
from zfv_rng import SplitMix64
from zfv_scenario import make_instance


def _strong_by_definition(n, a):
    """n − 1 = d · 2^s. Besteht, wenn a^d ≡ 1 oder a^(d·2^r) ≡ −1 für ein r mit 0 ≤ r < s (wiederholte Multiplikation, kein pow)."""
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    x = 1
    for _ in range(d):
        x = x * a % n
    if x == 1:
        return True
    for _ in range(s):
        if x == n - 1:
            return True
        x = x * x % n
    return False


def test_strong_test_agrees_with_the_definition_for_all_odd_n_and_bases():
    for n in range(3, 401, 2):
        for a in range(1, n):
            expected = _strong_by_definition(n, a)
            assert A.strong_test(n, a)[0] == A.strong_pass(n, a) == expected, (n, a)


def test_mod_pow_matches_builtin_pow():
    rng = SplitMix64(11)
    for _ in range(300):
        n, a, e = 2 + rng.below(5000), rng.below(5000), rng.below(3000)
        assert A.mod_pow(a, e, n)[0] == pow(a, e, n)


def test_primes_pass_every_base_and_composites_obey_rabins_bound():
    for n in range(3, 2001, 2):
        liars = A.strong_liars(n)
        if A.is_prime_trial(n):
            assert len(liars) == n - 1, n
        elif n > 9:
            assert 4 * len(liars) <= n - 1, n
        else:
            assert 4 * len(liars) == n - 1                                              # n = 9: genau 1/4


def test_korselt_numbers_are_exactly_the_composites_all_of_whose_coprime_bases_lie():
    korselt = {n for n in range(3, 2001, 2) if A.is_carmichael(n)}
    by_fermat = {n for n in range(3, 2001, 2) if not A.is_prime_trial(n) and all(pow(a, n - 1, n) == 1 for a in range(1, n) if math.gcd(a, n) == 1)}
    assert korselt == by_fermat == {561, 1105, 1729}


def test_the_demo_pipeline_agrees_for_the_three_carmichael_numbers():
    for n in (561, 1105, 1729):
        a = ev.analyse_number(n, 3)
        assert a.carmichael and set(a.fermat) == {x for x in range(1, n) if math.gcd(x, n) == 1}


def _vectors(n):
    return list(itertools.product((0, 1), repeat=n))


@pytest.mark.parametrize("n", [2, 3, 4, 5, 6])
@pytest.mark.parametrize("kind", list(C.KINDS))
def test_mask_equals_the_round_for_each_vector_and_the_full_product(n, kind):
    for seed in range(8):
        inst = make_instance(n, kind, seed)
        count, mask = A.liar_vectors(inst.a, inst.b, inst.c_wrong)
        vectors = _vectors(n)
        ab = A.product(inst.a, inst.b)
        assert ab == [list(r) for r in inst.c_true]
        for idx, r in enumerate(vectors):
            ok = A.freivalds_round(inst.a, inst.b, inst.c_wrong, list(r))[0]
            direct = all(sum((ab[i][j] - inst.c_wrong[i][j]) * r[j] for j in range(n)) == 0 for i in range(n))
            assert bool(mask[idx]) == ok == direct, (n, kind, seed, idx)
        assert count == int(sum(mask)) and 2 * count <= 1 << n                           # höchstens die Hälfte (Freivalds)
        assert A.liar_vectors(inst.a, inst.b, inst.c_true)[0] == 1 << n                  # richtig: alle Vektoren


def test_a_wrong_product_never_passes_more_than_half_over_many_instances():
    checked = 0
    for n in range(2, 8):
        for kind in C.KINDS:
            for seed in range(25):
                inst = make_instance(n, kind, 1000 + seed)
                assert inst.c_wrong != inst.c_true
                count = A.liar_vectors(inst.a, inst.b, inst.c_wrong)[0]
                assert 2 * count <= 1 << n
                checked += 1
    assert checked >= 600


def test_round_cost_is_three_n_squared():
    for n in (1, 2, 5, 9):
        a = [[1] * n for _ in range(n)]
        assert A.freivalds_round(a, a, A.product(a, a), [1] * n)[1] == 3 * n * n


def test_majority_error_equals_the_enumeration_of_all_outcomes():
    p = Fraction(1, 3)
    for t in range(1, 16, 2):
        total = Fraction(0)
        for outcome in itertools.product((0, 1), repeat=t):                               # 1 = der Lauf irrt
            k = sum(outcome)
            if 2 * k > t:
                total += p ** k * (1 - p) ** (t - k)
        assert A.majority_error(t, p) == total, t


def test_majority_error_decreases_with_runs():
    errs = [A.majority_error(t, Fraction(1, 3)) for t in range(1, 40, 2)]
    assert all(x > y for x, y in zip(errs, errs[1:]))


def test_amplification_helpers_are_exact():
    assert A.error_after_rounds(Fraction(1, 2), 10) == Fraction(1, 1024)
    assert A.one_sided_rounds(Fraction(1, 100)) == 7 and A.one_sided_rounds(Fraction(1, 128)) == 7 and A.one_sided_rounds(Fraction(1, 129)) == 8
    assert A.rounds_needed(Fraction(1, 3), Fraction(1, 3)) == 1


def test_the_evaluation_runs_over_a_grid_without_validation_errors():
    nums = (3, 4, 9, 15, 25, 91, 341, 561, 563, 1105, 1729, 1891, 4999)
    for i, num in enumerate(nums):
        for kind in C.KINDS:
            n = 2 + (i % 8)
            a = ev.analyse(ev.Settings(n=n, seed=10 + i, kind=kind, t=1 + i % 5, num=num, runs=1000))
            assert ev.validation_errors(a) == [], (num, kind)
            assert ev.verdict_matrix(a)[0] in ("success", "info") and ev.verdict_number(a)[0] in ("info", "warning")


def test_the_full_sweeps_hold_the_bounds():
    res = ev.sweep_liars()
    assert res["violations"] == [] and res["count"] > 1800
    rows = ev.sweep_freivalds()
    assert all(r["above_half"] == 0 for r in rows)
    assert ev.verdict_freivalds_sweep(rows)[0] == "success" and ev.verdict_liars(res)[0] == "info"
    assert A.carmichael_numbers(C.CARMICHAEL_LIMIT)[:4] == [561, 1105, 1729, 2465]
