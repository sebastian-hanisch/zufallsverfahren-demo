"""Zufall in der Komplexität: Freivalds, Miller–Rabin, RP und BPP - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Achtes Stück der Komplexitätsklassen-Reihe: was der Zufall kauft und wie sicher eine Antwort ist, die nur mit Wahrscheinlichkeit richtig ist. Die Fehlerwahrscheinlichkeit wird exakt gezählt (alle Vektoren,
alle Basen), nicht simuliert. Aufwand in Multiplikationen, nie in Sekunden.
Aufbau und Regeln stehen im DEMO-PLAYBOOK.md (§2).

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import zfv_algorithm as A
import zfv_constants as C
from zfv_evaluation import (
    Settings,
    analyse,
    bpp_table,
    carmichael_table,
    fmt_fraction,
    fmt_int,
    fmt_percent,
    sweep_freivalds,
    sweep_liars,
    validation_errors,
    verdict_bpp,
    verdict_carmichael,
    verdict_freivalds_sweep,
    verdict_liars,
    verdict_matrix,
    verdict_number,
)
from zfv_layout import dunkles_design, kopf_css
from zfv_pdf_export import build_pdf
from zfv_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sidebar_presets,
    sync_query_params,
)
from zfv_visualization import build_amplification, build_bases, build_bpp, build_carmichael, build_freivalds_sweep, build_liars, build_vectors

st.set_page_config(page_title="Zufall in der Komplexität – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _analysis(settings):
    return analyse(settings)


@st.cache_data(show_spinner=False)
def _mask(a, b, c):
    return A.liar_vectors(a, b, c)[1]


@st.cache_data(show_spinner=False)
def _freivalds():
    return sweep_freivalds()


@st.cache_data(show_spinner=False)
def _liars():
    return sweep_liars()


@st.cache_data(show_spinner=False)
def _carmichael():
    return carmichael_table()


@st.cache_data(show_spinner=False)
def _bpp():
    return bpp_table()


@st.cache_data(show_spinner=False)
def _pdf(settings):
    return build_pdf(analyse(settings))


def _md_table(header, rows):
    lines = ["| " + " | ".join(str(c) for c in header) + " |", "|" + "---|" * len(header)]
    lines += ["| " + " | ".join(str(c) for c in row) + " |" for row in rows]
    return "\n".join(lines)


def _matrix_table(m, reference=None):
    n = len(m)
    return _md_table([""] + list(range(n)), [[i] + [f"**{x}**" if reference is not None and x != reference[i][j] else x for j, x in enumerate(row)] for i, row in enumerate(m)])


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in zfv_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🎲 Zufall in der Komplexität: Freivalds, Miller–Rabin, RP und BPP")
st.markdown(
    """
Manche Verfahren würfeln und sind trotzdem verlässlich, weil sich ihre **Fehlerwahrscheinlichkeit angeben lässt**. **Freivalds** prüft ein Matrixprodukt A · B = C mit einem zufälligen 0/1-Vektor r (A(Br) = Cr) in
O(n²) statt O(n³): ein richtiges Produkt besteht immer, ein falsches fliegt mit Wahrscheinlichkeit mindestens 1/2 auf. **Miller–Rabin** prüft, ob eine Zahl zusammengesetzt ist: eine Primzahl besteht **jede** Basis,
eine zusammengesetzte Zahl höchstens ein Viertel der Basen. Die Demo **zählt die Lügner exakt** (alle 2^n Vektoren, alle Basen) statt sie zu simulieren; eine Stichprobe steht nur als Illustration daneben.
Dazu der Gegenentwurf, der keine solche Schranke hat (der **Fermat-Test** und die Carmichael-Zahlen), und der Preis der **Zweiseitigkeit** (BPP gegen RP). Aufwand wird in **Multiplikationen** gezählt, nicht in Sekunden.
Achtes Stück der Komplexitätsklassen-Reihe; die Fall-Demos behandeln einzelne Anwendungen, hier steht eine Frage der Komplexitätstheorie im Mittelpunkt.

Weiter unten: die Experimente **🔬 Wie scharf ist die Schranke 1/2?**, **🔬 Wie viele Lügner hat eine zusammengesetzte Zahl?**, **🔬 Fermat gegen Miller–Rabin** und **🔬 Ein- gegen zweiseitiger Fehler**,
dann **🚧 Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**.
"""
)

with st.expander("Zufall in der Komplexitätstheorie", expanded=True):
    st.markdown(
        """
