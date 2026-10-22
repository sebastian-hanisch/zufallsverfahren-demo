"""Einheiten des Kerns an Mini-Instanzen von Hand (DEMO-PLAYBOOK §1b): jede Einheit ist eine Funktion, jede hat einen Handwert."""

from fractions import Fraction

import pytest

import zfv_algorithm as A
from zfv_rng import SplitMix64


# --- Potenz, Zerlegung ---------------------------------------------------------------------------------------------------------------------


def test_mod_pow_hand_values():
    """3^13 mod 7: 13 = 1101 binär; Start 3, Bit 1: Quadrat 2, mal 3 = 6; Bit 0: Quadrat 1; Bit 1: Quadrat 1, mal 3 = 3: Ergebnis 3, 5 Multiplikationen (3^6 = 1 mod 7, also 3^13 = 3)."""
    assert A.mod_pow(3, 13, 7) == (3, 5)
    assert A.mod_pow(5, 0, 7) == (1, 0) and A.mod_pow(5, 1, 7) == (5, 0) and A.mod_pow(10, 1, 7) == (3, 0)
    assert A.mod_pow(2, 10, 1000) == (24, 4)                         # 10 = 1010: Bit 0: Quadrat; Bit 1: Quadrat, mal; Bit 0: Quadrat: 1 + 2 + 1 = 4 Multiplikationen; 1024 mod 1000 = 24
    assert A.mod_pow(5, 3, 1)[0] == 0
    with pytest.raises(ValueError):
        A.mod_pow(2, -1, 7)


def test_mod_pow_matches_pow_and_counts_logarithmically():
    for a, e, n in ((2, 100, 97), (7, 560, 561), (123, 4999, 5003), (3, 2 ** 20, 1000003)):
        value, mults = A.mod_pow(a, e, n)
        assert value == pow(a, e, n) and e.bit_length() - 1 <= mults <= 2 * (e.bit_length() - 1)


def test_decompose_hand_values():
    assert A.decompose(9) == (1, 3) and A.decompose(15) == (7, 1) and A.decompose(17) == (1, 4) and A.decompose(561) == (35, 4)
    d, s = A.decompose(1729)
    assert d * 2 ** s == 1728 and d % 2 == 1
    with pytest.raises(ValueError):
        A.decompose(8)
    with pytest.raises(ValueError):
        A.decompose(1)


# --- Miller–Rabin und Fermat -------------------------------------------------------------------------------------------------------------


def test_strong_pass_hand_values():
    """n = 9: n − 1 = 8 = 1 · 2^3. Basis 8 = −1: 8^1 = 8 = n − 1, besteht. Basis 2: 2, dann 4, dann 16 mod 9 = 7, nie 1 oder 8: besteht nicht. Basis 3: 3, dann 0, dann 0: besteht nicht. Basis 1 besteht immer."""
    assert A.strong_pass(9, 8) and A.strong_pass(9, 1) and not A.strong_pass(9, 2) and not A.strong_pass(9, 3)
    assert A.strong_liars(9) == [1, 8]
    assert A.strong_liars(15) == [1, 14] and A.strong_liars(21) == [1, 20] and A.strong_liars(25) == [1, 7, 18, 24]


def test_primes_pass_every_base_and_even_or_out_of_range_input_is_rejected():
    for p in (3, 5, 7, 13, 97, 563):
        assert A.strong_liars(p) == list(range(1, p))
    with pytest.raises(ValueError):
        A.strong_pass(10, 3)
    with pytest.raises(ValueError):
        A.strong_pass(9, 0)
    with pytest.raises(ValueError):
        A.strong_pass(9, 9)


def test_strong_test_counts_multiplications():
    passed, mults = A.strong_test(9, 8)
    assert passed and mults == 0                                    # d = 1: a^1 ohne Multiplikation, schon n − 1
    passed, mults = A.strong_test(9, 2)
    assert not passed and mults == 2                                 # zwei Quadrate nach a^1
    passed, mults = A.strong_test(561, 2)
    assert not passed and mults >= 5


