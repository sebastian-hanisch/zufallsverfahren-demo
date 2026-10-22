"""Kern: Miller–Rabin und Fermat-Test mit allen Basen, Carmichael-Zahlen nach Korselt, Freivalds mit allen 2^n Vektoren, Fehlerarten und exakte Verstärkungsrechnung (Brüche).

Jede Einheit ist eine Funktion (DEMO-PLAYBOOK §1b). Gezählt werden **Multiplikationen** (Freivalds: 3n² je Runde; Miller–Rabin: modulare Multiplikationen einer Basis), nie Sekunden.
Die „Lügner“ sind **aufgezählt**, nicht gestichprobt: bei Zahlen alle Basen 1 bis n − 1, bei Matrizen alle 2^n Vektoren aus {0, 1}^n. Vektoren werden in der Reihenfolge von `itertools.product` aufgezählt (erste Komponente zuerst)."""

import itertools
import math
from fractions import Fraction

import numpy as np


# --- Potenz, Zerlegung, Primzahlen ---------------------------------------------------------------------------------------------------------


def mod_pow(a: int, e: int, n: int) -> tuple:
    """a^e mod n durch Quadrieren und Multiplizieren von links (das höchste Bit kostet nichts); Rückgabe (Wert, Zahl der Multiplikationen)."""
    if e < 0:
        raise ValueError("Exponent muss >= 0 sein")
    result = a % n
    if e == 0:
        return 1 % n, 0
    mults = 0
    for bit in bin(e)[3:]:
        result = result * result % n
        mults += 1
        if bit == "1":
            result = result * a % n
            mults += 1
    return result, mults


def decompose(n: int) -> tuple:
    """n − 1 = d · 2^s mit ungeradem d (n ungerade, n >= 3)."""
    if n < 3 or n % 2 == 0:
        raise ValueError("n muss ungerade und >= 3 sein")
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    return d, s


def is_prime_trial(n: int) -> bool:
    """Probedivision (unabhängiger Prüfer, nicht Teil der Tests)."""
    if n < 2:
        return False
    i = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += 1
    return True


def factorize(n: int) -> list:
    """Primfaktoren aufsteigend mit Vielfachheit (Probedivision)."""
    factors, p = [], 2
    while p * p <= n:
        while n % p == 0:
            factors.append(p)
            n //= p
        p += 1
    if n > 1:
        factors.append(n)
    return factors


def is_carmichael(n: int) -> bool:
    """Korselt: n zusammengesetzt, quadratfrei, und p − 1 teilt n − 1 für jeden Primfaktor p. Unabhängig von jedem Test der Demo."""
    if n < 3 or is_prime_trial(n):
        return False
    factors = factorize(n)
    return len(set(factors)) == len(factors) and all((n - 1) % (p - 1) == 0 for p in factors)


def carmichael_numbers(limit: int) -> list:
    return [n for n in range(3, limit + 1, 2) if is_carmichael(n)]


# --- Miller–Rabin und Fermat -------------------------------------------------------------------------------------------------------------


def _check(n: int, a: int) -> None:
    if n < 3 or n % 2 == 0 or not 1 <= a <= n - 1:
        raise ValueError("n muss ungerade und >= 3 sein, die Basis zwischen 1 und n − 1 liegen")


def strong_test(n: int, a: int) -> tuple:
    """Ein Durchgang des Miller–Rabin-Tests zur Basis a: n − 1 = d · 2^s; n besteht, wenn a^d ≡ 1 oder a^(d · 2^r) ≡ −1 für ein r < s. Rückgabe (besteht, Multiplikationen)."""
    _check(n, a)
    d, s = decompose(n)
    x, mults = mod_pow(a, d, n)
    if x == 1 or x == n - 1:
        return True, mults
    for _ in range(s - 1):
        x = x * x % n
        mults += 1
        if x == n - 1:
            return True, mults
    return False, mults


def strong_pass(n: int, a: int) -> bool:
    """Wie `strong_test`, aber mit der eingebauten Potenz (schnell für die Messreihe über alle Basen)."""
    _check(n, a)
    d, s = decompose(n)
    x = pow(a, d, n)
    if x == 1 or x == n - 1:
        return True
    for _ in range(s - 1):
        x = x * x % n
        if x == n - 1:
            return True
    return False


def fermat_pass(n: int, a: int) -> bool:
    _check(n, a)
    return pow(a, n - 1, n) == 1


def strong_liars(n: int) -> list:
    """Alle Basen 1 bis n − 1, zu denen n den Miller–Rabin-Test besteht (bei Primzahlen alle; bei Zusammengesetzten die „Lügner“)."""
    return [a for a in range(1, n) if strong_pass(n, a)]


def fermat_liars(n: int) -> list:
    return [a for a in range(1, n) if fermat_pass(n, a)]