1. **Monte Carlo und Las Vegas.** Ein Monte-Carlo-Verfahren antwortet schnell, aber nur **mit Wahrscheinlichkeit** richtig. Ein Las-Vegas-Verfahren antwortet **immer** richtig, nur seine Laufzeit ist zufällig; aus einem Monte-Carlo-Verfahren mit billigem Prüfer wird eines, indem man wiederholt, bis der Prüfer zustimmt.
2. **Einseitig und zweiseitig.** Bei **einseitigem Fehler** irrt das Verfahren nur in eine Richtung: Freivalds sagt nie „falsch“ zu einem richtigen Produkt, Miller–Rabin nie „zusammengesetzt“ zu einer Primzahl. Das ist **RP** bzw. **coRP** (Fehler höchstens 1/2). Bei **zweiseitigem Fehler** (höchstens 1/3) heißt die Klasse **BPP**.
3. **Verstärkung.** Unabhängige Wiederholung drückt den Fehler: einseitig (1/2)^t, zweiseitig über den Mehrheitsentscheid deutlich langsamer. Ob Zufall überhaupt nötig ist (P = BPP), ist offen; **PRIMES ∈ P** (Agrawal, Kayal und Saxena 2004) zeigt, dass er beim Primzahltest am Ende nicht nötig war.
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.markdown("**Matrizen (Freivalds)**")
    n = st.slider("Größe n der Matrizen", *bounds("n_slider"), key="n_slider", help="n × n; alle 2^n Vektoren aus {0, 1}^n werden aufgezählt (bei n = 12 sind das 4.096).")
    seed = st.number_input("Zufalls-Seed", *bounds("seed_input"), key="seed_input", step=1)
    st.button("🎲 Neue Matrizen generieren", width="stretch", on_click=randomize_seed)
    kind = st.selectbox("Fehler im Produkt", list(C.KINDS), format_func=C.KINDS.get, key="kind_select", help="Wie C vom richtigen Produkt A · B abweicht. Am schwersten fallen Fehler auf, die in einer Spalte liegen oder sich in einer Zeile aufheben.")
    runs = st.select_slider("Läufe der Stichprobe", options=list(C.RUNS_OPTIONS), format_func=fmt_int, key="runs_select", help="Nur Illustration: wie oft der Fehler nach t Runden unentdeckt bleibt, wenn man t zufällige Vektoren zieht.")
    st.markdown("**Beide Prüfungen**")
    t = st.slider("Runden t (Vektoren bzw. Basen)", *bounds("t_slider"), key="t_slider", help="Unabhängige Wiederholungen des Tests.")
    st.markdown("**Zahl (Miller–Rabin)**")
    num = st.number_input("Zahl N", *bounds("num_input"), key="num_input", step=1, help="Alle Basen 1 bis N − 1 werden durchgerechnet (für ungerade Zahlen ab 3).")

sync_query_params({"n_slider": int(n), "seed_input": int(seed), "kind_select": kind, "t_slider": int(t), "num_input": int(num), "runs_select": int(runs)})

settings = Settings(n=int(n), seed=int(seed), kind=kind, t=int(t), num=int(num), runs=int(runs))
a = _analysis(settings)
m, z = a.matrix, a.number
for message in validation_errors(a):
    st.error(message)

# --- Matrizen ----------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Stimmt das Produkt? (Freivalds)")
st.markdown(f"Geprüft wird, ob **A · B = C** gilt; in C ist ein Fehler vom Typ „{C.KINDS[settings.kind]}“ (fett). Der Test zieht einen Vektor r aus {{0, 1}}^{settings.n} und vergleicht **A(Br)** mit **Cr**.")
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("**A**")
    st.markdown(_matrix_table(m.a))
with c2:
    st.markdown("**B**")
    st.markdown(_matrix_table(m.b))
with c3:
    st.markdown("**C (falsch)**")
    st.markdown(_matrix_table(m.c_wrong, m.c_true))
d1, d2, d3, d4 = st.columns(4)
d1.metric("Lügende Vektoren", f"{fmt_int(m.liars)} von {fmt_int(m.total)}", help="Vektoren, die den Test trotz des Fehlers bestehen (alle aufgezählt).")
d2.metric("Anteil", fmt_fraction(m.share), help="Höchstens 1/2: bei mindestens der Hälfte der Vektoren fällt der Fehler auf.")
d3.metric(f"Nach {settings.t} Runden unentdeckt", fmt_fraction(m.after_t), help="Anteil hoch t (unabhängige Runden).")
d4.metric("Multiplikationen", f"{fmt_int(m.mults_freivalds)} gegen {fmt_int(m.mults_naive)}", help=f"{settings.t} Runden · 3n² gegen n³ beim Nachrechnen.")
vkind, vtext = verdict_matrix(a)
getattr(st, vkind)(vtext)
g1, g2 = st.columns([2, 3])
mask = _mask(m.a, m.b, m.c_wrong)
with g1:
    st.markdown("**Alle Vektoren** (grün: lügt)")
    st.plotly_chart(build_vectors(mask, settings.n), width="stretch", key="vectors_chart")
