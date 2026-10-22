# Zufall in der Komplexität: Freivalds, Miller–Rabin, RP und BPP – Streamlit-Demo

<!-- TODO nach dem Deploy: direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-zufallsverfahren-demo.streamlit.app/)** -->

Achtes und letztes Kernstück der **Komplexitätsklassen-Reihe** in der „Konzepte“-Reihe für die Website „Sebastian Hanisch – Operations Research und Machine Learning“. Die Stücke davor zeigen, was bei schweren Problemen bleibt: Härte über Reduktionen weitergeben (Stück 3, [reduktionskette-demo](https://github.com/sebastian-hanisch/reduktionskette-demo)), Zufallsformeln als Eingabe (Stück 4), Güte statt Optimum (Stück 6, [approximation-grenzen-demo](https://github.com/sebastian-hanisch/approximation-grenzen-demo)), einen kleinen Parameter (Stück 7, [parametrisiert-demo](https://github.com/sebastian-hanisch/parametrisiert-demo)). Dieses Stück fragt, was der **Algorithmus selbst** gewinnt, wenn er würfelt: **Was kauft der Zufall, und wie sicher ist eine Antwort, die mit Wahrscheinlichkeit richtig ist?** Anders als die Fall-Demos zeigt es **eine Frage der Komplexitätstheorie** an zwei kleinen Verfahren. Ein weiteres Zufallsverfahren des Portfolios ist das zufällige Zusammenziehen von Karger im [globaler-schnitt-demo](https://github.com/sebastian-hanisch/globaler-schnitt-demo).

## Warum dieses Problem

Zwei Verfahren, bei denen sich die Fehlerwahrscheinlichkeit **exakt zählen** lässt, statt sie zu simulieren. **Freivalds** prüft ein Matrixprodukt A · B = C mit einem zufälligen 0/1-Vektor r: stimmt A(Br) = Cr? Das kostet 3n² statt n³ Multiplikationen; ein richtiges Produkt besteht **immer**, ein falsches fällt höchstens bei der Hälfte der Vektoren nicht auf (einseitiger Fehler, **coRP**). **Miller–Rabin** prüft, ob eine Zahl zusammengesetzt ist: eine Primzahl besteht **jede** Basis, eine ungerade zusammengesetzte Zahl über 9 höchstens ein Viertel der Basen (einseitiger Fehler, **RP** für „ist zusammengesetzt“). Die Demo **zählt die „Lügner“** (alle 2^n Vektoren bis n = 12, alle Basen jeder Zahl bis 4.999) statt sie zu würfeln; eine Stichprobe steht nur als Illustration daneben. Dazu der Gegenentwurf ohne solche Schranke, der **Fermat-Test** mit den **Carmichael-Zahlen**, und der Preis der **Zweiseitigkeit** (**BPP** gegen RP). Aufwand wird in **Multiplikationen** gezählt, nie in Sekunden.

## Modell

- **Matrizen.** A und B haben Einträge 0 bis 9 (eigener SplitMix64-Generator, deshalb auf jeder Plattform dieselben Matrizen); C ist A · B mit einem Fehler einer der fünf Arten: ein Eintrag (+1), zwei Einträge einer Zeile (+1, −1), je ein Eintrag in zwei Zeilen (+3, −2), eine ganze Zeile zufällig, ganz zufällige Matrix. n = 2 bis 12; **alle 2^n Vektoren aus {0, 1}^n** werden durchgerechnet.
- **Freivalds-Durchgang.** Besteht A(Br) = Cr? Kosten 3n² Multiplikationen (zwei Matrix-Vektor-Produkte links, eines rechts). Nach t Runden bleibt der Fehler unentdeckt, wenn jede Runde lügt: Anteil^t (unabhängige Runden).
- **Miller–Rabin.** n − 1 = d · 2^s mit ungeradem d; n besteht zur Basis a, wenn a^d ≡ 1 oder a^(d · 2^r) ≡ −1 (mod n) für ein r < s. **Alle Basen 1 bis n − 1** werden durchgerechnet, die trivialen Lügner 1 und n − 1 sind eingerechnet. Kosten: modulare Multiplikationen von links nach rechts (Quadrieren und Multiplizieren).
- **Fermat-Test.** n besteht zur Basis a, wenn a^(n − 1) ≡ 1 (mod n). **Carmichael-Zahlen** werden nach **Korselt** aus der Definition gerechnet (zusammengesetzt, quadratfrei, p − 1 teilt n − 1 für jeden Primfaktor p), nicht aus dem Gedächtnis.
- **Mehrheitsentscheid.** Irrt ein Lauf in beide Richtungen mit Wahrscheinlichkeit 1/3 (BPP), irrt die Mehrheit von t Läufen mit der Binomialsumme über j > t / 2 (exakt in Brüchen).
- **Stichprobe.** t zufällige Vektoren in 1.000 / 10.000 / 100.000 Läufen: **Illustration, kein Beleg**; der Beleg ist die Aufzählung. Die Prüfung vor der Anzeige verlangt, dass sie höchstens sechs Standardabweichungen vom exakten Wert abweicht.
- Mathematik (Freivalds-Argument, Rabin-Schranke, Binomialsumme) und Annahmentabelle: Expander **📐 Mathematische Formulierung** in der App.

## Methodik

| Baustein | Datei | Anmerkung |
|---|---|---|
| Potenz mit Zählung, Zerlegung, Probedivision, Korselt, Miller–Rabin und Fermat mit allen Basen, Freivalds-Durchgang, Aufzählung aller Vektoren, Fehlerarten, exakte Verstärkung und Mehrheitsentscheid | `zfv_algorithm.py` | eine Regel = eine Funktion; Reihenfolge der Vektoren wie `itertools.product` |
| Matrizenpaare mit falschem Produkt | `zfv_scenario.py` | deterministisch aus Größe, Fehlerart und Zufalls-Seed |
| SplitMix64 | `zfv_rng.py` | **wörtliche Kopie** von reduktionskette-demo/red_scenario.py (Commit ba24648); Regressionstest `tests/test_copies.py` |
| Kennzahlen, Messreihen, Prüfung vor der Anzeige, Verdikte | `zfv_evaluation.py` | alle Anteile als `Fraction`; alle Verdikte reine Funktionen |

Experimente in der App: **Wie scharf ist die Schranke 1/2?** (Knopf, unter einer Sekunde), **Wie viele Lügner hat eine zusammengesetzte Zahl?** (Knopf, rund 5 Sekunden), **Fermat gegen Miller–Rabin** (sofort), **Ein- gegen zweiseitiger Fehler** (sofort), **Einordnung** (Las Vegas, ZPP, PRIMES, Karger; nur Text).

## Befunde (gemessen, keine Behauptungen)

Alle Zahlen stehen in `tests/test_claims.py`. Die Messreihen laufen über feste Instanzen aus dem eigenen Generator, die Presets sind Einzelinstanzen und als solche ausgewiesen.

| Frage | Befund |
|---|---|
| **Wie scharf ist die Schranke 1/2 bei Freivalds?** (H1, H2) | 3 Größen (n = 6 / 8 / 10) · 5 Fehlerarten · 200 Paare = **3.000 Instanzen, alle 2^n Vektoren aufgezählt: der Anteil lügender Vektoren war nie über 1/2.** Genau **1/2 bei jedem der 200 Paare** für „ein Eintrag falsch“ und „zwei Einträge einer Zeile“ (alle drei Größen). „Zwei Zeilen, je ein Eintrag“: kleinster Anteil 1/4, Mittel 231/800 / 227/800 / 221/800, größter 1/2 (bei 31 / 27 / 21 von 200 Paaren genau 1/2). „Ganze Zeile zufällig“: Mittel 53/3200 (≈ 1,7 %) bei n = 6, 203/51200 (≈ 0,40 %) bei n = 8, 1/1024 bei n = 10. „Ganz zufällige Matrix“: **genau 1 Vektor von 2^n lügt** (1/64, 1/256, 1/1024). Die Schranke ist also **scharf**: sie wird bei einem falschen Eintrag, bei zwei sich aufhebenden Einträgen einer Zeile und bei Fehlern erreicht, die in einer Spalte liegen („zwei Zeilen, je ein Eintrag“, wenn beide Einträge in derselben Spalte stehen); Fehler, die über viele Spalten streuen, fallen fast sicher auf (ganz zufällige Matrix: nur der Nullvektor lügt, 2^(−n)); „ganze Zeile zufällig“ liegt weit darunter (`test_claim_freivalds_table`, `test_claim_the_bound_is_never_exceeded_and_exactly_met_for_errors_in_one_row`, `test_claim_random_errors_leave_two_to_the_minus_n_liars`). |
| **Wie wirkt die Wiederholung?** (H3) | Aus dem exakten Anteil folgt Anteil^t, bei 1/2: 1/2, 1/4, 1/8, 1/16, 1/32, 1/256 für t = 1, 2, 3, 4, 5, 8 (`test_claim_amplification_is_share_to_the_t`). Standardfall (n = 10, ein Eintrag, 3 Runden): exakt 1/8 = 12,5 %, Stichprobe (10.000 Läufe, **Illustration**) 1.207 Läufe = 12,07 % (`test_claim_standard_case_texts`). |
| **Wann ist Freivalds billiger als Nachrechnen?** (H4) | t · 3n² gegen n³: **Gleichstand bei t = n / 3** (n = 12, t = 4: je 1.728; n = 30, t = 10: je 27.000), darunter ist Freivalds billiger, darüber nicht. n = 100: 1.000.000 gegen 30.000 / 150.000 / 300.000 für t = 1 / 5 / 10. Standardfall n = 10, t = 3: **900 gegen 1.000** Multiplikationen; Lehrbeispiel n = 3, t = 2: 54 gegen 27, hier ist Nachrechnen billiger (`test_claim_cost_freivalds_against_recomputing`). |
| **Wie viele Lügner hat eine zusammengesetzte Zahl?** (H5, H6) | **1.831 ungerade Zusammengesetzte von 9 bis 5.000, alle Basen 1 bis n − 1 gezählt: der Anteil starker Lügner war an keiner Zahl über 1/4**; der größte Anteil überhaupt ist **1/4 bei n = 9** (Basen 1 und 8 bestehen, 2 von 8), danach 5/21 = 23,8 % (n = 1.891: 450 von 1.890), 3/13 = 23,1 % (n = 703), 1/5 (n = 91), 9/50 (n = 2.701), 1/6 (n = 25), 11/70 (n = 1.541), 5/34 (n = 341). **Typisch fast keine:** Median 0,13 % (1/753), Mittel 0,65 %; bei **1.261 von 1.831** Zahlen sind nur die beiden trivialen Basen 1 und n − 1 Lügner (`test_claim_liar_sweep`, `test_claim_typical_composites_have_almost_no_liars`, `test_claim_nine_is_exactly_one_quarter`). |
| **Gilt die Schranke für den Fermat-Test?** (H7) | **Nein.** Unter denselben 1.831 Zahlen liegt der Fermat-Anteil bei **5 Zahlen über 1/2**: 561, 1.105, 1.729, 2.465, 2.821. Die **12 Carmichael-Zahlen bis 50.000** (aus Korselt gerechnet; 561, 1.105, 1.729, 2.465, 2.821, 6.601, 8.911, 10.585, 15.841, 29.341, 41.041, 46.657): Fermat-Lügner **57,1 % (561) bis 88,9 % (46.657)** der Basen, und zwar jeweils **genau die zu n teilerfremden Basen** (Anzahl φ(n), z. B. 320 bei 561, 1.296 bei 1.729); Miller–Rabin bleibt bei **1,1 % (41.041) bis 20 % (8.911)**, bei 561 sind es 10 von 560 (`test_claim_carmichael_table`, `test_claim_carmichael_shares`). |
| **Was kostet die Zweiseitigkeit?** (H8) | Mehrheitsentscheid aus t Läufen mit Fehler 1/3 je Lauf: 1/3, 7/27, 17/81 für t = 1, 3, 5; 12,21 % / 5,57 % / 0,69 % / 0,03 % für t = 11 / 21 / 51 / 101. Für höchstens 1 % Fehler braucht er **47** Läufe, für höchstens 10^(−6) **193**; ein einseitiges Verfahren mit Fehler 1/2 je Lauf kommt mit **7** bzw. **20** aus (`test_claim_two_sided_error_costs_more_rounds`). |
| **Presets (Einzelinstanzen)** | Lügende Vektoren / Multiplikationen Freivalds gegen Nachrechnen / starke und Fermat-Lügner der Zahl / Multiplikationen einer Basis-2-Prüfung: **Standardfall** (n = 10, ein Eintrag, t = 3, N = 561): 512 von 1.024; 900 gegen 1.000; 10 und 320; 10. **Lehrbeispiel** (n = 3, t = 2, N = 15): 4 von 8; 54 gegen 27; 2 und 4; 4. **Strukturierter Fehler** (zwei Einträge einer Zeile): 512 von 1.024. **Zufälliger Fehler**: 1 von 1.024, nach 3 Runden unentdeckt 1/1.073.741.824. **Carmichael-Zahl 1.729**: 162 und 1.296 von 1.728 Basen; 12. **Zahl mit vielen Lügnern (1.891 = 31 · 61)**: 450 von 1.890 (23,8 %) und 900 (`test_claim_presets_are_single_instances_with_these_values`, `test_claim_preset_help_texts_quote_these_numbers`). |
| **Handwerte** | 3^13 mod 7 = 3 mit 5 Multiplikationen; 561 − 1 = 35 · 2^4, 2^35 mod 561 = 263 (7 Multiplikationen), danach drei Quadrate ohne −1: 561 fällt bei Basis 2 durch (10 Multiplikationen); 561 = 3 · 11 · 17 und 2, 10, 16 teilen 560 (`test_claim_hand_values_of_the_small_cases`). |

### Hypothesen des Plans

| | Hypothese | Ergebnis |
|---|---|---|
| H1 | Der Anteil lügender Vektoren bei Freivalds ist höchstens 1/2 | **Ja**, an allen 3.000 Instanzen exakt aufgezählt (und an über 600 weiteren im Orakel-Test) |
| H2 | Die Schranke ist scharf | **Ja**, bei einem Eintrag, bei zwei sich aufhebenden Einträgen einer Zeile und bei Fehlern in einer Spalte (genau 1/2); über viele Spalten gestreute Fehler fallen fast sicher auf |
| H3 | Nach t Runden ist der Fehler (1/2)^t | **Ja**, als Folge des exakten Anteils bei unabhängigen Runden; die Stichprobe stimmt im Rahmen des Stichprobenfehlers |
| H4 | Freivalds ist billiger als Nachrechnen | **Nur für t < n / 3** Runden; bei n = 3, t = 2 nicht |
| H5 | Zusammengesetzte Zahlen haben höchstens 1/4 starke Lügner | **Ja**, an allen 1.831 Zahlen bis 5.000 exakt gezählt (n = 9 genau 1/4, sonst höchstens 5/21); die Schranke ist ein Satz (Rabin), hier **an Instanzen geprüft, nicht bewiesen** |
| H6 | Typische Zusammengesetzte haben fast keine Lügner | **Ja**, Median 0,13 % |
| H7 | Der Fermat-Test hat auf Carmichael-Zahlen keine brauchbare Schranke | **Ja**, bei den 12 Carmichael-Zahlen bis 50.000 57,1 % bis 88,9 % Lügner |
| H8 | Zweiseitiger Fehler braucht viel mehr Wiederholungen | **Ja**, 47 gegen 7 Läufe für 1 % |
| H9 | Zufall ist für Primzahltests nötig | **Nein**: der deterministische Test von Agrawal, Kayal und Saxena (2004) ist polynomiell; Miller–Rabin bleibt das einfachere Verfahren (über die Praxis wird hier nichts gemessen) |

## Ehrliche Grenzen

- **Die Schranken sind Sätze, die Demo beweist sie nicht.** Sie prüft sie exakt an Instanzen (Matrizen bis 12 × 12, Zahlen bis 5.000; die Carmichael-Reihe bis 50.000). Für größere Instanzen sagt die Demo nichts, was nicht aus dem Satz folgt.
- **Die Stichprobe belegt nichts.** Sie ist eine Illustration mit Stichprobenfehler; der Beleg ist die vollständige Aufzählung der Vektoren bzw. der Basen.
- **Die Runden sind hier unabhängig, weil sie es per Konstruktion sind.** Ein Generator mit festem Zufalls-Seed ist kein echter Zufall; die Verstärkung (1/2)^t setzt unabhängige, gleichverteilte Runden voraus.
- **Freivalds erreicht 1/2 bei Fehlern in einer Spalte und bei sich aufhebenden Einträgen einer Zeile.** Wer Fehler gezielt so platziert, trifft die Schranke; über viele Spalten gestreute Fehler fallen fast sicher auf. Welche Fehler „typisch“ sind, hängt vom Anwendungsfall ab; die Demo misst fünf Arten.
- **„Billiger“ heißt hier weniger Multiplikationen.** Bei n ≤ 12 sind alle Aufwände klein; der Vorteil von n² gegen n³ zeigt sich erst bei großen n und wird hier nur gerechnet (n = 100), nicht gemessen. Bei n = 3 ist Nachrechnen billiger.
- **Der Mehrheitsentscheid setzt Fehler unter 1/2 in beide Richtungen voraus** und unabhängige Läufe; die Zahlen 47 und 193 gelten für Fehler 1/3 je Lauf.
- **Miller–Rabin ist hier das einfache Verfahren.** Deterministische Varianten mit festen Basismengen, Solovay–Strassen und die Praxis (Schlüsselerzeugung) sind nicht Teil der Demo. Dass der Zufall für Primzahltests nicht nötig ist (AKS), ist eine Aussage über die Komplexität, nicht über die schnellste Praxis.
- **P = BPP ist offen.** Die Demo zeigt keinen Beleg für oder gegen die Derandomisierung.
- **Die Presets sind Einzelinstanzen**, die Messreihen über feste Instanzen; Aussagen über „alle“ Matrizen gelten nur über den Satz, nicht über die Demo.

## Befunde und Korrekturen gegenüber dem Plan

- **Standardgröße n = 10 statt 8 (Plan):** Mit n = 8 und t = 3 kostet Freivalds 576 Multiplikationen gegen 512 beim Nachrechnen; die Demo würde ihre eigene Aussage im Standardfall widerlegen. Bei n = 10 sind es 900 gegen 1.000.
- **Handwert korrigiert:** 3^13 mod 7 kostet 5 Multiplikationen (Plan: 6) bei der gewählten Variante von links nach rechts (3 Quadrate, 2 Multiplikationen).
- **Carmichael-Liste aus der Rechnung:** Die Vormessung hatte die Liste aus dem Gedächtnis; die Rechnung nach Korselt liefert bis 50.000 **12** Zahlen, darunter 10.585 und 15.841, die in der Vormessung fehlten.
- **Messreihen aus anderen Instanzen als in der Vormessung:** Einzelne Mittelwerte weichen ab (zwei Zeilen bei n = 6: Mittel 231/800 ≈ 0,289 statt 0,30; ganze Zeile bei n = 10: genau 1/1024 statt „größter 0,002“), die Gestalt ist dieselbe. Die Zahlen oben sind die der Demo.
- **Stichprobe höchstens 100.000 Läufe** (Plan: 200.000), damit der Regler bei n = 12 schnell bleibt; sie ist Illustration.
- **Preset „Zahl mit vielen Lügnern (1.891)“ statt „Schwerste kleine Zahl“:** Die Zahl 9 hat mit genau 1/4 den größten Anteil überhaupt; 1.891 hat den größten Anteil unter den Zahlen über 9.
- **Messreihen hinter Knöpfen:** die Freivalds-Reihe und die Reihe über alle Zahlen bis 5.000 laufen erst auf Klick (Freivalds unter einer Sekunde, Zahlen rund 5 Sekunden, auf dem Entwicklungsrechner gemessen).

## Verifikation

- **Kern:** jede Einheit gegen Handrechnung an Mini-Instanzen (`tests/conftest.py`, `tests/test_algorithm.py`): Potenz mit Zählung, Zerlegung n − 1 = d · 2^s, Miller–Rabin für n = 9 (Basis 8 besteht, Basis 2 nicht), Fermat, Korselt, Freivalds-Durchgang an der 2 × 2-Matrix mit allen vier Vektoren, Fehlerarten, Binomialsumme t = 3 (7/27), Randfälle (gerade Zahlen, Basis außerhalb 1 bis n − 1, n = 1, negative Exponenten, Fehlerarten bei n = 1, gerade Rundenzahl beim Mehrheitsentscheid).
- **Orakel** (`tests/test_oracle_zufallsverfahren.py`): Miller–Rabin ein **zweites Mal aus der Definition** durch wiederholte Multiplikation (kein `pow`) für alle ungeraden n bis 400 und alle Basen; Primzahlen bestehen jede Basis, der Anteil starker Lügner ist für alle ungeraden Zusammengesetzten 9 < n ≤ 2.000 höchstens 1/4 (n = 9 genau 1/4); die Korselt-Zahlen sind **genau** die ungeraden Zusammengesetzten, bei denen jede teilerfremde Basis den Fermat-Test besteht (561, 1.105, 1.729 bis 2.000); die aufgezählte Maske gleicht für jeden der 2^n Vektoren dem Durchgang `freivalds_round` und dem ausmultiplizierten (AB − C)r = 0 (n = 2 bis 6, alle Fehlerarten, 8 Seeds), ein richtiges Produkt besteht alle Vektoren, ein falsches höchstens die Hälfte (über 600 falsche Produkte); `majority_error` gegen die Aufzählung aller 2^t Ausgänge für t ≤ 15; die Auswertung läuft über ein Raster von Einstellungen ohne Prüffehler, die vollen Messreihen halten die Schranken.
- **Kopie** (`tests/test_copies.py`): wortgleich mit dem Original, solange es im Portfolio-Ordner liegt, dazu die bekannten ersten Werte der SplitMix64-Konvention.
- **Prüfung vor der Anzeige:** `validation_errors` prüft das falsche Produkt (ist falsch, C richtig = AB), die Zahl der Lügner gegen eine zweite Rechnung (D = AB − C ausmultipliziert), die Schranke 1/2, die Stichprobe (sechs Standardabweichungen ab 1.000 Läufen), die Klasse der Zahl gegen die Probedivision, Primzahlen (alle Basen), Zusammengesetzte (Schranke 1/4 an jeder Zahl, bei n = 9 genau, starke ⊆ Fermat-Lügner), die Carmichael-Eigenschaft gegen Korselt und die Fermat-Lügner (genau die teilerfremden Basen); jede Meldung wird einzeln ausgelöst, auch an den Grenzen (`tests/test_evaluation.py`).
- **Verdikte** als reine Funktionen, jede Zahl im Text und jede Schwelle an handgesetzten Werten (`tests/test_verdicts.py`); **Claims:** jede Zahl dieser README (`tests/test_claims.py`).
- **Presets:** vollständig, gültige Werte, Hilfetexte erst nach der Messung geschrieben, erstes Preset gleich Standard, jedes Preset ohne Prüffehler (`tests/test_presets.py`); Randfälle der Regler (`tests/test_edge_cases.py`).
- **Oberfläche:** AppTest-Rauchtest (jeder Button, jeder Regler an den Grenzen), beide Messreihen-Knöpfe einzeln (`tests/test_app_sweeps.py`), Permalink mit Begrenzung, Layout, Footer, Abbildungen und PDF (`tests/test_visualization.py`).
- **Browser:** Standardansicht, beide Messreihen per Klick, Preset-Wechsel; keine Konsolenmeldung.

## Mutationsprüfung und großer Lauf

- **Großer Lauf im Scratch-Ordner (nicht im Repo):** 2.265.269 Prüfungen, **0 Abweichungen**: Miller–Rabin gegen die Lehrbuchfassung für **jede** ungerade Zahl bis 3.000 und **alle** Basen (rund 2,25 Millionen Paare), Primzahlen bestehen alle Basen, Rabin-Schranke an jeder Zusammengesetzten, starke ⊆ Fermat-Lügner, Korselt-Zahlen gegen „jede teilerfremde Basis besteht“, die Zählung der Multiplikationen von `mod_pow` für alle Exponenten bis 3.999, die aufgezählte Maske gegen (AB − C)r = 0 in reinem Python auf 3.600 Matrizenpaaren (n = 2 bis 7, alle Fehlerarten; ein richtiges Produkt besteht jeden Vektor, ein falsches höchstens die Hälfte), `majority_error` gegen die Aufzählung für drei Fehlerwahrscheinlichkeiten, und die Auswertung samt Prüfung vor der Anzeige für 403 Zahlen.
- **Mutationsprüfung** (`tools/mutate_demo.py`, über `zfv_algorithm.py` und `zfv_evaluation.py`; Darstellung, PDF, Presets, Szenario und Oberfläche mutiert das Werkzeug nicht, sie sind durch Rauch-, Verdikt-, Claims- und Orakel-Tests abgesichert; die wörtliche Kopie `zfv_rng.py` ist ausgenommen, ihre Tests liegen in Stück 3): **331 Stellen**, davon **314 gefangen**, **10 als äquivalent festgehalten** (`tests/mutation_state.json`), 4 durch wortgleiche Zeilen in Nachbar-Demos gesichert und 3 Endlosschleifen-Mutanten durch Zeitüberschreitung (zählen nicht). Die Lücken der ersten Läufe wurden mit Grenztests geschlossen: die Prüfung von Modul und Basis allein (`fermat_pass` und `strong_pass` vor `decompose`), die zweite Zeile der Fehlerart „zwei Zeilen“ (nie die erste, jeder Abstand kommt vor), `factorize(2)`, `one_sided_rounds` mit Fehler 0, negative Brüche im Format, die Obergrenze der Messreihe über Zahlen (eine ungerade zusammengesetzte Grenze gehört dazu), die Schwellen genau bei 1/4 und 1/2 der Zusammenfassung (an handgesetzten Zeilen, dafür `summarise_liars` ausgelagert) und die Aufzählung der Fehlerarten im Verdikt der Messreihe (nur die kleinste Größe). Aus dem Befund folgte eine Vereinfachung: Die Ausnahme „n > 9“ bei der Schranke 1/4 war überflüssig, denn über **alle** Basen 1 bis n − 1 gezählt gilt 1/4 auch für n = 9 (genau); der Code prüft jetzt ohne Ausnahme. Äquivalent sind: die Grenzen 3 gegen 2 oder 4 in `_check`, `decompose` und `is_carmichael` (die Zahlen 2 und 3 werden schon durch die Parität bzw. durch die Probedivision abgefangen), `t < 1` gegen `t < 0` im Mehrheitsentscheid (t = 0 ist gerade), mehr Quadrate in `strong_pass` (ein weiteres Quadrat ergibt nie −1: dafür müsste jeder Primfaktor p ≡ 1 mod 2^(s+1) sein, was n − 1 = d · 2^s mit ungeradem d widerspricht), `0 < x` gegen `0 <= x` im Format (der Wert 0 ist eine ganze Zahl und wird vorher abgefangen) und `+ 1e-9` gegen `− 1e-9` in der Toleranz der Stichprobe (nur gegen Gleitkomma-Gleichheit).

## Einordnung und Quellen (anhand der Quellen geprüft)

**Geprüft:** Agrawal, Kayal und Saxena, *PRIMES is in P*, Annals of Mathematics 160 (2004), S. 781 bis 793 (deterministisch, polynomiell). Alford, Granville und Pomerance, *There are infinitely many Carmichael numbers*, Annals of Mathematics 139 (1994), S. 703 bis 722 (eine Quelle nennt Band 140). **Nach der Literatur, Journal-Angaben nicht geprüft:** der Miller–Rabin-Test mit Fehler unter 1/4 (Rabin 1980; die Schranke selbst prüft die Demo an den Instanzen). **Nicht nachgeschlagen:** Freivalds 1977 (Prüfung von Matrixprodukten mit Zufall), Miller 1976, die Aussage zur Derandomisierung (P = BPP ist offen) und die Beziehungen P ⊆ RP ⊆ NP und P ⊆ BPP, die in der App als Lehrbuchwissen genannt sind. Das Korselt-Kriterium ist die übliche Lehrbuchfassung und wird hier gegen die Fermat-Lügner geprüft, nicht zitiert.

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App: Freivalds mit allen Vektoren, Miller–Rabin und Fermat mit allen Basen, Kernfrage, vier Experimente, Einordnung, Annahmentabelle, Formeln |
| `requirements-dev.txt` | Laufzeit plus pytest |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `zfv_algorithm.py` | Kern: Potenz, Miller–Rabin, Fermat, Korselt, Freivalds, Fehlerarten, Verstärkung, Mehrheitsentscheid |
| `zfv_constants.py` | Regler-Grenzen, Rechengrenzen, Messreihen-Parameter, Farben, Presets mit Hilfetexten |
| `zfv_evaluation.py` | Analyse, Messreihen, Prüfung vor der Anzeige, Verdikte, Zahlenformate |
| `zfv_layout.py` | Fester Kopf (Stylesheet) |
| `zfv_pdf_export.py` | PDF-Bericht (fpdf2) |
| `zfv_presets.py` | Permalink (Begrenzen), Presets (Schnellstart in der Seitenleiste, aktives Preset hervorgehoben), Zufalls-Seed-Button |
| `zfv_rng.py` | wörtliche Kopie: SplitMix64 aus Stück 3 |
| `zfv_scenario.py` | Matrizenpaare mit falschem Produkt |
| `zfv_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `tests/` | Mini-Instanzen, Orakel, Kopie, Auswertung, Verdikte, Claims, Presets, Randfälle, Layout, AppTest-Smoke-Test und Messreihen-Knöpfe, Footer, Laufzeit-Importe |

## Bewusst nicht umgesetzt

- **Schwartz–Zippel / Polynomidentitätstest:** Freivalds ist selbst ein solcher Test; ein drittes Verfahren würde das Stück verwässern, es wird nur im Text genannt.
- **Deterministische Basismengen für Miller–Rabin, Solovay–Strassen:** andere Verfahren derselben Klasse, hier nicht gebaut.
- **Las-Vegas-Beispiele:** Las Vegas und ZPP stehen als Einordnung im Text (RP ∩ coRP), ohne eigenes Verfahren.
- **Zufall aus einer echten Quelle:** hier ein Generator mit festem Zufalls-Seed, damit jede Zahl reproduzierbar ist.
- **Größere Instanzen:** Matrizen über 12 × 12 und Zahlen über 4.999 wären nicht mehr vollständig zählbar.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly, NumPy und fpdf2.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