def test_fermat_liars_hand_values():
    """n = 15: a^14 ≡ 1 (mod 15) für a = 1, 4, 11, 14 (4^2 = 1, 11^2 = 1, 14 = −1); 2, 7, 8, 13 haben Ordnung 4 und scheitern; Basen mit gemeinsamem Teiler mit 15 scheitern immer."""
    assert A.fermat_liars(15) == [1, 4, 11, 14]
    assert A.fermat_liars(9) == [1, 8]
    assert A.fermat_pass(15, 4) and not A.fermat_pass(15, 2) and not A.fermat_pass(15, 3)


def test_liar_shares_are_fractions_over_the_bases_one_to_n_minus_one():
    assert A.liar_shares(9) == (Fraction(2, 8), Fraction(2, 8))
    assert A.liar_shares(15) == (Fraction(2, 14), Fraction(4, 14))
    assert A.liar_shares(13) == (Fraction(1), Fraction(1))


def test_is_prime_trial():
    assert [n for n in range(0, 30) if A.is_prime_trial(n)] == [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    assert A.is_prime_trial(563) and not A.is_prime_trial(561) and not A.is_prime_trial(1) and not A.is_prime_trial(-7)


def test_factorization_and_korselt():
    assert A.factorize(561) == [3, 11, 17] and A.factorize(1) == [] and A.factorize(12) == [2, 2, 3] and A.factorize(97) == [97]
    assert A.is_carmichael(561) and A.is_carmichael(1105) and A.is_carmichael(1729)
    assert not A.is_carmichael(15) and not A.is_carmichael(9) and not A.is_carmichael(563) and not A.is_carmichael(1)
    assert not A.is_carmichael(1024) and not A.is_carmichael(91)           # 91 = 7 · 13: nur zwei Primfaktoren (6 teilt 90, 12 nicht)


def test_carmichael_numbers_by_korselt():
    assert A.carmichael_numbers(5000) == [561, 1105, 1729, 2465, 2821]
    assert A.carmichael_numbers(560) == [] and A.carmichael_numbers(561) == [561]
    assert A.carmichael_numbers(50_000)[-1] == 46657


# --- Freivalds ---------------------------------------------------------------------------------------------------------------------------


def test_product_hand_values(mat):
    a, b, c, _ = mat
    assert A.product(a, b) == c == [[2, 1], [4, 3]]


def test_freivalds_round_hand_values(mat):
    a, b, c, wrong = mat
    assert A.freivalds_round(a, b, wrong, (1, 0)) == (True, 12)             # lügt
    assert A.freivalds_round(a, b, wrong, (0, 1)) == (False, 12)            # entlarvt
    assert A.freivalds_round(a, b, wrong, (0, 0))[0] and not A.freivalds_round(a, b, wrong, (1, 1))[0]
    for r in ((0, 0), (0, 1), (1, 0), (1, 1)):
        assert A.freivalds_round(a, b, c, r)[0]                                # ein richtiges Produkt besteht jeden Test


def test_all_vectors_order_and_size():
    v = A.all_vectors(2)
    assert v.shape == (2, 4) and [tuple(int(x) for x in v[:, j]) for j in range(4)] == [(0, 0), (0, 1), (1, 0), (1, 1)]
    assert A.all_vectors(5).shape == (5, 32) and len({tuple(col) for col in A.all_vectors(5).T}) == 32


def test_liar_vectors_hand_values(mat):
    a, b, c, wrong = mat
    count, mask = A.liar_vectors(a, b, wrong)
    assert count == 2 and [bool(x) for x in mask] == [True, False, True, False]
    assert A.liar_vectors(a, b, c)[0] == 4                                  # richtiges Produkt: alle Vektoren bestehen
    assert A.liar_vectors([[2]], [[3]], [[7]])[0] == 1 and A.liar_vectors([[2]], [[3]], [[6]])[0] == 2     # 1 × 1: r = 0 lügt immer, r = 1 nur wenn richtig


def test_liar_vectors_agree_with_the_round_for_every_vector(mat):
    a, b, _, wrong = mat
    count, mask = A.liar_vectors(a, b, wrong)
    vectors = A.all_vectors(2)
    for j in range(4):
        r = tuple(int(x) for x in vectors[:, j])
        assert A.freivalds_round(a, b, wrong, r)[0] == bool(mask[j])
    assert count == sum(bool(x) for x in mask)


def test_corrupt_kinds_change_exactly_what_they_say():
    rng = SplitMix64(11)
    n = 5
    c = [[10 * i + j for j in range(n)] for i in range(n)]
    diff = lambda d: {(i, j): d[i][j] - c[i][j] for i in range(n) for j in range(n) if d[i][j] != c[i][j]}
    one = diff(A.corrupt(c, "one", rng))
    assert len(one) == 1 and list(one.values()) == [1]
    two = diff(A.corrupt(c, "two_row", rng))
    assert len(two) == 2 and sorted(two.values()) == [-1, 1] and len({i for i, _ in two}) == 1
    rows = diff(A.corrupt(c, "two_rows", rng))
    assert len(rows) == 2 and sorted(rows.values()) == [-2, 3] and len({i for i, _ in rows}) == 2
    row = A.corrupt(c, "row", rng)
    changed_rows = {i for i in range(n) if row[i] != c[i]}
    assert len(changed_rows) == 1 and all(0 <= x < 100 for i in changed_rows for x in row[i])
    rand = A.corrupt(c, "random", rng)
    assert rand != c and all(0 <= x < 1000 for r in rand for x in r)
    assert c == [[10 * i + j for j in range(n)] for i in range(n)]            # das Original bleibt unverändert
    with pytest.raises(ValueError):
        A.corrupt(c, "unbekannt", rng)


def test_corrupt_needs_two_rows_and_columns_for_the_pair_kinds():
    rng = SplitMix64(1)
    with pytest.raises(ValueError):
        A.corrupt([[1]], "two_row", rng)
    with pytest.raises(ValueError):
        A.corrupt([[1]], "two_rows", rng)
    assert A.corrupt([[1]], "one", rng) == [[2]]


# --- Wiederholung, Mehrheitsentscheid ------------------------------------------------------------------------------------------------------


def test_error_after_rounds_and_one_sided_rounds():
    assert A.error_after_rounds(Fraction(1, 2), 3) == Fraction(1, 8) and A.error_after_rounds(Fraction(1, 4), 0) == 1
    assert A.one_sided_rounds(Fraction(1, 100)) == 7 and A.one_sided_rounds(Fraction(1, 10 ** 6)) == 20 and A.one_sided_rounds(Fraction(1, 2)) == 1
    assert A.one_sided_rounds(Fraction(1, 100), Fraction(1, 4)) == 4
    with pytest.raises(ValueError):
        A.one_sided_rounds(Fraction(1, 100), Fraction(1))


def test_majority_error_hand_values():
    third = Fraction(1, 3)
    assert A.majority_error(1, third) == third and A.majority_error(3, third) == Fraction(7, 27) and A.majority_error(5, third) == Fraction(17, 81)
    assert A.majority_error(5, Fraction(0)) == 0 and A.majority_error(5, Fraction(1)) == 1 and A.majority_error(5, Fraction(1, 2)) == Fraction(1, 2)
    with pytest.raises(ValueError):
        A.majority_error(4, third)


def test_rounds_needed_for_the_majority_vote():
    assert A.rounds_needed(Fraction(1, 100), Fraction(1, 3)) == 47 and A.rounds_needed(Fraction(1, 10 ** 6), Fraction(1, 3)) == 193
    assert A.rounds_needed(Fraction(1, 3), Fraction(1, 3)) == 1 and A.rounds_needed(Fraction(1, 4), Fraction(1, 3)) == 5