with g2:
    st.markdown("**Der Fehler über die Runden**")
    st.plotly_chart(build_amplification(m.share, C.T_MAX, settings.t, m.sample_fails / settings.runs), width="stretch", key="amplification_chart")

st.markdown("## 🎯 Ist die Zahl zusammengesetzt? (Miller–Rabin und Fermat)")
e1, e2, e3, e4 = st.columns(4)
e1.metric("Zahl", fmt_int(z.num), help="Für ungerade Zahlen ab 3 werden alle Basen 1 bis N − 1 durchgerechnet.")
e2.metric("Klasse", z.kind + (" (Carmichael)" if z.carmichael else ""))
if z.kind != "gerade":
    e3.metric("Miller–Rabin besteht", f"{fmt_int(len(z.strong))} von {fmt_int(z.num - 1)}", help="Basen, zu denen die Zahl den starken Test besteht (bei Primzahlen alle).")
    e4.metric("Fermat besteht", f"{fmt_int(len(z.fermat))} von {fmt_int(z.num - 1)}", help="Basen mit a^(N − 1) ≡ 1 (mod N).")
vkind, vtext = verdict_number(a)
getattr(st, vkind)(vtext)
if z.kind != "gerade":
    st.plotly_chart(build_bases(z.num, z.strong, z.fermat), width="stretch", key="bases_chart")
    st.caption("Jeder Strich ist eine Basis, zu der die Zahl den Test besteht. Jeder starke Lügner ist auch ein Fermat-Lügner. "
               f"Ein Durchgang mit Basis 2 kostet {z.mults_base_two} Multiplikationen modulo N (etwa log N).")
if st.button("📄 PDF erstellen"):
    st.session_state["pdf_for"] = settings
if st.session_state.get("pdf_for") == settings:
    st.download_button("⬇️ PDF herunterladen", data=_pdf(settings), file_name="zufall-in-der-komplexitaet.pdf", mime="application/pdf")

st.markdown("## ❓ Kernfrage: Was kauft der Zufall, und wie sicher ist eine wahrscheinlich richtige Antwort?")
st.markdown(
    "Er kauft Geschwindigkeit (Freivalds: n² statt n³) oder Einfachheit (Miller–Rabin), und er verkauft **Gewissheit gegen eine angebbare Wahrscheinlichkeit**. Die Experimente zeigen, wie scharf diese Wahrscheinlichkeiten sind, "
    "wo sie fehlen (Fermat) und was die Zweiseitigkeit kostet."
)

st.markdown("---")

# --- Experimente --------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment: Wie scharf ist die Schranke 1/2?")
st.caption(f"Je Größe n = {', '.join(str(x) for x in C.E1_SIZES)} und Fehlerart {C.E1_PAIRS} feste Matrizenpaare, für jedes **alle 2^n Vektoren** aufgezählt. Dargestellt ist der größte Anteil lügender Vektoren. Unter einer Sekunde.")
if st.button("▶️ Messreihe Freivalds rechnen"):
    st.session_state["freivalds_on"] = True
if st.session_state.get("freivalds_on"):
    with st.spinner("Zähle die lügenden Vektoren (3 Größen, 5 Fehlerarten, 200 Paare) …"):
        sweep = _freivalds()
    st.plotly_chart(build_freivalds_sweep(sweep), width="stretch", key="freivalds_chart")
    st.markdown(_md_table(
        ["n", "Fehlerart", "kleinster Anteil", "Mittel", "größter Anteil", "Paare mit genau 1/2", "Paare über 1/2"],
        [[r["n"], C.KINDS[r["kind"]], fmt_fraction(r["min"]), fmt_fraction(r["mean"]), fmt_fraction(r["max"]), f"{r['at_half']} von {r['pairs']}", r["above_half"]] for r in sweep],
    ))
    vkind, vtext = verdict_freivalds_sweep(sweep)
    getattr(st, vkind)(vtext)

st.markdown("---")

