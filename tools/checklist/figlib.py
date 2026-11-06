"""520 Quest figure helpers. Every figure is drawn from code (no generative AI), so it is exact and reproducible.
Usage inside a figure script:  import sys; sys.path.insert(0, "/mnt/project-files/520-quest-bank-src/fig"); from figlib import *
Outputs go to /mnt/project-files/520-quest-bank-src/figout/<cat>/<name>.svg  (use out(cat, name)).
"""
import os, re, html, math
ROOT = "/mnt/project-files/520-quest-bank-src"
PAL = dict(ink="#1f2430", sub="#5b6474", line="#8a93a3", bg="#ffffff",
           blue="#2f6fdb", red="#d6453d", green="#1f9d63", amber="#d98a00", purple="#7a4cd9", teal="#138f9a", pink="#d23c8a",
           blueL="#e6eefc", redL="#fbe7e5", greenL="#e3f5ec", amberL="#fdf1db", purpleL="#efe8fc", tealL="#e0f3f4", grayL="#f1f3f6")
FONT = "system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif"

def out(cat, name):
    d = os.path.join(ROOT, "figout", cat); os.makedirs(d, exist_ok=True)
    return os.path.join(d, name + ".svg")

def _clean(svg):
    svg = re.sub(r"<\?xml[^>]*\?>\s*", "", svg); svg = re.sub(r"<!DOCTYPE[^>]*>\s*", "", svg)
    svg = re.sub(r"<!--.*?-->", "", svg, flags=re.S); svg = re.sub(r"<metadata>.*?</metadata>", "", svg, flags=re.S)
    return svg.strip() + "\n"

