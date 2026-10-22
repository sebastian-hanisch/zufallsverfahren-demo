"""PDF-Export (fpdf2, Kernschriften): Einstellungen, Ergebnis der Matrizenprüfung und der Zahlenprüfung, die Matrizen. Kein Gedankenstrich und kein Euro-Zeichen (Kernschriften)."""

from fpdf import FPDF

import zfv_constants as C
import zfv_evaluation as ev


def _text(value: str) -> str:
    """Zeichen, die die Kernschriften nicht kennen, ersetzen (Gedankenstrich, Pfeile, Fettdruck-Markierung, mathematische Zeichen)."""
    table = {"–": "-", "—": "-", "→": "->", "**": "", "€": "EUR", "·": "*", "³": "^3", "≤": "<=", "≥": ">=", "−": "-", "×": "x", "„": '"', "“": '"', "⇔": "<=>", "²": "^2", "ℓ": "l"}
    for old, new in table.items():
        value = value.replace(old, new)
    return value


def _para(pdf: FPDF, height: float, text: str) -> None:
    """Absatz über die volle Breite; danach steht der Cursor wieder am linken Rand (fpdf2 setzt ihn sonst an den rechten Rand)."""
    pdf.multi_cell(0, height, _text(text), new_x="LMARGIN", new_y="NEXT")


def build_pdf(a: ev.Analysis) -> bytes:
    s, m = a.settings, a.matrix
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Helvetica", "B", 15)
    pdf.cell(0, 9, _text("Zufall in der Komplexität: Freivalds und Miller–Rabin"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    _para(pdf, 5.5, f"Matrizen: {s.n} x {s.n}   Fehlerart: {C.KINDS[s.kind]}   Zufalls-Seed: {s.seed}   Runden: {s.t}   Zahl: {s.num}")
    pdf.ln(1)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, "Ergebnis", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    _para(pdf, 5.5, ev.verdict_matrix(a)[1])
    _para(pdf, 5.5, ev.verdict_number(a)[1])
    pdf.ln(1)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, "Matrizen", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Courier", "", 8)
    for name, mat in (("A", m.a), ("B", m.b), ("C (falsch)", m.c_wrong)):
        _para(pdf, 4.2, f"{name}:")
        for row in mat:
            _para(pdf, 4.2, "  " + " ".join(f"{x:5d}" for x in row))
    pdf.ln(2)
    pdf.set_font("Helvetica", "I", 8)
    _para(pdf, 4.5, "Aufwand in Multiplikationen, nicht in Sekunden. Sebastian Hanisch - Operations Research und Machine Learning.")
    return bytes(pdf.output())