st.subheader("🔬 Experiment: Wie viele Lügner hat eine zusammengesetzte Zahl?")
st.caption(f"Alle ungeraden zusammengesetzten Zahlen von 9 bis {fmt_int(C.LIAR_LIMIT)}, für jede **alle Basen 1 bis n − 1** durchgerechnet (die trivialen Lügner 1 und n − 1 eingerechnet). Rund 5 Sekunden.")
if st.button("▶️ Messreihe Miller–Rabin rechnen"):
    st.session_state["liars_on"] = True
if st.session_state.get("liars_on"):
    with st.spinner(f"Zähle die Lügner aller Zahlen bis {fmt_int(C.LIAR_LIMIT)} …"):
        liars = _liars()
    st.plotly_chart(build_liars(liars), width="stretch", key="liars_chart")
    st.markdown(_md_table(
        ["Zahl n", "Faktoren", "starke Lügner", "Anteil", "Fermat-Lügner", "Anteil"],
        [[fmt_int(r["n"]), " · ".join(str(p) for p in A.factorize(r["n"])), r["strong"], fmt_percent(r["strong_share"]), r["fermat"], fmt_percent(r["fermat_share"])] for r in liars["worst"]],
    ))
    st.caption("Die acht Zahlen mit dem größten Anteil starker Lügner.")
    vkind, vtext = verdict_liars(liars)
    getattr(st, vkind)(vtext)

st.markdown("---")

st.subheader("🔬 Experiment: Fermat gegen Miller–Rabin")
st.caption("Der Fermat-Test besteht eine Zahl, wenn a^(N − 1) ≡ 1 (mod N). **Carmichael-Zahlen** (Korselt: quadratfrei, und p − 1 teilt N − 1 für jeden Primfaktor p) bestehen ihn zu **jeder** teilerfremden Basis.")
carm = _carmichael()
st.plotly_chart(build_carmichael(carm), width="stretch", key="carmichael_chart")
st.markdown(_md_table(
    ["Carmichael-Zahl", "Faktoren", "Fermat-Lügner", "Anteil", "starke Lügner", "Anteil", "teilerfremde Basen φ(N)"],
    [[fmt_int(r["n"]), " · ".join(str(p) for p in r["factors"]), fmt_int(r["fermat"]), fmt_percent(r["fermat_share"]), fmt_int(r["strong"]), fmt_percent(r["strong_share"]), fmt_int(r["phi"])] for r in carm],
))
vkind, vtext = verdict_carmichael(carm)
getattr(st, vkind)(vtext)

st.markdown("---")

st.subheader("🔬 Experiment: Ein- gegen zweiseitiger Fehler")
st.caption("Exakt aus der Binomialverteilung (Brüche, keine Simulation): ein Verfahren, das mit Wahrscheinlichkeit 1/3 **in beide Richtungen** irrt (BPP), wird über den **Mehrheitsentscheid** von t Läufen verstärkt; ein einseitiges Verfahren braucht nur eine Runde, die entlarvt.")
bpp = _bpp()
st.plotly_chart(build_bpp(bpp), width="stretch", key="bpp_chart")
st.markdown(_md_table(
    ["Läufe t", "Mehrheit, Fehler je Lauf 1/3", "einseitig 1/2: (1/2)^t", "einseitig 1/4: (1/4)^t"],
    [[r["t"], fmt_fraction(r["majority"]), fmt_fraction(r["one_sided"]), fmt_fraction(r["one_sided"] ** 2)] for r in bpp["rows"]],
))
vkind, vtext = verdict_bpp(bpp)
getattr(st, vkind)(vtext)

st.markdown("---")

