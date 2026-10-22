"""Die beiden Messreihen-Knöpfe (▶️) lässt der allgemeine Rauchtest aus (er überspringt Auto-Play-Marken): hier wird jeder Knopf einzeln gedrückt und die Seite ohne Ausnahme gerendert."""

import os
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parent.parent / "app.py")
TIMEOUT = int(os.environ.get("APPTEST_TIMEOUT", "600"))


@pytest.mark.parametrize("label", ["Messreihe Freivalds", "Messreihe Miller–Rabin"])
def test_each_sweep_button_renders(label):
    at = AppTest.from_file(APP, default_timeout=TIMEOUT)
    at.run()
    assert not at.exception
    before = len(at.get("plotly_chart"))
    next(b for b in at.button if label in b.label).click().run(timeout=TIMEOUT)
    assert not at.exception, [str(e) for e in at.exception]
    assert len(at.get("plotly_chart")) == before + 1
    assert not at.error, [e.value for e in at.error]                                                                  # kein Verdikt der Art „error“


def test_both_sweeps_together_and_a_preset_afterwards():
    at = AppTest.from_file(APP, default_timeout=TIMEOUT)
    at.run()
    for label in ("Messreihe Freivalds", "Messreihe Miller–Rabin"):
        next(b for b in at.button if label in b.label).click().run(timeout=TIMEOUT)
    assert len(at.get("plotly_chart")) == 3 + 2 + 1 + 1                                                               # 3 Live-Diagramme (Vektoren, Verstärkung, Basen) + 2 Messreihen + Carmichael + BPP
    next(b for b in at.button if "Lehrbeispiel" in b.label).click().run(timeout=TIMEOUT)
    assert not at.exception, [str(e) for e in at.exception]
