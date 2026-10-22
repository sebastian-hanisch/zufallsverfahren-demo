"""Szenario: zufällige Matrizenpaare und ihre falschen Produkte, mit eigenem Zufallsgenerator (SplitMix64, wörtliche Kopie in zfv_rng.py), damit alle Instanzen auf jeder Plattform gleich sind.

A und B haben Einträge 0 bis 9 (Reihenfolge: erst alle Einträge von A zeilenweise, dann B); danach zieht `corrupt` die Fehlerstellen aus demselben Strom."""

from dataclasses import dataclass

import zfv_algorithm as A
import zfv_constants as C
from zfv_rng import SplitMix64


@dataclass(frozen=True)
class Instance:
    a: tuple
    b: tuple
    c_true: tuple                    # A · B
    c_wrong: tuple                   # das falsche Produkt, das geprüft wird


def random_matrix(n: int, rng: SplitMix64, high: int = C.MATRIX_HIGH) -> list:
    return [[rng.below(high) for _ in range(n)] for _ in range(n)]


def make_instance(n: int, kind: str, seed: int) -> Instance:
    """Deterministisch aus (n, Fehlerart, Zufalls-Seed)."""
    rng = SplitMix64(seed)
    a, b = random_matrix(n, rng), random_matrix(n, rng)
    c = A.product(a, b)
    wrong = A.corrupt(c, kind, rng)
    return Instance(tuple(map(tuple, a)), tuple(map(tuple, b)), tuple(map(tuple, c)), tuple(map(tuple, wrong)))
