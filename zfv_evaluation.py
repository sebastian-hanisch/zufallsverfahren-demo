"""Kennzahlen, Messreihen und Verdikte (alle Verdikte sind reine Funktionen (Art, Text), DEMO-PLAYBOOK §12).

Anteile sind **Brüche** (`Fraction`): die Schranken 1/2 und 1/4 werden exakt verglichen, nie mit Gleitkomma."""

import math
from dataclasses import dataclass
from fractions import Fraction
from statistics import median

import numpy as np

import zfv_algorithm as A
import zfv_constants as C
from zfv_rng import SplitMix64
from zfv_scenario import make_instance, random_matrix

HALF, QUARTER = Fraction(1, 2), Fraction(1, 4)


@dataclass(frozen=True, kw_only=True)
class Settings:
    n: int = C.DEFAULT_N
    seed: int = C.DEFAULT_SEED
    kind: str = C.DEFAULT_KIND
    t: int = C.DEFAULT_T
    num: int = C.DEFAULT_NUM
    runs: int = C.DEFAULT_RUNS


@dataclass(frozen=True)
class MatrixPart:
    a: tuple
    b: tuple
    c_true: tuple
    c_wrong: tuple
    liars: int                       # Vektoren aus {0, 1}^n, die den falschen Test bestehen (alle aufgezählt)
    total: int                       # 2^n
    share: Fraction
    after_t: Fraction                # share^t: der Fehler bleibt nach t Runden unentdeckt
    sample_fails: int                # Läufe der Stichprobe, in denen alle t Runden lügen
    mults_naive: int                 # n^3
    mults_freivalds: int             # t · 3n²


@dataclass(frozen=True)
class NumberPart:
    num: int
    kind: str                        # "prim", "zusammengesetzt" oder "gerade"
    factors: tuple
    strong: tuple                    # Basen 1 bis n − 1, die den Miller–Rabin-Test bestehen
    fermat: tuple
    strong_share: Fraction | None
    fermat_share: Fraction | None
    after_t: Fraction | None         # strong_share^t
    carmichael: bool
    mults_base_two: int              # Multiplikationen eines Durchgangs mit Basis 2 (None bei gerader Zahl)


@dataclass(frozen=True)
class Analysis:
    settings: Settings
    matrix: MatrixPart
    number: NumberPart


# --- Zahlen im deutschen Format ------------------------------------------------------------------------------------------------------------


def fmt_int(n: int) -> str:
    """Ganze Zahl mit Punkt als Tausendertrenner (1.720.350)."""
    return f"{n:,}".replace(",", ".")


def fmt_num(x: float, digits: int = 1) -> str:
    """Dezimalzahl mit Komma (22,7)."""
    return f"{x:.{digits}f}".replace(".", ",")


def fmt_median(x) -> str:
    """Median als ganze Zahl, wenn er eine ist, sonst mit einer Nachkommastelle und Komma (nie stillschweigend gerundet)."""
    return fmt_int(int(x)) if x == int(x) else fmt_num(float(x), 1)


def fmt_fraction(f: Fraction, digits: int = 4) -> str:
    """Bruch mit Dezimalwert: „1/2 (0,5)“, „1/256 (0,0039)“, sehr kleine Werte (unter 0,0001) in Zehnerpotenz („1/175616 (5,7 · 10^(−6))“); ganze Zahlen ohne Bruch."""
    if f.denominator == 1:
        return str(f.numerator)
    x = float(f)
    if 0 < x < 10 ** (-digits):
        mantissa, exponent = f"{x:.1e}".split("e")
        dec = f"{mantissa.replace('.', ',')} · 10^(−{abs(int(exponent))})"
    else:
        dec = f"{x:.{digits}f}".rstrip("0").rstrip(".").replace(".", ",")
    return f"{f.numerator}/{f.denominator} ({dec})"


def fmt_percent(f: Fraction, digits: int = 1) -> str:
    """Anteil als Prozentzahl mit Komma, ohne überflüssige Nachkommastelle (57,1 %, 25 %)."""
    x = round(float(f) * 100, digits)
    return (fmt_int(int(x)) if x == int(x) else fmt_num(x, digits)) + " %"


# --- Stichprobe ----------------------------------------------------------------------------------------------------------------------------


