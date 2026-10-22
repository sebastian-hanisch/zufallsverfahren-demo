"""Konstanten: Regler-Grenzen, Rechengrenzen, Messreihen-Parameter, Farben und Presets.

Rechengrenze am Regler-Maximum (DEMO-PLAYBOOK §1c): n = 12 Matrizen: alle 2^12 = 4.096 Vektoren, je 3n² = 432 Multiplikationen (rund 1,8 Millionen); Primtest bis N = 4.999: alle Basen einer Zahl in Millisekunden;
die Messreihe über alle ungeraden Zusammengesetzten bis LIAR_LIMIT zählt jede Basis jeder Zahl (rund 5 Sekunden)."""

N_MIN, N_MAX, DEFAULT_N = 2, 12, 10                   # Größe der Matrizen (alle 2^n Vektoren werden aufgezählt)
SEED_MAX, DEFAULT_SEED = 999999, 35
KINDS = {
    "one": "ein Eintrag falsch",
    "two_row": "zwei Einträge einer Zeile (+1, −1)",
    "two_rows": "zwei Zeilen, je ein Eintrag",
    "row": "eine ganze Zeile zufällig",
    "random": "ganz zufällige Matrix",
}
DEFAULT_KIND = "one"
T_MIN, T_MAX, DEFAULT_T = 1, 12, 3                    # Runden bzw. Basen
NUM_MIN, NUM_MAX, DEFAULT_NUM = 3, 4999, 561          # Zahl für den Primtest
RUNS_OPTIONS = (1_000, 10_000, 100_000)               # Läufe der Stichprobe (Illustration, nicht Beleg)
DEFAULT_RUNS = 10_000
MATRIX_HIGH = 10                                      # Einträge von A und B: 0 bis 9
ROW_HIGH, RANDOM_HIGH = 100, 1000                     # Wertebereich der zufälligen Fehler

# Messreihen (alle Instanzen aus dem eigenen Generator: auf jeder Plattform dieselben)
E1_SIZES = (6, 8, 10)
E1_PAIRS = 200                                        # Matrizenpaare je Fehlerart und Größe
E1_SEED = 1000
LIAR_LIMIT = 5000                                     # alle ungeraden Zusammengesetzten 9 bis hierhin
CARMICHAEL_LIMIT = 50_000
BPP_ERROR = (1, 3)                                    # Fehler eines Laufs bei zweiseitigem Fehler (1/3)
RP_ERROR = (1, 2)                                     # Fehler eines Laufs bei einseitigem Fehler (1/2)
BPP_TS = (1, 3, 5, 11, 21, 51, 101)
BPP_TARGETS = ((1, 100), (1, 1_000_000))              # gewünschter Gesamtfehler

COLOR_STRONG = "#2F6B65"
COLOR_FERMAT = "#B8860B"
COLOR_BOUND = "#C0392B"
COLOR_EXACT = "#4c78a8"
COLOR_SAMPLE = "#7a5195"
COLOR_SERIES = ("#2F6B65", "#4c78a8", "#B8860B", "#C0392B", "#7a5195")

PRESETS = {
    "Standardfall (Voreinstellung)": {"n": DEFAULT_N, "seed": DEFAULT_SEED, "kind": "one", "t": DEFAULT_T, "num": DEFAULT_NUM, "runs": DEFAULT_RUNS},
    "Lehrbeispiel (3 × 3)": {"n": 3, "seed": 2, "kind": "one", "t": 2, "num": 15, "runs": DEFAULT_RUNS},
    "Strukturierter Fehler": {"n": DEFAULT_N, "seed": DEFAULT_SEED, "kind": "two_row", "t": DEFAULT_T, "num": DEFAULT_NUM, "runs": DEFAULT_RUNS},
    "Zufälliger Fehler": {"n": DEFAULT_N, "seed": DEFAULT_SEED, "kind": "random", "t": DEFAULT_T, "num": DEFAULT_NUM, "runs": DEFAULT_RUNS},
    "Carmichael-Zahl 1.729": {"n": DEFAULT_N, "seed": DEFAULT_SEED, "kind": "one", "t": DEFAULT_T, "num": 1729, "runs": DEFAULT_RUNS},
    "Zahl mit vielen Lügnern (1.891)": {"n": DEFAULT_N, "seed": DEFAULT_SEED, "kind": "one", "t": DEFAULT_T, "num": 1891, "runs": DEFAULT_RUNS},
}
PRESET_HELP = {   # nach der Messung geschrieben (DEMO-PLAYBOOK: Hilfetexte nie vor der Messung); jede Zahl steht in tests/test_claims.py
    "Standardfall (Voreinstellung)": "10 × 10, ein Eintrag falsch, 3 Runden; die Zahl 561 = 3 · 11 · 17: 10 von 560 Basen bestehen Miller–Rabin, 320 den Fermat-Test.",
    "Lehrbeispiel (3 × 3)": "3 × 3 mit nur 8 Vektoren, 4 davon lügen: jeder Vektor lässt sich von Hand prüfen. Bei dieser Größe ist Nachrechnen billiger (54 gegen 27 Multiplikationen).",
    "Strukturierter Fehler": "Zwei Einträge einer Zeile (+1, −1): genau die Hälfte der Vektoren lügt, die Schranke 1/2 wird erreicht.",
    "Zufälliger Fehler": "Eine ganz zufällige Matrix als C: nur 1 von 1.024 Vektoren lügt, der Fehler fällt fast sicher auf.",
    "Carmichael-Zahl 1.729": "1.729 = 7 · 13 · 19: der Fermat-Test besteht 1.296 von 1.728 Basen, Miller–Rabin nur 162.",
    "Zahl mit vielen Lügnern (1.891)": "1.891 = 31 · 61: 450 von 1.890 Basen bestehen Miller–Rabin (23,8 %), der größte Anteil unter den Zahlen über 9 bis 5.000.",
}