def liar_shares(n: int) -> tuple:
    """(Anteil starker Lügner, Anteil Fermat-Lügner) unter den Basen 1 bis n − 1, als Brüche (die trivialen Lügner 1 und n − 1 sind eingerechnet)."""
    return Fraction(len(strong_liars(n)), n - 1), Fraction(len(fermat_liars(n)), n - 1)


# --- Freivalds ---------------------------------------------------------------------------------------------------------------------------


def product(a, b) -> list:
    n = len(a)
    return [[sum(a[i][k] * b[k][j] for k in range(n)) for j in range(n)] for i in range(n)]


def _matvec(m, v):
    return [sum(row[k] * v[k] for k in range(len(v))) for row in m]


def freivalds_round(a, b, c, r) -> tuple:
    """Ein Durchgang: besteht A(Br) = Cr? Rückgabe (besteht, Multiplikationen = 3n²). Ein richtiges Produkt besteht jeden Durchgang."""
    n = len(a)
    left = _matvec(a, _matvec(b, r))
    right = _matvec(c, r)
    return left == right, 3 * n * n


def all_vectors(n: int):
    """Alle 2^n Vektoren aus {0, 1}^n als Spalten einer n × 2^n Matrix (Reihenfolge von `itertools.product`)."""
    return np.array(list(itertools.product((0, 1), repeat=n)), dtype=np.int64).T


def liar_vectors(a, b, c) -> tuple:
    """Wie viele der 2^n Vektoren bestehen den Test A(Br) = Cr? Rückgabe (Anzahl, Maske über alle Vektoren). Bei richtigem Produkt bestehen alle; bei falschem höchstens die Hälfte."""
    n = len(a)
    vectors = all_vectors(n)
    left = np.array(a, dtype=np.int64) @ (np.array(b, dtype=np.int64) @ vectors)
    right = np.array(c, dtype=np.int64) @ vectors
    mask = np.all(left == right, axis=0)
    return int(mask.sum()), mask


def corrupt(c, kind: str, rng) -> list:
    """Eine falsche Fassung von C (das Original bleibt unverändert): „one“: ein Eintrag +1; „two_row“: zwei Einträge einer Zeile (+1, −1); „two_rows“: je ein Eintrag in zwei Zeilen (+3, −2);
    „row“: eine ganze Zeile zufällig (0 bis 99, anders als die alte); „random“: ganz zufällig (0 bis 999, anders als C)."""
    n = len(c)
    out = [list(row) for row in c]
    if kind not in ("one", "two_row", "two_rows", "row", "random"):
        raise ValueError(f"unbekannte Fehlerart: {kind}")
    if kind in ("two_row", "two_rows") and n < 2:
        raise ValueError("diese Fehlerart braucht mindestens zwei Zeilen und Spalten")
    i, j = rng.below(n), rng.below(n)
    if kind == "one":
        out[i][j] += 1
    elif kind == "two_row":
        j2 = (j + 1 + rng.below(n - 1)) % n
        out[i][j] += 1
        out[i][j2] -= 1
    elif kind == "two_rows":
        i2 = (i + 1 + rng.below(n - 1)) % n
        j2 = rng.below(n)
        out[i][j] += 3
        out[i2][j2] -= 2
    elif kind == "row":
        out[i] = [rng.below(100) for _ in range(n)]
        if out[i] == list(c[i]):
            out[i][0] += 1
    else:
        out = [[rng.below(1000) for _ in range(n)] for _ in range(n)]
        if out == [list(r) for r in c]:
            out[0][0] += 1
    return out


# --- Wiederholung und Mehrheitsentscheid (exakt, Brüche) --------------------------------------------------------------------------------------


def error_after_rounds(share: Fraction, t: int) -> Fraction:
    """Unabhängige Runden: die Antwort bleibt falsch, wenn jede Runde lügt: share^t."""
    return share ** t


def one_sided_rounds(target: Fraction, q: Fraction = Fraction(1, 2)) -> int:
    """Kleinste Rundenzahl t >= 1 mit q^t <= target (einseitiger Fehler q je Runde)."""
    if not 0 <= q < 1:
        raise ValueError("q muss in [0, 1) liegen")
    t = 1
    while q ** t > target:
        t += 1
    return t


def majority_error(t: int, p: Fraction) -> Fraction:
    """Fehler des Mehrheitsentscheids aus t (ungerade) unabhängigen Läufen, jeder mit Fehler p: mehr als t / 2 Läufe falsch (Binomialsumme in Brüchen)."""
    if t % 2 == 0 or t < 1:
        raise ValueError("t muss ungerade sein")
    return sum(math.comb(t, j) * p ** j * (1 - p) ** (t - j) for j in range(t // 2 + 1, t + 1))


def rounds_needed(target: Fraction, p: Fraction) -> int:
    """Kleinste ungerade Zahl t, für die der Mehrheitsentscheid höchstens `target` Fehler hat."""
    t = 1
    while majority_error(t, p) > target:
        t += 2
    return t