# ---------- Free-form diagrams (flowcharts, pathways, labelled schematics) ----------
class Diagram:
    """Coordinate-based SVG canvas. Units are px in a viewBox of width w, height h."""
    def __init__(self, w=640, h=360, title=None):
        self.w, self.h, self.el = w, h, []
        self.defs = ('<marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
                     f'<path d="M0,0 L10,5 L0,10 z" fill="{PAL["ink"]}"/></marker>')
        if title: self.text(w / 2, 24, title, size=17, weight=700)
    def raw(self, s): self.el.append(s); return self
    def text(self, x, y, s, size=14, color=None, weight=400, anchor="middle", italic=False):
        lines = s.split("\n"); lh = size * 1.25; y0 = y - (len(lines) - 1) * lh / 2
        for i, ln in enumerate(lines):
            self.el.append(f'<text x="{x:.1f}" y="{y0 + i * lh:.1f}" font-size="{size}" font-weight="{weight}" fill="{color or PAL["ink"]}" '
                           f'text-anchor="{anchor}" dominant-baseline="middle"{" font-style=\"italic\"" if italic else ""}>{html.escape(ln)}</text>')
        return self
    def box(self, x, y, w, h, s="", fill="grayL", stroke="line", size=14, weight=500, r=10, color=None):
        """Box with top-left (x, y). Text centered; use \\n for line breaks. Returns centre/edge anchors."""
        self.el.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{PAL.get(fill, fill)}" stroke="{PAL.get(stroke, stroke)}" stroke-width="1.5"/>')
        if s: self.text(x + w / 2, y + h / 2, s, size=size, weight=weight, color=color)
        return dict(c=(x + w / 2, y + h / 2), t=(x + w / 2, y), b=(x + w / 2, y + h), l=(x, y + h / 2), r=(x + w, y + h / 2))
    def circle(self, cx, cy, r, s="", fill="grayL", stroke="line", size=14):
        self.el.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{PAL.get(fill, fill)}" stroke="{PAL.get(stroke, stroke)}" stroke-width="1.5"/>')
        if s: self.text(cx, cy, s, size=size)
        return self
    def arrow(self, p1, p2, label=None, color="ink", dash=False, both=False, curve=0, lsize=12, loff=(0, -10), width=1.8):
        (x1, y1), (x2, y2) = p1, p2; c = PAL.get(color, color)
        if curve:
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2; dx, dy = x2 - x1, y2 - y1; L = math.hypot(dx, dy) or 1
            qx, qy = mx - dy / L * curve, my + dx / L * curve; d = f"M{x1},{y1} Q{qx:.1f},{qy:.1f} {x2},{y2}"; lx, ly = qx, qy
        else: d = f"M{x1},{y1} L{x2},{y2}"; lx, ly = (x1 + x2) / 2, (y1 + y2) / 2
        mk = f' marker-end="url(#ah)"' + (' marker-start="url(#ah)"' if both else "")
        self.el.append(f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{width}"{" stroke-dasharray=\"6 4\"" if dash else ""}{mk}/>')
        if label: self.text(lx + loff[0], ly + loff[1], label, size=lsize, color=PAL["sub"])
        return self
    def line(self, pts, color="ink", width=1.8, dash=False, fill="none"):
        self.el.append(f'<polyline points="{" ".join(f"{x},{y}" for x, y in pts)}" fill="{PAL.get(fill, fill)}" stroke="{PAL.get(color, color)}" stroke-width="{width}"{" stroke-dasharray=\"6 4\"" if dash else ""}/>')
        return self
    def tag(self, x, y, label, ok=None, size=12):
        """Pill label for pointing at part of a figure, e.g. tag(x, y, "pI = 3.2", ok=True). Never use answer letters
        (A-D): choice order can be shuffled in the app. ok=True green check, False red cross, None gray."""
        f = PAL["green"] if ok else PAL["red"] if ok is False else PAL["sub"]
        s = ("✓ " if ok else "✗ " if ok is False else "") + label; w = 0.62 * size * len(s) + 16
        self.el.append(f'<rect x="{x - w / 2:.1f}" y="{y - size}" width="{w:.1f}" height="{2 * size}" rx="{size}" fill="{f}"/>')
        self.text(x, y + 0.5, s, size=size, weight=700, color="#fff"); return self
    def embed(self, svg, x, y, w, h):
        """Place another SVG (e.g. from mol() or mols()) inside this diagram at (x, y) scaled to w x h."""
        svg = _clean(svg); svg = re.sub(r"\s(width|height)='[^']*'", "", svg, count=2); svg = re.sub(r'\s(width|height)="[^"]*"', "", svg, count=2)
        self.el.append(svg.replace("<svg", f'<svg x="{x}" y="{y}" width="{w}" height="{h}"', 1)); return self
    def svg(self):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" font-family="{FONT}">'
                f'<defs>{self.defs}</defs><rect width="100%" height="100%" rx="14" fill="{PAL["bg"]}"/>' + "".join(self.el) + "</svg>\n")
    def save(self, path):
        open(path, "w").write(self.svg()); print("wrote", path)

# ---------- Exact chemical structures (RDKit from SMILES) ----------
def mols(smiles, legends=None, per_row=4, cell=(200, 170), path=None, highlight=None, title=None):
    """Grid of structures drawn by RDKit from SMILES (exact connectivity, charges, stereo).
    highlight: list (per molecule) of SMARTS strings to highlight, or None."""
    from rdkit import Chem
    from rdkit.Chem import Draw
    from rdkit.Chem.Draw import rdMolDraw2D
    ms = [Chem.MolFromSmiles(s) for s in smiles]
    assert all(ms), "bad SMILES: " + str([s for s, m in zip(smiles, ms) if m is None])
    for m in ms: _orient(m)
    assert not any(ord(ch) > 127 for ch in "".join(legends or [])), "RDKit legends must be ASCII (its font lacks −, ₂ etc.); put rich labels in a Diagram instead"
    hl = None
    if highlight:
        hl = [list(m.GetSubstructMatch(Chem.MolFromSmarts(h))) if h else [] for m, h in zip(ms, highlight)]
    n = len(ms); cols = min(per_row, n); rows = math.ceil(n / cols)
    d = rdMolDraw2D.MolDraw2DSVG(cols * cell[0], rows * cell[1] + (34 if title else 0), cell[0], cell[1])
    o = d.drawOptions(); o.legendFontSize = 16; o.addStereoAnnotation = True; o.bondLineWidth = 2
    o.setHighlightColour((1.0, 0.85, 0.4)); o.clearBackground = True
    if title: d.SetOffset(0, 0)
    d.DrawMolecules(ms, legends=legends or [""] * n, highlightAtoms=hl)
    d.FinishDrawing(); s = _clean(d.GetDrawingText())
    s = s.replace("<svg ", f'<svg font-family="{FONT}" ', 1)
    s = re.sub(r"(<rect style='opacity:1\.0;fill:#FFFFFF)", r"\1", s)
    if path: open(path, "w").write(s); print("wrote", path)
    return s