def sample_failures(mask, n: int, t: int, runs: int, seed: int) -> int:
    """Illustration (kein Beleg): `runs` Läufe mit je t zufälligen Vektoren; ein Lauf scheitert, wenn jeder gezogene Vektor ein Lügner ist. Ein Durchgang von Freivalds hängt nur vom Vektor ab (die Maske
    ist die vollständige Aufzählung), deshalb genügt es, den Index zu ziehen; die Gleichwertigkeit prüfen die Tests für jeden Vektor."""
    rng = SplitMix64(seed ^ 0x5DEECE66D)
    size = 1 << n
    fails = 0
    for _ in range(runs):
        if all(mask[rng.below(size)] for _ in range(t)):
            fails += 1
    return fails


# --- Einzelanalyse -------------------------------------------------------------------------------------------------------------------------


def analyse_matrix(n: int, kind: str, seed: int, t: int, runs: int) -> MatrixPart:
    inst = make_instance(n, kind, seed)
    liars, mask = A.liar_vectors(inst.a, inst.b, inst.c_wrong)
    share = Fraction(liars, 1 << n)
    return MatrixPart(inst.a, inst.b, inst.c_true, inst.c_wrong, liars, 1 << n, share, A.error_after_rounds(share, t), sample_failures(mask, n, t, runs, seed), n ** 3, t * 3 * n * n)


def analyse_number(num: int, t: int) -> NumberPart:
    if num % 2 == 0:
        return NumberPart(num, "gerade", tuple(A.factorize(num)), (), (), None, None, None, False, None)
    strong, fermat = tuple(A.strong_liars(num)), tuple(A.fermat_liars(num))
    prime = A.is_prime_trial(num)
    share = Fraction(len(strong), num - 1)
    return NumberPart(num, "prim" if prime else "zusammengesetzt", tuple(A.factorize(num)), strong, fermat, share, Fraction(len(fermat), num - 1),
                      None if prime else A.error_after_rounds(share, t), A.is_carmichael(num), A.strong_test(num, 2)[1])


def analyse(settings: Settings) -> Analysis:
    return Analysis(settings, analyse_matrix(settings.n, settings.kind, settings.seed, settings.t, settings.runs), analyse_number(settings.num, settings.t))


def validation_errors(a: Analysis) -> list:
    """Ergebnis vor der Anzeige prüfen (DEMO-PLAYBOOK §1d): das falsche Produkt ist falsch, der Lügneranteil stimmt mit einer zweiten Rechnung überein und ist höchstens 1/2, ein richtiges Produkt besteht
    jeden Vektor, die Stichprobe passt zum exakten Anteil; bei Zahlen: Klasse stimmt mit Probedivision überein, Lügner passen zu den Sätzen (Primzahlen alle Basen, Zusammengesetzte höchstens 1/4)."""
    errors = []
    m, n = a.matrix, a.settings.n
    ab = A.product(m.a, m.b)
    if tuple(map(tuple, ab)) != m.c_true or m.c_wrong == m.c_true:
        errors.append("Das falsche Produkt ist nicht falsch oder das richtige nicht A · B.")
    vectors = A.all_vectors(n)
    d = np.array(ab, dtype=np.int64) - np.array(m.c_wrong, dtype=np.int64)
    second = int(np.all(d @ vectors == 0, axis=0).sum())
    if second != m.liars or m.total != 1 << n:
        errors.append("Die Zahl der lügenden Vektoren widerspricht der zweiten Rechnung (A · B ausmultipliziert).")
    if m.share > HALF:
        errors.append("Der Anteil lügender Vektoren ist größer als 1/2.")
    if A.liar_vectors(m.a, m.b, m.c_true)[0] != m.total:
        errors.append("Ein richtiges Produkt besteht nicht jeden Vektor.")
    if not 0 <= m.sample_fails <= a.settings.runs:
        errors.append("Die Stichprobe meldet mehr Fehlschläge als Läufe.")
    else:
        p = float(m.after_t)
        sigma = math.sqrt(max(p * (1 - p), 1e-12) / a.settings.runs)
        if a.settings.runs >= 1000 and abs(m.sample_fails / a.settings.runs - p) > 6 * sigma + 1e-9:
            errors.append("Die Stichprobe weicht um mehr als sechs Standardabweichungen vom exakten Anteil ab.")
    z = a.number
    expected = "gerade" if z.num % 2 == 0 else ("prim" if A.is_prime_trial(z.num) else "zusammengesetzt")
    if z.kind != expected:
        errors.append("Die Klasse der Zahl widerspricht der Probedivision.")
        return errors                                                                       # die klassenabhängigen Prüfungen setzen die richtige Klasse voraus
    if z.kind == "prim" and (len(z.strong) != z.num - 1 or len(z.fermat) != z.num - 1):
        errors.append("Eine Primzahl muss jede Basis bestehen.")
    if z.kind == "zusammengesetzt":
        if z.strong_share > QUARTER:                                                        # über alle Basen 1 bis n − 1 gezählt gilt 1/4 auch für n = 9 (dort genau)
            errors.append("Der Anteil starker Lügner ist größer als 1/4.")
        if not set(z.strong) <= set(z.fermat):
            errors.append("Ein starker Lügner ist kein Fermat-Lügner.")
        if z.carmichael != A.is_carmichael(z.num):
            errors.append("Die Carmichael-Eigenschaft widerspricht dem Korselt-Kriterium.")
        if z.carmichael and set(z.fermat) != {x for x in range(1, z.num) if math.gcd(x, z.num) == 1}:
            errors.append("Bei einer Carmichael-Zahl müssen die Fermat-Lügner genau die teilerfremden Basen sein.")
    return errors


