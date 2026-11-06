"""Checklist schematic diagrams and RDKit structures. Run from repo root: python3 tools/checklist/figs_diagrams.py
Needs: pip install rdkit"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from figlib import Diagram, PAL, mol, mols
OUT = os.path.join(os.path.dirname(os.path.dirname(HERE)), "play/fig/chk"); os.makedirs(OUT, exist_ok=True)
P = lambda n: os.path.join(OUT, n + ".svg")

def zig(d, x1, y1, x2, y2, n=6, amp=7, color="ink"):
    """Resistor zigzag from (x1,y1) to (x2,y2)."""
    L = math.hypot(x2 - x1, y2 - y1); ux, uy = (x2 - x1) / L, (y2 - y1) / L; px, py = -uy, ux
    pts = [(x1, y1)]
    for k in range(1, 2 * n):
        t = k / (2 * n); s = amp if k % 2 else -amp
        pts.append((x1 + ux * L * t + px * s, y1 + uy * L * t + py * s))
    pts.append((x2, y2)); d.line([(round(a, 1), round(b, 1)) for a, b in pts], color=color, width=2)

def battery(d, x, y1, y2, label="battery"):
    """Vertical battery between y1 (top) and y2 (bottom) at x; long plate (+) on top."""
    m = (y1 + y2) / 2
    d.line([(x, y1), (x, m - 6)], width=2); d.line([(x, m + 6), (x, y2)], width=2)
    d.line([(x - 16, m - 6), (x + 16, m - 6)], width=3); d.line([(x - 8, m + 6), (x + 8, m + 6)], width=5)
    d.text(x - 26, m - 8, "+", size=15, weight=700, color=PAL["red"]); d.text(x - 26, m + 10, "−", size=15, weight=700, color=PAL["blue"])

def meter(d, x, y, s, fill):
    d.circle(x, y, 14, s, fill=fill, stroke="ink", size=14)

# ---------- CPAS-03 Venturi ----------
d = Diagram(660, 270)
top = [(30, 90), (220, 90), (280, 125), (400, 125), (460, 90), (630, 90)]; bot = [(x, 270 - 60 - (y - 90) + 90 - 30) for x, y in top]
bot = [(30, 210), (220, 210), (280, 175), (400, 175), (460, 210), (630, 210)]
d.raw('<polygon points="' + " ".join(f"{x},{y}" for x, y in top + bot[::-1]) + f'" fill="{PAL["blueL"]}" stroke="none"/>')
d.line(top, width=2.5); d.line(bot, width=2.5)
for x0 in (60, 130): d.arrow((x0, 150), (x0 + 40, 150), color="blue")
d.arrow((300, 150), (380, 150), color="blue", width=3)
for x0 in (490, 560): d.arrow((x0, 150), (x0 + 40, 150), color="blue")
for x, h, lab in [(125, 70, "P₁ high"), (340, 30, "P₂ low"), (545, 70, "P₃ high")]:
    ybase = 90 if x != 340 else 125
    d.raw(f'<rect x="{x - 9}" y="{ybase - 80}" width="18" height="80" fill="#fff" stroke="{PAL["line"]}"/>')
    d.raw(f'<rect x="{x - 9}" y="{ybase - h}" width="18" height="{h}" fill="{PAL["blue"]}" opacity=".55"/>')
    d.text(x + 16, ybase - 70, lab, size=13, weight=700, anchor="start", color=PAL["red"] if "low" in lab else PAL["ink"])
d.text(125, 236, "wide: A big → v slow", size=13); d.text(340, 236, "narrow: A small → v fast", size=13, weight=700); d.text(545, 236, "wide again: v slow", size=13)
d.text(330, 258, "A₁v₁ = A₂v₂ and Bernoulli: faster flow → lower pressure", size=12, color=PAL["sub"])
d.save(P("cpas03-venturi"))

# ---------- CPAS-05 converging lens ray diagram ----------
d = Diagram(700, 320); ax_y, lx, f, o, ho = 170, 340, 80, 200, 70
i = 1 / (1 / f - 1 / o); m = -i / o; ix, hi = lx + i, m * ho
d.line([(20, ax_y), (680, ax_y)], color="line", width=1.2)
d.raw(f'<ellipse cx="{lx}" cy="{ax_y}" rx="12" ry="120" fill="{PAL["tealL"]}" stroke="{PAL["teal"]}" stroke-width="2"/>')
for x, lab in [(lx - f, "F"), (lx + f, "F"), (lx - 2 * f, "2F"), (lx + 2 * f, "2F")]:
    d.circle(x, ax_y, 3.5, fill="ink", stroke="ink"); d.text(x, ax_y + 16, lab, size=13, weight=700)
ox, oy = lx - o, ax_y - ho; iy = ax_y - hi
d.arrow((ox, ax_y), (ox, oy), color="green", width=3); d.text(ox, oy - 14, "object", size=13, color=PAL["green"], weight=700)
d.arrow((ix, ax_y), (ix, iy), color="red", width=3); d.text(ix - 30, iy + 62, "image: real, inverted, smaller", size=13, color=PAL["red"], weight=700, anchor="start")
d.line([(ox, oy), (lx, oy), (ix + 60, oy + (iy - oy) / (ix - lx) * (ix + 60 - lx))], color="amber", width=1.6)
d.line([(ox, oy), (ix + 60, ax_y + (ax_y - oy) / (lx - ox) * (ix + 60 - lx))], color="purple", width=1.6)
d.line([(ox, oy), (lx, iy), (ix + 60, iy)], color="blue", width=1.6)
d.text(350, 22, "1/f = 1/o + 1/i:  f = 8, o = 20 → i = 13.3 (+, real),  m = −i/o = −0.67", size=13, color=PAL["sub"])
d.save(P("cpas05-lens"))

# ---------- CPAS-12 series vs parallel ----------
d = Diagram(720, 300)
d.text(180, 22, "Series: one path, same current", size=15, weight=700); d.text(540, 22, "Parallel: same voltage across each branch", size=15, weight=700)
# series loop
L, R, T, B = 50, 310, 70, 250
battery(d, L, T, B)
d.line([(L, T), (95, T)], width=2); meter(d, 110, T, "A", "amberL"); d.line([(124, T), (140, T)], width=2)
zig(d, 140, T, 200, T); d.line([(200, T), (235, T)], width=2); zig(d, 235, T, 295, T); d.line([(295, T), (R, T), (R, B), (L, B)], width=2)
d.text(170, T + 22, "R₁", size=13, weight=700); d.text(265, T + 22, "R₂", size=13, weight=700)
d.line([(140, T), (140, T + 45)], width=1.5, dash=True); d.line([(200, T), (200, T + 45)], width=1.5, dash=True)
d.line([(140, T + 45), (156, T + 45)], width=1.5); d.line([(184, T + 45), (200, T + 45)], width=1.5); meter(d, 170, T + 45, "V", "greenL")
d.text(180, 165, "ammeter (A) in series:\nideal R = 0", size=12, color=PAL["sub"]); d.text(180, 210, "voltmeter (V) across R₁:\nideal R = ∞", size=12, color=PAL["sub"])
# parallel
L2, R2 = 410, 690
battery(d, L2, T, B)
d.line([(L2, T), (450, T)], width=2); meter(d, 465, T, "A", "amberL"); d.line([(479, T), (R2, T)], width=2); d.line([(L2, B), (R2, B)], width=2)
for x, lab in [(560, "R₁"), (650, "R₂")]:
    d.line([(x, T), (x, 120)], width=2); zig(d, x, 120, x, 200); d.line([(x, 200), (x, B)], width=2); d.text(x - 20, 160, lab, size=13, weight=700)
d.line([(650, 110), (680, 110), (680, 145)], width=1.5, dash=True); d.line([(650, 210), (680, 210), (680, 175)], width=1.5, dash=True); meter(d, 680, 160, "V", "greenL")
d.text(470, 225, "I = I₁ + I₂", size=13, color=PAL["blue"], weight=700)
d.text(360, 285, "Series: R_eq = R₁ + R₂     Parallel: 1/R_eq = 1/R₁ + 1/R₂ (smaller than either)", size=12.5, color=PAL["sub"])
d.save(P("cpas12-circuits"))

# ---------- CPAS-13 dielectric table ----------
d = Diagram(640, 300, title="Slide in a dielectric (κ > 1)")
rows = [("Capacitance C", "↑ ×κ", "↑ ×κ"), ("Voltage V", "same (locked)", "↓ ÷κ"), ("Charge Q", "↑ ×κ", "same (locked)"),
        ("Field E = V/d", "same", "↓ ÷κ"), ("Stored energy U", "↑ (½CV²)", "↓ (Q²/2C)")]
d.box(220, 44, 200, 40, "Battery connected", fill="blueL", stroke="blue", weight=700); d.box(425, 44, 200, 40, "Battery disconnected", fill="amberL", stroke="amber", weight=700)
for k, (a, b, c) in enumerate(rows):
    y = 90 + k * 40
    d.box(15, y, 200, 36, a, fill="grayL", weight=700, size=13)
    for x, s in [(220, b), (425, c)]:
        col = PAL["green"] if "↑" in s else PAL["red"] if "↓" in s else PAL["sub"]
        d.box(x, y, 200, 36, "", fill="#ffffff"); d.text(x + 100, y + 18, s, size=14, weight=700, color=col)
d.save(P("cpas13-dielectric"))

# ---------- CPAS-07 quadrants ----------
d = Diagram(640, 380, title="ΔG = ΔH − TΔS: when is a reaction spontaneous?")
cx, cy, w, h = 330, 205, 270, 140
quads = [(-1, -1, "ΔH > 0, ΔS < 0", "NEVER spontaneous\n(ΔG always > 0)", "redL", "red"),
         (1, -1, "ΔH > 0, ΔS > 0", "Spontaneous at HIGH T\n(entropy wins when hot)", "amberL", "amber"),
         (-1, 1, "ΔH < 0, ΔS < 0", "Spontaneous at LOW T\n(enthalpy wins when cold)", "blueL", "blue"),
         (1, 1, "ΔH < 0, ΔS > 0", "ALWAYS spontaneous\n(ΔG always < 0)", "greenL", "green")]
for sx, sy, a, b, fl, st in quads:
    x = cx if sx > 0 else cx - w; y = cy if sy > 0 else cy - h
    d.box(x + 3, y + 3, w - 6, h - 6, "", fill=fl, stroke=st)
    d.text(x + w / 2, y + 38, a, size=15, weight=700); d.text(x + w / 2, y + 88, b, size=14, color=PAL[st] if st != "amber" else "#9a6200", weight=700)
d.arrow((cx - w - 10, cy), (cx + w + 25, cy), color="sub"); d.text(cx + w + 30, cy - 14, "ΔS", size=14, weight=700, anchor="end")
d.arrow((cx, cy + h + 10), (cx, cy - h - 18), color="sub"); d.text(cx + 12, cy - h - 14, "ΔH", size=14, weight=700, anchor="start")
d.save(P("cpas07-quadrants"))

# ---------- CPAS-10 galvanic cell ----------
d = Diagram(720, 385)
for bx, fill, ion, metal, role, sign, rxn in [(70, "#e7eef8", "Zn²⁺", "Zn", "ANODE (−): oxidation", "−", "Zn → Zn²⁺ + 2e⁻"),
                                             (430, "#e0f0f6", "Cu²⁺", "Cu", "CATHODE (+): reduction", "+", "Cu²⁺ + 2e⁻ → Cu")]:
    d.raw(f'<path d="M{bx},150 L{bx},300 Q{bx},315 {bx + 15},315 L{bx + 205},315 Q{bx + 220},315 {bx + 220},300 L{bx + 220},150" fill="none" stroke="{PAL["ink"]}" stroke-width="2"/>')
    d.raw(f'<rect x="{bx + 2}" y="190" width="216" height="123" fill="{fill}"/>')
    d.box(bx + 90, 110, 40, 170, metal, fill="#c9ced8" if metal == "Zn" else "#e3a676", stroke="ink", weight=700)
    d.text(bx + 110, 338, role, size=13, weight=700, color=PAL["red"] if sign == "+" else PAL["blue"])
    d.text(bx + 110, 300, rxn, size=12.5); d.text(bx + 45, 230, ion, size=14, weight=700)
d.line([(180, 110), (180, 60), (540, 60), (540, 110)], width=2); d.circle(360, 60, 22, "1.10 V", fill="#fff", stroke="ink", size=12)
d.arrow((215, 45), (320, 45), color="amber", width=2.4); d.text(267, 32, "e⁻ flow", size=13, color="#9a6200", weight=700)
d.arrow((400, 45), (505, 45), color="amber", width=2.4)
d.raw(f'<path d="M265,250 L265,140 L455,140 L455,250" fill="none" stroke="{PAL["sub"]}" stroke-width="18" stroke-linejoin="round" opacity=".35"/>')
d.text(360, 128, "salt bridge (KNO₃)", size=12.5, color=PAL["sub"])
d.arrow((330, 160), (290, 160), color="blue"); d.text(345, 172, "NO₃⁻ → anode", size=11.5, color=PAL["blue"], anchor="start")
d.arrow((390, 196), (430, 196), color="red"); d.text(375, 210, "K⁺ → cathode", size=11.5, color=PAL["red"], anchor="end")
d.text(360, 372, "E°cell = E°cathode − E°anode = 0.34 − (−0.76) = +1.10 V", size=12.5, color=PAL["sub"])
d.save(P("cpas10-galvanic"))

# ---------- BBFL-05 Hardy-Weinberg square ----------
d = Diagram(520, 380, title="Example: p = 0.7, q = 0.3")
x0, y0, S, p = 140, 80, 280, 0.7; a = S * p
cells = [(x0, y0, a, a, "AA = p²\n0.49", "blueL"), (x0 + a, y0, S - a, a, "Aa = pq\n0.21", "purpleL"),
         (x0, y0 + a, a, S - a, "Aa = pq\n0.21", "purpleL"), (x0 + a, y0 + a, S - a, S - a, "aa\nq² = 0.09", "redL")]
for x, y, w, h, s, fl in cells: d.box(x, y, w, h, s, fill=fl, stroke="ink", r=0, size=14, weight=700)
d.text(x0 + a / 2, y0 - 14, "A (p = 0.7)", size=13, weight=700); d.text(x0 + a + (S - a) / 2, y0 - 14, "a (q = 0.3)", size=13, weight=700)
d.text(x0 - 10, y0 + a / 2, "A (p)", size=13, weight=700, anchor="end"); d.text(x0 - 10, y0 + a + (S - a) / 2, "a (q)", size=13, weight=700, anchor="end")
d.text(260, 372, "Carriers = 2pq = 0.42   ·   Affected = q² = 0.09   ·   Total = 1", size=12.5, color=PAL["sub"])
d.save(P("bbfl05-hw"))

# ---------- BBFL-08 replication fork ----------
d = Diagram(740, 330)
fx = 480
d.line([(fx, 150), (720, 150)], width=3, color="ink"); d.line([(fx, 172), (720, 172)], width=3, color="ink")
d.line([(40, 70), (400, 70), (fx, 150)], width=3, color="ink"); d.line([(40, 252), (400, 252), (fx, 172)], width=3, color="ink")
d.text(30, 70, "3′", size=13, weight=700, anchor="end"); d.text(728, 150, "5′", size=13, weight=700, anchor="start")
d.text(30, 252, "5′", size=13, weight=700, anchor="end"); d.text(728, 172, "3′", size=13, weight=700, anchor="start")
d.text(110, 52, "parental (template) strand", size=12, color=PAL["sub"]); d.text(110, 272, "parental (template) strand", size=12, color=PAL["sub"])
# leading strand
d.line([(50, 92), (70, 92)], width=5, color="red"); d.arrow((70, 92), (380, 92), color="blue", width=3)
d.text(30, 92, "5′", size=12, color=PAL["blue"], anchor="end"); d.text(215, 110, "LEADING strand: continuous, toward the fork", size=12.5, color=PAL["blue"], weight=700)
d.box(382, 80, 54, 24, "Pol III", fill="blueL", stroke="blue", size=11, weight=700)
# lagging strand fragments (synthesized right → left)
for xs, xe in [(395, 330), (310, 190), (170, 55)]:
    if xs == 395: d.line([(xs, 230), (xs + 22, 230)], width=5, color="red"); d.text(xs + 11, 246, "primer", size=10.5, color=PAL["red"]); continue
    d.line([(xs, 230), (xs + 20, 230)], width=5, color="red"); d.arrow((xs, 230), (xe, 230), color="green", width=3)
d.text(250, 212, "LAGGING strand: Okazaki fragments, away from the fork", size=12.5, color=PAL["green"], weight=700)
d.text(180, 244, "ligase", size=11, color=PAL["purple"], weight=700)
d.circle(fx + 8, 161, 20, "", fill="amberL", stroke="amber"); d.text(fx + 8, 196, "helicase", size=12, weight=700, color="#9a6200")
for x in (440, 458): d.circle(x, 228, 6, "", fill="purpleL", stroke="purple")
d.text(470, 220, "SSB", size=11, color=PAL["purple"], anchor="start")
d.box(590, 128, 100, 22, "topoisomerase", fill="tealL", stroke="teal", size=11, weight=700)
d.arrow((600, 105), (690, 105), color="ink"); d.text(645, 92, "fork moves", size=12, weight=700)
d.text(370, 316, "Red = RNA primer (made by primase). New DNA always grows 5′ → 3′.", size=12, color=PAL["sub"])
d.save(P("bbfl08-fork"))

# ---------- BBFL-09 counts ----------
d = Diagram(720, 260, title="One human cell: chromosomes vs chromatids")
cols = ["G1", "after S phase", "each cell after\nmitosis", "each cell after\nmeiosis I", "each cell after\nmeiosis II"]
vals = [("chromosomes", ["46", "46", "46", "23", "23"]), ("chromatids", ["46", "92", "46", "46", "23"]), ("ploidy", ["2n", "2n", "2n", "n", "n"])]
for j, c in enumerate(cols): d.box(140 + j * 115, 44, 110, 50, c, fill="blueL", stroke="blue", size=12, weight=700)
for i, (lab, vs) in enumerate(vals):
    y = 100 + i * 46; d.box(20, y, 115, 40, lab, fill="grayL", size=13, weight=700)
    for j, v in enumerate(vs):
        hl = (lab == "chromatids" and j == 1) or (lab == "ploidy" and j == 3)
        d.box(140 + j * 115, y, 110, 40, v, fill="amberL" if hl else "#ffffff", stroke="line", size=16, weight=700)
d.save(P("bbfl09-ploidy"))

# ---------- BBFL-10 MHC ----------
d = Diagram(740, 330)
for x0, cell, mhc, pep, t, tfill, act, col in [
        (20, "Any nucleated cell\n(e.g., virus-infected)", "MHC I", "peptide from INSIDE\nthe cell", "CD8⁺ cytotoxic T cell", "redL", "kills the cell", "red"),
        (385, "Antigen-presenting cell\n(dendritic, macrophage, B cell)", "MHC II", "peptide from OUTSIDE\n(engulfed microbe)", "CD4⁺ helper T cell", "blueL", "activates B cells,\nmacrophages, CD8 cells", "blue")]:
    d.box(x0, 40, 335, 70, cell, fill="grayL", size=14, weight=700)
    d.box(x0 + 100, 125, 135, 36, mhc, fill="amberL", stroke="amber", size=14, weight=700)
    d.text(x0 + 167, 178, pep, size=12, color=PAL["sub"])
    d.arrow((x0 + 167, 198), (x0 + 167, 222), color="ink")
    d.box(x0 + 60, 226, 215, 40, t, fill=tfill, stroke=col, size=14, weight=700)
    d.text(x0 + 167, 290, act, size=12.5, color=PAL[col], weight=700)
d.text(370, 322, "Rule of 8:  MHC I × CD8 = 8,   MHC II × CD4 = 8", size=13, weight=700)
d.save(P("bbfl10-mhc"))

# ---------- OChem-01 pKa ladder ----------
d = Diagram(740, 250, title="Approximate pKa values (lower = stronger acid)")
x0, x1, lo, hi = 40, 710, -10, 50; X = lambda v: x0 + (v - lo) / (hi - lo) * (x1 - x0); y = 125
d.line([(x0, y), (x1, y)], width=2)
for v in range(-10, 51, 10): d.line([(X(v), y - 5), (X(v), y + 5)], width=1.5); d.text(X(v), y + 18, str(v), size=11, color=PAL["sub"])
marks = [(-7, "HCl", -30), (4.8, "carboxylic acid", 40), (10, "phenol", -30), (15.7, "water", 40), (17, "alcohol", -55), (20, "ketone α-H", 65),
         (25, "terminal alkyne", -30), (38, "amine N–H", 40), (44, "alkene C–H", -30), (50, "alkane C–H", 65)]
for v, lab, off in marks:
    yy = y + off
    d.line([(X(v), y), (X(v), yy + (8 if off < 0 else -10))], color="line", width=1.2); d.circle(X(v), y, 4, fill="blue", stroke="blue")
    d.text(min(X(v), 660), yy, f"{lab} ≈ {v:g}", size=11.5, weight=600)
d.arrow((300, 236), (120, 236), color="red"); d.text(310, 236, "more acidic", size=12, color=PAL["red"], anchor="start", weight=700)
d.save(P("ochem01-pka"))

# ---------- OChem-02 SN2 ----------
d = Diagram(740, 240)
def center(x, y, groups, left=None, right=None):
    d.text(x, y, "C", size=20, weight=700)
    for gx, gy, g in groups: d.line([(x + (gx - x) * 0.25, y + (gy - y) * 0.25), (x + (gx - x) * 0.75, y + (gy - y) * 0.75)], width=2); d.text(gx, gy, g, size=14)
d.text(40, 120, "Nu⁻", size=18, weight=700, color=PAL["blue"])
d.arrow((62, 104), (128, 112), color="blue", curve=-18)
center(150, 120, [(118, 72, "R¹"), (118, 168, "R²"), (100, 128, "R³")]); d.line([(162, 120), (205, 120)], width=2); d.text(225, 120, "Br", size=18, weight=700, color=PAL["red"])
d.arrow((262, 120), (300, 120))
d.text(318, 120, "[", size=60, color=PAL["sub"]); d.text(345, 120, "Nu", size=16, weight=700, color=PAL["blue"])
d.line([(362, 120), (392, 120)], width=2, dash=True); center(410, 120, [(410, 66, "R¹"), (410, 174, "R²"), (440, 150, "R³")])
d.line([(428, 120), (458, 120)], width=2, dash=True); d.text(474, 120, "Br", size=16, weight=700, color=PAL["red"]); d.text(500, 120, "]‡", size=60, color=PAL["sub"])
d.text(410, 214, "transition state: 5 groups, R's flat", size=12, color=PAL["sub"])
d.arrow((530, 120), (566, 120))
d.text(588, 120, "Nu", size=18, weight=700, color=PAL["blue"]); d.line([(606, 120), (640, 120)], width=2)
center(652, 120, [(688, 72, "R¹"), (688, 168, "R²"), (706, 128, "R³")])
d.text(640, 214, "inverted + Br⁻ leaves", size=12, color=PAL["sub"])
d.text(150, 214, "backside attack, opposite Br", size=12, color=PAL["sub"])
d.save(P("ochem02-sn2"))

# ---------- OChem-03 Zaitsev vs Hofmann ----------
d = Diagram(740, 300)
d.embed(mol("CC(Br)CC", 200, 150), 10, 70, 200, 150); d.text(110, 236, "2-bromobutane", size=13, weight=700)
d.arrow((215, 120), (370, 75), label="EtO⁻ (small base)", lsize=12.5, loff=(-10, -14))
d.arrow((215, 170), (370, 225), label="t-BuO⁻ (bulky base)", lsize=12.5, loff=(-10, 16))
d.embed(mol("C/C=C/C", 180, 110), 380, 15, 180, 110); d.text(575, 55, "2-butene (major)\nZaitsev: MORE\nsubstituted", size=12.5, weight=700, anchor="start", color=PAL["green"])
d.embed(mol("C=CCC", 180, 110), 380, 170, 180, 110); d.text(575, 220, "1-butene (major)\nHofmann: LESS\nsubstituted", size=12.5, weight=700, anchor="start", color=PAL["amber"])
d.save(P("ochem03-zaitsev"))

# ---------- OChem-04 Fischer ----------
d = Diagram(620, 290)
for cx, left, right, lab, col in [(160, "H", "OH", "D-glyceraldehyde = (R)\nOH on the RIGHT", "blue"), (460, "HO", "H", "L-glyceraldehyde = (S)\nOH on the LEFT", "red")]:
    cy = 130
    d.line([(cx, cy - 55), (cx, cy + 55)], width=2.4); d.line([(cx - 60, cy), (cx + 60, cy)], width=2.4)
    d.text(cx, cy - 72, "CHO", size=16, weight=700); d.text(cx, cy + 74, "CH₂OH", size=16, weight=700)
    d.text(cx - 80, cy, left, size=16, weight=700, color=PAL[col] if left == "HO" else PAL["ink"]); d.text(cx + 80, cy, right, size=16, weight=700, color=PAL[col] if right == "OH" else PAL["ink"])
    d.text(cx, 255, lab, size=13, weight=700, color=PAL[col])
d.text(310, 18, "Fischer projection: horizontal bonds point toward you, vertical bonds point away", size=12, color=PAL["sub"])
d.save(P("ochem04-fischer"))

# ---------- OChem-05 IR + NMR rulers ----------
d = Diagram(740, 400)
def ruler(y0, a, b, ticks, title, unit, bars):
    x0, x1 = 40, 710; X = lambda v: x0 + (a - v) / (a - b) * (x1 - x0)
    d.text(x0, y0 - 20, title, size=14, weight=700, anchor="start")
    d.line([(x0, y0), (x1, y0)], width=2)
    for t in ticks: d.line([(X(t), y0 - 4), (X(t), y0 + 4)], width=1.4); d.text(X(t), y0 + 16, str(t), size=11, color=PAL["sub"])
    d.text(x1, y0 - 20, unit, size=11, color=PAL["sub"], anchor="end")
    for k, (lo, hi, lab, col) in enumerate(bars):
        yy = y0 + 42 + (k % 3) * 24; xa, xb = X(hi), X(lo)
        d.raw(f'<rect x="{xa:.1f}" y="{yy - 9}" width="{max(xb - xa, 4):.1f}" height="18" rx="4" fill="{PAL[col + "L"]}" stroke="{PAL[col]}"/>')
        d.text(xb + 6, yy, lab, size=11.5, weight=600, anchor="start")
ruler(40, 4000, 1000, [4000, 3500, 3000, 2500, 2000, 1500, 1000], "IR key bands", "wavenumber (cm⁻¹)",
      [(3200, 3600, "O–H alcohol (broad)", "blue"), (2500, 3300, "O–H acid (very broad)", "purple"), (3300, 3500, "N–H (sharp)", "teal"),
       (2100, 2260, "C≡C, C≡N", "amber"), (1650, 1750, "C=O (strong, sharp)", "red")])
ruler(230, 13, 0, list(range(13, -1, -1)), "¹H NMR chemical shifts", "δ (ppm), left = deshielded (downfield)",
      [(10, 13, "COOH", "purple"), (9, 10, "aldehyde", "red"), (6.5, 8, "aromatic", "amber"), (4.5, 6.5, "alkene", "teal"),
       (3, 4, "H–C–O / H–C–X", "blue"), (2, 2.5, "H–C–C=O", "green"), (0.9, 1.5, "alkyl", "purple")])
d.save(P("ochem05-spec"))

# ---------- OChem-06 acid derivatives ----------
d = Diagram(740, 250)
for k, (smi, lab) in enumerate([("CC(=O)Cl", "acid chloride"), ("CC(=O)OC(C)=O", "anhydride"), ("CC(=O)OCC", "ester"), ("CC(N)=O", "amide")]):
    d.embed(mol(smi, 170, 130), 15 + k * 180, 20, 170, 130); d.text(100 + k * 180, 165, lab, size=14, weight=700)
d.raw(f'<defs><linearGradient id="gr" x1="0" x2="1"><stop offset="0" stop-color="{PAL["red"]}"/><stop offset="1" stop-color="{PAL["blue"]}"/></linearGradient></defs>')
d.raw('<rect x="40" y="190" width="650" height="12" rx="6" fill="url(#gr)"/>')
d.text(40, 222, "most reactive (best leaving group)", size=12.5, weight=700, anchor="start", color=PAL["red"])
d.text(700, 222, "least reactive (N lone pair donates)", size=12.5, weight=700, anchor="end", color=PAL["blue"])
d.save(P("ochem06-derivatives"))

# ---------- Lab-01 blots ----------
d = Diagram(660, 230, title="SNoW DRoP")
for k, (blot, tgt, probe, col) in enumerate([("Southern", "DNA", "DNA probe", "blue"), ("Northern", "RNA", "nucleic-acid probe", "green"), ("Western", "Protein", "antibody", "red")]):
    x = 20 + k * 215
    d.box(x, 44, 200, 44, blot, fill=col + "L", stroke=col, size=16, weight=700)
    d.box(x, 96, 200, 50, "detects: " + tgt, fill="#ffffff", stroke="line", size=15, weight=700)
    d.box(x, 154, 200, 50, "probe: " + probe, fill="grayL", stroke="line", size=13)
d.save(P("lab01-blots"))

# ---------- Lab-02 gel ----------
import math as _m
d = Diagram(560, 380)
gx, gy, gw, gh = 120, 50, 330, 290
d.box(gx, gy, gw, gh, "", fill="#eef2f7", stroke="ink", r=6)
d.box(gx, 14, gw, 26, "− cathode (black lead): load wells here", fill="#334155", stroke="#334155", size=12.5, weight=700, color="#ffffff")
d.box(gx, 346, gw, 26, "+ anode (red lead): DNA runs this way", fill=PAL["red"], stroke=PAL["red"], size=12.5, weight=700, color="#ffffff")
Y = lambda bp: gy + 20 + (_m.log10(5000) - _m.log10(bp)) / (_m.log10(5000) - _m.log10(80)) * (gh - 40)
lanes = [("ladder", [3000, 2000, 1000, 500, 250, 100]), ("A", [2000, 400]), ("B", [1200]), ("C", [3000, 600, 150])]
for k, (lab, bands) in enumerate(lanes):
    lx = gx + 25 + k * 78; d.raw(f'<rect x="{lx}" y="{gy + 6}" width="56" height="8" fill="#94a3b8"/>')
    for bp in bands:
        d.raw(f'<rect x="{lx}" y="{Y(bp) - 3:.1f}" width="56" height="6" rx="2" fill="{PAL["blue"]}"/>')
        if k == 0: d.text(gx - 8, Y(bp), f"{bp} bp", size=11, anchor="end", color=PAL["sub"])
for k, (lab, _) in enumerate(lanes): d.text(gx + 53 + k * 78, gy + gh - 10, lab, size=12, weight=700)
d.arrow((490, 80), (490, 310), color="red", width=2.5); d.text(500, 120, "large:\nslow", size=12, anchor="start"); d.text(500, 280, "small:\nfast, far", size=12, anchor="start")
d.save(P("lab02-gel"))

# ---------- Lab-03 TLC ----------
d = Diagram(560, 380)
px, py, pw, ph = 150, 30, 170, 320; base, front = 310, 70
d.box(px, py, pw, ph, "", fill="#f8fafc", stroke="ink", r=4)
d.line([(px, base), (px + pw, base)], color="sub", width=1.5, dash=True); d.text(px + pw + 8, base, "baseline (spotted here)", size=12, anchor="start", color=PAL["sub"])
d.line([(px, front), (px + pw, front)], color="blue", width=1.5, dash=True); d.text(px + pw + 8, front, "solvent front", size=12, anchor="start", color=PAL["blue"])
sx = px + pw / 2; ya, yb = 130, 250
d.raw(f'<ellipse cx="{sx}" cy="{ya}" rx="14" ry="9" fill="{PAL["amber"]}"/><ellipse cx="{sx}" cy="{yb}" rx="14" ry="9" fill="{PAL["purple"]}"/>')
d.text(px + pw + 8, ya, f"less polar: Rf = {(base - ya) / (base - front):.2f}", size=13, anchor="start", weight=700, color="#9a6200")
d.text(px + pw + 8, yb, f"more polar: Rf = {(base - yb) / (base - front):.2f}", size=13, anchor="start", weight=700, color=PAL["purple"])
d.arrow((px - 50, base), (px - 50, ya), both=True, color="amber"); d.text(px - 58, (base + ya) / 2, "spot\ndistance", size=11, anchor="end")
d.arrow((px - 15, base), (px - 15, front), both=True, color="blue"); d.text(px - 58, front + 20, "solvent\ndistance", size=11, anchor="end")
d.text(280, 368, "Silica plate (polar): polar compounds stick and travel less", size=12, color=PAL["sub"])
d.save(P("lab03-tlc"))

# ---------- BBFL-06 amino acids (RDKit, pH 7.4) ----------
from rdkit import Chem
T = "[NH3+][C@@H]({})C(=O)[O-]"
groups = [
 ("Nonpolar, aliphatic", [("Gly (G)", "[NH3+]CC(=O)[O-]"), ("Ala (A)", T.format("C")), ("Val (V)", T.format("C(C)C")), ("Leu (L)", T.format("CC(C)C")),
                          ("Ile (I)", T.format("[C@@H](C)CC")), ("Met (M)", T.format("CCSC")), ("Pro (P)", "[O-]C(=O)[C@@H]1CCC[NH2+]1")], "line"),
 ("Aromatic (F, W nonpolar; Y polar)", [("Phe (F)", T.format("Cc1ccccc1")), ("Trp (W)", T.format("Cc1c[nH]c2ccccc12")), ("Tyr (Y)", T.format("Cc1ccc(O)cc1"))], "amber"),
 ("Polar, uncharged", [("Ser (S)", T.format("CO")), ("Thr (T)", T.format("[C@@H](C)O")), ("Cys (C)", T.format("CS")), ("Asn (N)", T.format("CC(N)=O")), ("Gln (Q)", T.format("CCC(N)=O"))], "green"),
 ("Acidic (−) and basic (+) at pH 7.4", [("Asp (D) -", T.format("CC(=O)[O-]")), ("Glu (E) -", T.format("CCC(=O)[O-]")), ("Lys (K) +", T.format("CCCC[NH3+]")),
                                         ("Arg (R) +", T.format("CCCNC(N)=[NH2+]")), ("His (H) ~0", T.format("Cc1c[nH]cn1"))], "purple"),
]
# check stereo: all L. Expect (S) except Cys (R); Ile CB (S); Thr CB (R).
from rdkit.Chem import FindMolChiralCenters
for _, aas, _ in groups:
    for name, s in aas:
        m = Chem.MolFromSmiles(s); cc = FindMolChiralCenters(m, includeUnassigned=True, useLegacyImplementation=False)
        print(f"  {name:12s} {cc}")
cw, ch = 118, 112
d = Diagram(7 * cw + 20, sum(34 + ch for _ in groups) + 10)
y = 6
for title, aas, col in groups:
    d.text(12, y + 16, title, size=15, weight=700, anchor="start", color=PAL.get(col, PAL["ink"]) if col != "line" else PAL["ink"])
    y += 30
    for k, (name, s) in enumerate(aas):
        d.embed(mol(s, 170, 150), 10 + k * cw, y, cw, ch - 18); d.text(10 + k * cw + cw / 2, y + ch - 10, name.replace(" -", " (−)").replace(" +", " (+)").replace(" ~0", " (mostly 0)"), size=12, weight=700)
    y += ch + 4
d.save(P("bbfl06-aa"))
