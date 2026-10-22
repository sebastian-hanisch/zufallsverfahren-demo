"""Gemeinsame Fixtures: Mini-Instanzen, an denen jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b).

Vektoren werden in der Reihenfolge von `itertools.product((0, 1), repeat=n)` aufgezählt (erste Komponente zuerst): für n = 2: (0, 0), (0, 1), (1, 0), (1, 1)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture
def mat():
    """A = ((1, 2), (3, 4)), B = ((0, 1), (1, 0)): A · B = ((2, 1), (4, 3)) (Spalten von A vertauscht).

    Falsches C = ((2, 1), (4, 4)): Eintrag (1, 1) um 1 zu groß, D = C − AB = ((0, 0), (0, 1)), D r = (0, r_1): null genau für r_1 = 0: die Vektoren (0, 0) und (1, 0) lügen, (0, 1) und (1, 1) entlarven.
    Durchgang mit r = (1, 0): B r = (0, 1), A (B r) = (1 · 0 + 2 · 1, 3 · 0 + 4 · 1) = (2, 4); C r = (2, 4): gleich, der Test besteht (Lügner). 12 Multiplikationen (3 · 2²).
    Durchgang mit r = (0, 1): B r = (1, 0), A (B r) = (1, 3); C r = (1, 4): verschieden, der Fehler ist entdeckt."""
    a = [[1, 2], [3, 4]]
    b = [[0, 1], [1, 0]]
    return a, b, [[2, 1], [4, 3]], [[2, 1], [4, 4]]