# --- Messreihen ----------------------------------------------------------------------------------------------------------------------------


def sweep_freivalds(sizes=C.E1_SIZES, pairs: int = C.E1_PAIRS, seed: int = C.E1_SEED, kinds=tuple(C.KINDS)) -> list:
    """Anteil lügender Vektoren (alle 2^n aufgezählt) je Größe und Fehlerart über feste Matrizenpaare: kleinster, mittlerer (exakter Bruch) und größter Anteil, Zahl der Fälle mit genau 1/2 und über 1/2."""
    rows = []
    for n in sizes:
        rng = SplitMix64(seed + n)
        shares = {k: [] for k in kinds}
        for _ in range(pairs):
            a, b = random_matrix(n, rng), random_matrix(n, rng)
            c = A.product(a, b)
            for k in kinds:
                shares[k].append(Fraction(A.liar_vectors(a, b, A.corrupt(c, k, rng))[0], 1 << n))
        for k in kinds:
            v = shares[k]
            rows.append({"n": n, "kind": k, "pairs": pairs, "min": min(v), "mean": sum(v) / len(v), "max": max(v), "at_half": sum(x == HALF for x in v), "above_half": sum(x > HALF for x in v)})
    return rows


def sweep_liars(limit: int = C.LIAR_LIMIT) -> dict:
    """Alle ungeraden Zusammengesetzten 9 bis `limit`, alle Basen 1 bis n − 1: Zahl der starken und der Fermat-Lügner je Zahl; Zusammenfassung siehe `summarise_liars`."""
    rows = []
    for n in range(9, limit + 1, 2):
        if A.is_prime_trial(n):
            continue
        rows.append({"n": n, "strong": len(A.strong_liars(n)), "fermat": len(A.fermat_liars(n))})
    return summarise_liars(rows, limit)


def summarise_liars(rows: list, limit: int) -> dict:
    """Anteile je Zahl (Brüche) und Zusammenfassung: die acht schlimmsten, Median, Mittel, Zahlen mit starkem Anteil über 1/4 (Schranke; bei allen Basen 1 bis n − 1 gilt sie auch für n = 9, dort genau 1/4)
    und Zahlen mit Fermat-Anteil über 1/2."""
    for r in rows:
        r["strong_share"] = Fraction(r["strong"], r["n"] - 1)
        r["fermat_share"] = Fraction(r["fermat"], r["n"] - 1)
    worst = sorted(rows, key=lambda r: (-r["strong_share"], r["n"]))
    shares = [r["strong_share"] for r in rows]                                                 # `median` sortiert selbst
    return {"limit": limit, "count": len(rows), "rows": rows, "worst": worst[:8], "median": median(shares), "mean": sum(shares) / len(shares),
            "violations": [r["n"] for r in rows if r["strong_share"] > QUARTER],
            "fermat_over_half": [r["n"] for r in rows if r["fermat_share"] > HALF]}


