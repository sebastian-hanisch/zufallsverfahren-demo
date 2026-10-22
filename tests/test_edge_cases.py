"""Randfälle auf App-Ebene: jede Reglerkombination an den Grenzen liefert eine geprüfte Analyse; Eingaben außerhalb des Bereichs werden abgewiesen."""

from fractions import Fraction

import pytest

import zfv_algorithm as A
import zfv_constants as C
import zfv_evaluation as ev
from zfv_rng import SplitMix64


@pytest.mark.parametrize("kind", list(C.KINDS))
@pytest.mark.parametrize("n", [C.N_MIN, 3, C.N_MAX])
@pytest.mark.parametrize("t", [C.T_MIN, C.T_MAX])
def test_extremes_of_the_sliders_are_clean(n, kind, t):
    a = ev.analyse(ev.Settings(n=n, kind=kind, t=t, runs=1000))
    assert ev.validation_errors(a) == []
    assert ev.verdict_matrix(a)[0] in ("success", "info")


@pytest.mark.parametrize("num", [C.NUM_MIN, 4, 5, 8, 9, 10, 25, C.NUM_MAX, 4998])
def test_number_bounds(num):
    a = ev.analyse(ev.Settings(num=num))
    assert ev.validation_errors(a) == []
    assert ev.verdict_number(a)[0] in ("info", "warning")


@pytest.mark.parametrize("seed", [0, C.SEED_MAX])
def test_seed_bounds(seed):
    assert ev.validation_errors(ev.analyse(ev.Settings(seed=seed))) == []


def test_largest_matrix_is_enumerated_completely():
    a = ev.analyse(ev.Settings(n=C.N_MAX, kind="row"))
    assert a.matrix.total == 4096 and a.matrix.mults_naive == 1728 and a.matrix.mults_freivalds == C.DEFAULT_T * 3 * 144


def test_smallest_matrix_two_by_two():
    a = ev.analyse(ev.Settings(n=2, kind="two_rows", seed=1))
    assert a.matrix.total == 4 and a.matrix.liars in (0, 1, 2) and ev.validation_errors(a) == []


def test_cheaper_than_recomputing_flips_with_n_and_t():
    small = ev.analyse(ev.Settings(n=3, t=2))
    assert small.matrix.mults_freivalds > small.matrix.mults_naive and ev.verdict_matrix(small)[0] == "info"
    big = ev.analyse(ev.Settings(n=10, t=3))
    assert big.matrix.mults_freivalds < big.matrix.mults_naive and ev.verdict_matrix(big)[0] == "success"
    assert ev.analyse(ev.Settings(n=C.N_MAX, t=C.T_MAX)).matrix.mults_freivalds == 12 * 3 * 144                                 # 5.184 gegen 1.728: viele Runden machen es teurer


def test_the_validation_catches_a_number_the_tests_cannot_handle():
    with pytest.raises(ValueError):
        A.strong_test(10, 3)
    with pytest.raises(ValueError):
        A.strong_test(1, 1)
    with pytest.raises(ValueError):
        A.strong_test(9, 0)
    with pytest.raises(ValueError):
        A.strong_test(9, 9)
    with pytest.raises(ValueError):
        A.fermat_pass(9, 10)
    with pytest.raises(ValueError):
        A.decompose(8)
    with pytest.raises(ValueError):
        A.decompose(1)


def test_invalid_arguments_are_rejected():
    with pytest.raises(ValueError):
        A.mod_pow(2, -1, 7)
    with pytest.raises(ValueError):
        A.majority_error(4, Fraction(1, 3))
    with pytest.raises(ValueError):
        A.majority_error(-1, Fraction(1, 3))
    with pytest.raises(ValueError):
        A.one_sided_rounds(Fraction(1, 10), Fraction(1))
    with pytest.raises(ValueError):
        A.one_sided_rounds(Fraction(1, 10), Fraction(-1, 2))
    with pytest.raises(ValueError):
        A.corrupt([[1]], "two_row", SplitMix64(1))
    with pytest.raises(ValueError):
        A.corrupt([[1, 2], [3, 4]], "bogus", SplitMix64(1))


def test_mod_pow_zero_exponent_and_small_moduli():
    assert A.mod_pow(5, 0, 7) == (1, 0) and A.mod_pow(5, 0, 1) == (0, 0) and A.mod_pow(5, 1, 7) == (5, 0) and A.mod_pow(0, 3, 7)[0] == 0


def test_corrupt_leaves_the_input_untouched_and_always_changes_it():
    c = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    for kind in C.KINDS:
        for seed in range(40):
            copy = [row[:] for row in c]
            out = A.corrupt(c, kind, SplitMix64(seed))
            assert c == copy and out != c
    # ein Eintrag: genau ein Eintrag um 1 größer; zwei in einer Zeile: Summe unverändert
    one = A.corrupt(c, "one", SplitMix64(1))
    assert sum(map(sum, one)) - sum(map(sum, c)) == 1
    two = A.corrupt(c, "two_row", SplitMix64(1))
    assert sum(map(sum, two)) == sum(map(sum, c)) and sum(x != y for r, s in zip(two, c) for x, y in zip(r, s)) == 2
    rows = A.corrupt(c, "two_rows", SplitMix64(1))
    assert sum(map(sum, rows)) - sum(map(sum, c)) == 1