def _orient(m):
    """2D layout rotated so the first atom written in the SMILES sits on the left and the last on the right
    (so a peptide reads N-terminus to C-terminus). Wedges are recomputed from the chiral tags, so stereo stays correct."""
    from rdkit.Chem import rdDepictor
    from rdkit.Geometry import Point3D
    rdDepictor.SetPreferCoordGen(True); rdDepictor.Compute2DCoords(m); c = m.GetConformer(); n = m.GetNumAtoms()
    if n < 2: return m
    a, b = c.GetAtomPosition(0), c.GetAtomPosition(n - 1); t = -math.atan2(b.y - a.y, b.x - a.x); ct, st = math.cos(t), math.sin(t)
    for i in range(n):
        p = c.GetAtomPosition(i); c.SetAtomPosition(i, Point3D(p.x * ct - p.y * st, p.x * st + p.y * ct, 0))
    return m

def mol(smiles, w=220, h=170, highlight=None, legend=""):
    """One structure as an SVG string (for Diagram.embed). highlight: SMARTS to shade. Legends: ASCII only (RDKit font)."""
    from rdkit import Chem
    from rdkit.Chem.Draw import rdMolDraw2D
    m = Chem.MolFromSmiles(smiles); assert m, "bad SMILES " + smiles; _orient(m)
    d = rdMolDraw2D.MolDraw2DSVG(w, h); o = d.drawOptions(); o.bondLineWidth = 2; o.clearBackground = False; o.addStereoAnnotation = True
    o.setHighlightColour((1.0, 0.85, 0.4)); o.legendFontSize = 15
    atoms = list(m.GetSubstructMatch(Chem.MolFromSmarts(highlight))) if highlight else []
    d.DrawMolecule(m, highlightAtoms=atoms, legend=legend); d.FinishDrawing(); return _clean(d.GetDrawingText())

# ---------- Data plots computed from the real equations (matplotlib) ----------
def plot(w=6.4, h=3.6):
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    plt.rcParams.update({"svg.fonttype": "none", "font.family": "sans-serif", "font.size": 11, "axes.spines.top": False,
                         "axes.spines.right": False, "axes.edgecolor": PAL["sub"], "axes.labelcolor": PAL["ink"],
                         "xtick.color": PAL["sub"], "ytick.color": PAL["sub"], "axes.titleweight": "bold", "axes.titlesize": 13,
                         "legend.frameon": False})
    fig, ax = plt.subplots(figsize=(w, h), dpi=100); return fig, ax

def saveplot(fig, path):
    import io; fig.tight_layout(); b = io.StringIO(); fig.savefig(b, format="svg", facecolor="white")
    s = _clean(b.getvalue()); s = re.sub(r'width="[\d.]+pt" height="[\d.]+pt"', "", s, count=1)
    s = s.replace("font-family:sans-serif", "font-family:" + FONT.replace(",", ", "))
    open(path, "w").write(s); print("wrote", path)