st.subheader("🔬 Einordnung: Las Vegas, ZPP, PRIMES und Karger")
st.markdown(
    "Ein Verfahren, das nie falsch antwortet und nur manchmal lange braucht (**Las Vegas**, Klasse **ZPP** = RP ∩ coRP), entsteht aus zwei einseitigen Verfahren oder aus einem Monte-Carlo-Verfahren mit billigem Prüfer. "
    "Miller–Rabin ist einseitig (RP für „zusammengesetzt“); dass auch „prim“ beweisbar ist, zeigte erst der deterministische Test von Agrawal, Kayal und Saxena (2004): **PRIMES ∈ P**. Zufall war dort am Ende nicht nötig; "
    "ob er es bei allen Problemen nicht ist (P = BPP), ist offen. Ein weiteres Zufallsverfahren des Portfolios ist das zufällige Zusammenziehen von **Karger** im `globaler-schnitt-demo` (Erfolgswahrscheinlichkeit pro Versuch klein, "
    "durch Wiederholung verstärkt)."
)

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Die Schranken sind bewiesen** | Es sind Sätze (Freivalds: höchstens die Hälfte der Vektoren lügt; Rabin: höchstens ein Viertel der Basen). Die Demo **prüft** sie exakt an Instanzen (Matrizen bis 12 × 12, Zahlen bis 5.000), beweist sie nicht. | – |
| **Die Stichprobe belegt die Wahrscheinlichkeit** | Sie ist eine Illustration mit Stichprobenfehler; der Beleg ist die exakte Aufzählung. | – |
| **Die Runden sind unabhängig und echt zufällig** | Hier zieht ein Generator mit festem Zufalls-Seed; die Verstärkung (1/2)^t setzt unabhängige Runden voraus. | – |
| **Alle Fehler sind gleich schwer** | Freivalds erreicht 1/2 bei Fehlern in einer Spalte und bei sich aufhebenden Einträgen einer Zeile; bei einer ganz zufälligen Matrix lügt nur der Nullvektor (2^(−n)). Wer Fehler gezielt so legt, trifft die Schranke. | – |
| **Der Fermat-Test ist ein Primzahltest** | Auf den gezeigten Carmichael-Zahlen (bis 50.000) besteht er die Mehrheit der Basen; ohne die starke Variante ist er kein Test mit Schranke. | – |
| **Zufall ist nötig** | Für den Primzahltest nicht (AKS 2004, deterministisch polynomiell); über die Praxis (Miller–Rabin ist einfacher und schneller) wird hier nichts gemessen. | – |
| **Mehrheitsentscheid ist so billig wie Einseitigkeit** | Er braucht bei Fehler 1/3 eine Größenordnung mehr Läufe (Experiment 4). | – |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(r"**Freivalds.** Sei $D = AB - C \ne 0$ und $r \in \{0, 1\}^n$ gleichverteilt. Der Test besteht genau dann, wenn $D r = 0$. Hat $D$ einen Eintrag $d_{ij} \ne 0$, so ist die $i$-te Komponente $\sum_k d_{ik} r_k$; fixiert man alle $r_k$ mit $k \ne j$, gibt es höchstens einen Wert von $r_j \in \{0, 1\}$, der sie zu 0 macht:")
    st.latex(r"\Pr\big[\, D r = 0 \,\big] \;\le\; \tfrac{1}{2}, \qquad \Pr\big[\text{nach } t \text{ Runden unentdeckt}\big] \;\le\; 2^{-t}")
    st.markdown(r"**Miller–Rabin.** Sei $n - 1 = d \cdot 2^s$ mit $d$ ungerade. $n$ besteht den Test zur Basis $a$, wenn $a^d \equiv 1$ oder $a^{d \cdot 2^r} \equiv -1 \pmod n$ für ein $r < s$. Eine Primzahl besteht jede Basis; für zusammengesetztes ungerades $n > 9$ bestehen höchstens $\varphi(n) / 4$ Basen (Rabin):")
    st.latex(r"\Pr\big[\, n \text{ besteht, obwohl zusammengesetzt} \,\big] \;\le\; \tfrac{1}{4}, \qquad \text{nach } t \text{ Basen: } 4^{-t}")
    st.markdown(r"**Mehrheitsentscheid.** Irrt jeder von $t$ unabhängigen Läufen (ungerades $t$) mit Wahrscheinlichkeit $p < 1/2$ in beide Richtungen, irrt die Mehrheit mit:")
    st.latex(r"\sum_{j = (t+1)/2}^{t} \binom{t}{j}\, p^{j} (1 - p)^{t - j}")
    st.markdown(
        r"""
| Annahme | Bedeutung | Wer setzt an |
|---|---|---|
| Vektoren aus {0, 1}^n | gleichverteilt: jeder der 2^n Vektoren mit Wahrscheinlichkeit 2^(−n) | – |
| Basen 1 bis n − 1 | gleichverteilt; die trivialen Lügner 1 und n − 1 zählen mit | – |
| Anteile als Brüche | Schranken werden exakt verglichen, nie mit Gleitkomma | – |
| Unabhängige Runden | die Verstärkung multipliziert die Fehlerwahrscheinlichkeiten | – |

**Folgestücke.** Dies ist das letzte der acht Kernstücke der Reihe; die Kanten laufen zurück zu Stück 3 (Reduktionen), Stück 4 (Zufallsformeln als Eingabe) und Stück 6 (Approximation).
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