def test_corrupt_row_kind_changes_exactly_one_row_and_random_stays_in_range():
    c = [[1, 2], [3, 4]]
    for seed in range(60):
        out = A.corrupt(c, "row", SplitMix64(seed))
        changed = [r for r, s in zip(out, c) if r != s]
        assert len(changed) == 1 and all(0 <= x < 100 or x == c[out.index(changed[0])][0] + 1 for x in changed[0])
        rand = A.corrupt(c, "random", SplitMix64(seed))
        assert all(0 <= x < 1000 for r in rand for x in r)


def test_corrupt_collision_fallbacks():
    class Fixed:
        def __init__(self, values):
            self.values, self.i = values, 0

        def below(self, n):
            v = self.values[self.i % len(self.values)] % n
            self.i += 1
            return v

    c = [[5, 5], [5, 5]]
    out = A.corrupt(c, "row", Fixed([0, 0, 5, 5]))                  # Zeile 0 wird zufällig 5, 5: gleich wie vorher -> der erste Eintrag wird verschoben
    assert out == [[6, 5], [5, 5]]
    out = A.corrupt(c, "random", Fixed([5]))                        # alles 5: gleich wie C -> Eintrag (0, 0) verschoben
    assert out == [[6, 5], [5, 5]]


def test_the_base_check_rejects_even_and_tiny_moduli_on_its_own():
    """`_check` allein: `fermat_pass` und `strong_pass` rufen `decompose` nicht vor der Prüfung auf (bei `strong_test` fängt `decompose` gerade n zusätzlich ab)."""
    for n, a in ((10, 3), (4, 1), (2, 1), (1, 1), (0, 1)):
        with pytest.raises(ValueError):
            A.fermat_pass(n, a)
        with pytest.raises(ValueError):
            A.strong_pass(n, a)
    for n, a in ((9, 0), (9, 9), (9, -1)):
        with pytest.raises(ValueError):
            A.fermat_pass(n, a)
    assert A.fermat_pass(9, 1) and A.fermat_pass(9, 8) and A.strong_pass(9, 8) and not A.strong_pass(9, 2)                       # Grenzen 1 und n − 1 gelten


def test_two_rows_error_always_hits_two_distinct_rows_and_every_pair():
    """Die zweite Zeile ist nie die erste und jede andere Zeile kommt vor (Abstand 1 bis n − 1)."""
    for n in (2, 3, 4, 5):
        c = [[10 * i + j for j in range(n)] for i in range(n)]
        distances = set()
        for seed in range(300):
            out = A.corrupt(c, "two_rows", SplitMix64(seed))
            plus = [(i, j) for i in range(n) for j in range(n) if out[i][j] == c[i][j] + 3]
            minus = [(i, j) for i in range(n) for j in range(n) if out[i][j] == c[i][j] - 2]
            assert len(plus) == 1 and len(minus) == 1 and plus[0][0] != minus[0][0], (n, seed)
            distances.add((minus[0][0] - plus[0][0]) % n)
        assert distances == set(range(1, n)), n


def test_two_row_error_always_hits_two_distinct_columns_and_every_distance():
    for n in (2, 3, 4, 5):
        c = [[0] * n for _ in range(n)]
        distances = set()
        for seed in range(300):
            out = A.corrupt(c, "two_row", SplitMix64(seed))
            row = next(r for r in out if any(r))
            plus, minus = row.index(1), row.index(-1)
            assert plus != minus and sum(map(sum, out)) == 0
            distances.add((minus - plus) % n)
        assert distances == set(range(1, n)), n


def test_factorize_small_cases():
    assert A.factorize(2) == [2] and A.factorize(3) == [3] and A.factorize(1) == [] and A.factorize(4) == [2, 2] and A.factorize(12) == [2, 2, 3] and A.factorize(49) == [7, 7]


def test_one_sided_rounds_accepts_a_round_that_never_errs():
    assert A.one_sided_rounds(Fraction(1, 10), Fraction(0)) == 1
    assert A.one_sided_rounds(Fraction(1, 2), Fraction(1, 2)) == 1 and A.one_sided_rounds(Fraction(1, 2), Fraction(999, 1000)) == 693 and Fraction(999, 1000) ** 693 <= Fraction(1, 2) < Fraction(999, 1000) ** 692


def test_fmt_fraction_of_negative_values_stays_decimal():
    assert ev.fmt_fraction(Fraction(-1, 3)) == "-1/3 (-0,3333)"