def carmichael_table(limit: int = C.CARMICHAEL_LIMIT) -> list:
    """Carmichael-Zahlen (nach Korselt) bis `limit`: Anteil der Fermat-Lügner und der starken Lügner, Eulersche φ-Funktion."""
    rows = []
    for n in A.carmichael_numbers(limit):
        fermat, strong = A.fermat_liars(n), A.strong_liars(n)
        coprime = sum(1 for x in range(1, n) if math.gcd(x, n) == 1)
        rows.append({"n": n, "factors": tuple(A.factorize(n)), "fermat": len(fermat), "strong": len(strong), "phi": coprime, "fermat_share": Fraction(len(fermat), n - 1),
                     "strong_share": Fraction(len(strong), n - 1), "fermat_is_coprime": len(fermat) == coprime})
    return rows


def bpp_table(ts=C.BPP_TS, bpp=Fraction(*C.BPP_ERROR), rp=Fraction(*C.RP_ERROR), targets=C.BPP_TARGETS) -> dict:
    """Exakt: Fehler des Mehrheitsentscheids (zweiseitig, je Lauf `bpp`) und des einseitigen Verfahrens (`rp`^t); Läufe für die Zielfehler."""
    rows = [{"t": t, "majority": A.majority_error(t, bpp), "one_sided": rp ** t} for t in ts]
    needed = [{"target": Fraction(*tg), "majority": A.rounds_needed(Fraction(*tg), bpp), "one_sided": A.one_sided_rounds(Fraction(*tg), rp)} for tg in targets]
    return {"rows": rows, "needed": needed}


# --- Verdikte (reine Funktionen: (Art, Text)) ------------------------------------------------------------------------------------------------------


def verdict_matrix(a: Analysis) -> tuple:
    m, n, t, runs = a.matrix, a.settings.n, a.settings.t, a.settings.runs
    head = (f"Von {fmt_int(m.total)} Vektoren aus {{0, 1}}^{n} {'besteht' if m.liars == 1 else 'bestehen'} {fmt_int(m.liars)} den Test trotz des Fehlers (Anteil {fmt_fraction(m.share)}); der Fehler wird mit Wahrscheinlichkeit "
            f"{fmt_fraction(1 - m.share)} entdeckt. Nach {t} Runden bleibt er mit Wahrscheinlichkeit {fmt_fraction(m.after_t)} unentdeckt; Stichprobe ({fmt_int(runs)} Läufe, Illustration): "
            f"{fmt_int(m.sample_fails)} Läufe ({fmt_num(100 * m.sample_fails / runs, 2)} %) unentdeckt. Aufwand: {fmt_int(m.mults_freivalds)} Multiplikationen gegen {fmt_int(m.mults_naive)} beim Nachrechnen.")
    if m.share > HALF:
        return "error", head + " Der Anteil überschreitet die Schranke 1/2: das darf nicht sein."
    return ("success" if m.mults_freivalds < m.mults_naive else "info"), head + (" Freivalds ist hier billiger." if m.mults_freivalds < m.mults_naive else " Bei dieser Größe ist Nachrechnen nicht teurer.")


def verdict_number(a: Analysis) -> tuple:
    z, t = a.number, a.settings.t
    if z.kind == "gerade":
        return "info", f"{fmt_int(z.num)} ist gerade" + (" und prim." if z.num == 2 else f": zusammengesetzt (Teiler 2); der Test ist für ungerade Zahlen ab 3 gedacht.")
    if z.kind == "prim":
        return "info", (f"{fmt_int(z.num)} ist prim: sie besteht den Miller–Rabin-Test zu **jeder** der {fmt_int(z.num - 1)} Basen (ein Fehler „zusammengesetzt“ ist unmöglich, einseitiger Fehler); "
                        f"ein Durchgang mit Basis 2 kostet {z.mults_base_two} Multiplikationen modulo n.")
    factors = " · ".join(str(p) for p in z.factors)
    carm = " Eine Carmichael-Zahl (Korselt): der Fermat-Test besteht zu jeder teilerfremden Basis." if z.carmichael else ""
    return "warning", (
        f"{fmt_int(z.num)} = {factors} ist zusammengesetzt. Den Miller–Rabin-Test bestehen {fmt_int(len(z.strong))} von {fmt_int(z.num - 1)} Basen (Anteil {fmt_percent(z.strong_share)}, Schranke 25 %), "
        f"den Fermat-Test {fmt_int(len(z.fermat))} (Anteil {fmt_percent(z.fermat_share)}). Nach {t} zufälligen Basen hält Miller–Rabin die Zahl höchstens mit Wahrscheinlichkeit {fmt_fraction(z.after_t)} für prim.{carm}"
    )


def verdict_freivalds_sweep(rows: list) -> tuple:
    bad = sum(r["above_half"] for r in rows)
    total = sum(r["pairs"] for r in rows)
    if bad:
        return "error", f"Der Anteil lügender Vektoren überschritt 1/2 in {bad} von {fmt_int(total)} Fällen: das darf nicht sein."
    half = [r for r in rows if r["at_half"] == r["pairs"]]
    sizes = sorted({r["n"] for r in rows})
    rand = next(r for r in rows if r["kind"] == "random" and r["n"] == sizes[-1])
    kinds = ", ".join(C.KINDS[r["kind"]] for r in half if r["n"] == sizes[0])
    return "success", (
        f"In allen {fmt_int(total)} Fällen war der Anteil höchstens 1/2 (alle 2^n Vektoren aufgezählt). Genau 1/2 war er bei jedem Paar für: {kinds}. "
        f"Bei einer ganz zufälligen Matrix lag er bei n = {sizes[-1]} bei {fmt_fraction(rand['max'])}: strukturierte Fehler sind die schwersten."
    )


def verdict_liars(res: dict) -> tuple:
    worst = res["worst"]
    top = ", ".join(f"{fmt_int(r['n'])} ({fmt_percent(r['strong_share'])})" for r in worst[:4])
    if res["violations"]:
        return "error", f"Die Schranke 1/4 wurde bei {len(res['violations'])} Zahlen überschritten: das darf nicht sein."
    return "info", (
        f"Alle {fmt_int(res['count'])} ungeraden Zusammengesetzten von 9 bis {fmt_int(res['limit'])}, alle Basen gezählt: der Anteil starker Lügner ist höchstens {fmt_percent(worst[0]['strong_share'])} "
        f"(n = {worst[0]['n']}; für n > 9 ist es höchstens {fmt_percent(max(r['strong_share'] for r in res['rows'] if r['n'] > 9))}); die Schranke 1/4 hält an jeder Zahl. "
        f"Die schlimmsten: {top}. Typisch sind es fast keine: Median {fmt_percent(res['median'], 2)}, Mittel {fmt_percent(res['mean'], 2)}. Beim Fermat-Test liegt der Anteil bei {len(res['fermat_over_half'])} Zahlen über 1/2."
    )


def verdict_carmichael(rows: list) -> tuple:
    lo = min(rows, key=lambda r: r["fermat_share"])
    hi = max(rows, key=lambda r: r["fermat_share"])
    s_hi = max(rows, key=lambda r: r["strong_share"])
    coprime = all(r["fermat_is_coprime"] for r in rows)
    return "warning", (
        f"Bei den {len(rows)} Carmichael-Zahlen bis {fmt_int(max(r['n'] for r in rows))} besteht den Fermat-Test ein Anteil von {fmt_percent(lo['fermat_share'])} (n = {lo['n']}) bis {fmt_percent(hi['fermat_share'])} "
        f"(n = {hi['n']}) der Basen: zusammengesetzt und trotzdem „prim“, ohne brauchbare Schranke. Miller–Rabin bleibt bei höchstens {fmt_percent(s_hi['strong_share'])} (n = {s_hi['n']}). "
        + ("Die Fermat-Lügner sind jeweils genau die zu n teilerfremden Basen." if coprime else "Nicht überall sind die Fermat-Lügner genau die teilerfremden Basen.")
    )


def verdict_bpp(res: dict) -> tuple:
    need = {n["target"]: n for n in res["needed"]}
    small, tiny = need[Fraction(1, 100)], need[Fraction(1, 1_000_000)]
    return "info", (
        f"Zweiseitiger Fehler je Lauf 1/3 (BPP): der Mehrheitsentscheid braucht {small['majority']} Läufe für höchstens 1 % Fehler und {tiny['majority']} für höchstens 10^(−6); "
        f"einseitiger Fehler je Lauf 1/2 (RP) genügt mit {small['one_sided']} bzw. {tiny['one_sided']} Läufen. Der Preis der Zweiseitigkeit ist eine Größenordnung mehr Wiederholungen."
    )
