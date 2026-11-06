"""Checklist figures computed from the real equations (matplotlib). Run from repo root: python3 tools/checklist/figs_plots.py
Needs: pip install matplotlib numpy"""
import os, sys, math
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from figlib import plot, saveplot, PAL
OUT = os.path.join(os.path.dirname(os.path.dirname(HERE)), "play/fig/chk"); os.makedirs(OUT, exist_ok=True)
P = lambda n: os.path.join(OUT, n + ".svg")
import matplotlib.pyplot as plt

def mm(S, Vm, Km): return Vm * S / (Km + S)

# CPAS-01 ball thrown up at 20 m/s, g = 10
fig, ax = plot(6.4, 3.4)
t = np.linspace(0, 4, 200); h = 20 * t - 5 * t ** 2
ax.plot(t, h, color=PAL["blue"], lw=2.5)
ax.plot([2], [20], "o", color=PAL["red"]); ax.axvline(2, color=PAL["line"], ls=":", lw=1); ax.axhline(20, color=PAL["line"], ls=":", lw=1)
ax.annotate("Peak: v = 0, but a = −10 m/s² still\nt_peak = v₀/g = 2 s,  h_max = v₀²/2g = 20 m", xy=(2, 20), xytext=(2.15, 25.5),
            arrowprops=dict(arrowstyle="->", color=PAL["ink"]), fontsize=10)
ax.text(0.55, 3, "going up:\nslowing down", fontsize=9, color=PAL["sub"]); ax.text(3.05, 3, "coming down:\nspeeding up", fontsize=9, color=PAL["sub"])
ax.set_xlabel("time t (s)"); ax.set_ylabel("height (m)"); ax.set_xlim(0, 4.1); ax.set_ylim(0, 30); ax.set_yticks([0, 5, 10, 15, 20])
saveplot(fig, P("cpas01-ball"))

# CPAS-04 field lines and equipotentials for +q at (-1,0) and -q at (1,0)
fig, ax = plot(6.0, 4.0)
x, y = np.meshgrid(np.linspace(-3, 3, 300), np.linspace(-2, 2, 200))
def comp(qx, q):
    dx, dy = x - qx, y; r3 = (dx ** 2 + dy ** 2) ** 1.5 + 1e-9; return q * dx / r3, q * dy / r3, q / np.sqrt(dx ** 2 + dy ** 2 + 1e-9)
ex1, ey1, v1 = comp(-1, 1); ex2, ey2, v2 = comp(1, -1)
Ex, Ey, V = ex1 + ex2, ey1 + ey2, v1 + v2
ax.streamplot(x, y, Ex, Ey, color=PAL["blue"], density=0.75, linewidth=1.1, arrowsize=1.1)
ax.contour(x, y, V, levels=[-2, -1, -0.5, -0.2, 0, 0.2, 0.5, 1, 2], colors=PAL["amber"], linestyles="dashed", linewidths=1.2)
for qx, s, c in [(-1, "+", PAL["red"]), (1, "−", PAL["blue"])]:
    ax.add_patch(plt.Circle((qx, 0), 0.18, color=c, zorder=5)); ax.text(qx, -0.02, s, color="white", ha="center", va="center", fontsize=16, fontweight="bold", zorder=6)
ax.set_aspect("equal"); ax.set_xlim(-3, 3); ax.set_ylim(-2, 2); ax.axis("off")
ax.plot([], [], color=PAL["blue"], label="field lines (+ → −)"); ax.plot([], [], color=PAL["amber"], ls="--", label="equipotentials (zero work along them)")
ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.12), ncol=2, fontsize=9)
saveplot(fig, P("cpas04-field"))

# CPAS-09 titration: 25 mL 0.10 M acetic acid with 0.10 M NaOH (exact charge balance)
Ka, Kw, Ca0, Cb, Va = 10 ** -4.76, 1e-14, 0.10, 0.10, 25.0
def pH_at(Vb):
    Ct = Ca0 * Va / (Va + Vb); Na = Cb * Vb / (Va + Vb); lo, hi = 0.0, 14.0
    for _ in range(80):
        m = (lo + hi) / 2; H = 10 ** -m; f = H + Na - Kw / H - Ct * Ka / (Ka + H)
        lo, hi = (m, hi) if f > 0 else (lo, m)
    return (lo + hi) / 2
vb = np.linspace(0, 50, 600); ph = [pH_at(v) for v in vb]
fig, ax = plot(6.4, 3.6)
ax.plot(vb, ph, color=PAL["blue"], lw=2.5)
ax.plot([12.5], [pH_at(12.5)], "o", color=PAL["green"]); ax.plot([25], [pH_at(25)], "o", color=PAL["red"])
ax.annotate(f"half-equivalence\npH = pKa = 4.76", xy=(12.5, 4.76), xytext=(3, 8.2), arrowprops=dict(arrowstyle="->"), fontsize=10)
ax.annotate(f"equivalence\npH ≈ {pH_at(25):.1f} (> 7)", xy=(25, pH_at(25)), xytext=(30, 5.2), arrowprops=dict(arrowstyle="->"), fontsize=10)
ax.axvspan(5, 20, color=PAL["greenL"], zorder=0); ax.text(12.5, 2.0, "buffer region", ha="center", fontsize=9, color=PAL["green"])
ax.set_xlabel("volume of NaOH added (mL)"); ax.set_ylabel("pH"); ax.set_ylim(0, 14); ax.set_xlim(0, 50)
saveplot(fig, P("cpas09-titration"))

# CPAS-11 Doppler wavefronts: source moving right at 0.5 v
fig, ax = plot(6.0, 3.0)
for k in range(6):
    tk = k * 1.0; cx = 0.5 * tk; r = 1.0 * (5 - tk) + 0.0001
    if r > 0: ax.add_patch(plt.Circle((cx, 0), r, fill=False, color=PAL["blue"], lw=1.4))
ax.plot([2.5], [0], "o", color=PAL["red"], ms=10); ax.annotate("", xy=(3.4, 0), xytext=(2.6, 0), arrowprops=dict(arrowstyle="->", color=PAL["red"], lw=2))
ax.text(2.0, 6.0, "ahead: waves bunched\nshort λ → higher pitch", fontsize=9, ha="left", color=PAL["ink"])
ax.text(-5.5, 6.0, "behind: waves spread\nlong λ → lower pitch", fontsize=9, ha="left", color=PAL["ink"])
ax.set_aspect("equal"); ax.set_xlim(-5.6, 6.0); ax.set_ylim(-5.2, 7.4); ax.axis("off")
saveplot(fig, P("cpas11-doppler"))

# BBFL-01 MM curve
fig, ax = plot(6.0, 3.4)
S = np.linspace(0, 20, 400); Vm, Km = 10, 2
ax.plot(S, mm(S, Vm, Km), color=PAL["blue"], lw=2.5)
ax.axhline(Vm, color=PAL["red"], ls="--", lw=1.2); ax.text(19.8, Vm + 0.3, "Vmax", color=PAL["red"], ha="right")
ax.plot([0, Km, Km], [Vm / 2, Vm / 2, 0], color=PAL["amber"], ls=":", lw=1.6)
ax.set_yticks([0, Vm / 2, Vm], ["0", "Vmax/2", "Vmax"]); ax.set_xticks([0, Km, 5, 10, 15, 20], ["0", "Km", "5", "10", "15", "20"])
ax.set_xlabel("substrate concentration [S]"); ax.set_ylabel("initial rate v₀"); ax.set_ylim(0, 11.5); ax.set_xlim(0, 20)
saveplot(fig, P("bbfl01-mm"))

# BBFL-02 MM vs LB, Km 2 vs Km 0.5 (same Vmax)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.6, 3.4), dpi=100)
for a in (a1, a2):
    a.spines["top"].set_visible(False); a.spines["right"].set_visible(False)
S = np.linspace(0.01, 10, 400)
for K, c, lab in [(2, PAL["blue"], "Km = 2 mM"), (0.5, PAL["amber"], "Km = 0.5 mM (lower)")]:
    a1.plot(S, mm(S, 10, K), color=c, lw=2.3, label=lab); a1.plot([K, K], [0, 5], color=c, ls=":", lw=1.4)
    xs = np.linspace(-1 / K, 2.2, 50); a2.plot(xs, (K / 10) * xs + 0.1, color=c, lw=2.3)
    a2.plot([-1 / K], [0], "o", color=c); a2.text(-1 / K, -0.07, f"−1/Km\n= {-1 / K:g}", color=c, ha="center", va="top", fontsize=9)
a1.axhline(10, color=PAL["red"], ls="--", lw=1); a1.axhline(5, color=PAL["line"], ls=":", lw=1)
a1.set_title("Michaelis-Menten (MM)"); a1.set_xlabel("[S] (mM)"); a1.set_ylabel("v₀"); a1.set_ylim(0, 11); a1.legend(fontsize=9, loc="lower right")
a2.axhline(0, color=PAL["sub"], lw=1); a2.axvline(0, color=PAL["sub"], lw=1)
a2.text(-0.08, 0.13, "1/Vmax", color=PAL["red"], ha="right", fontsize=9)
a2.set_title("Lineweaver-Burk (LB)"); a2.set_xlabel("1/[S] (mM⁻¹)"); a2.set_ylabel("1/v₀"); a2.set_xlim(-2.4, 2.3); a2.set_ylim(-0.32, 0.6)
a2.annotate("lower Km →\nfarther left", xy=(-2, 0.02), xytext=(-2.3, 0.3), fontsize=9, arrowprops=dict(arrowstyle="->"))
saveplot(fig, P("bbfl02-mm-lb"))

# BBFL-03 LB for three inhibitor types (Km 2, Vmax 10, alpha 2)
fig, axs = plt.subplots(1, 3, figsize=(8.4, 3.0), dpi=100)
cases = [("Competitive", (4, 10)), ("Noncompetitive", (2, 5)), ("Uncompetitive", (1, 5))]
for a, (name, (Ki, Vi)) in zip(axs, cases):
    for spine in ("top", "right"): a.spines[spine].set_visible(False)
    for K, V, c, lab in [(2, 10, PAL["blue"], "no inhibitor"), (Ki, Vi, PAL["red"], "+ inhibitor")]:
        xs = np.linspace(-1 / K, 1.5, 50); a.plot(xs, (K / V) * xs + 1 / V, color=c, lw=2.2, label=lab)
    a.axhline(0, color=PAL["sub"], lw=1); a.axvline(0, color=PAL["sub"], lw=1)
    a.set_title(name, fontsize=11); a.set_xlim(-1.1, 1.5); a.set_ylim(-0.05, 0.6); a.set_xticks([]); a.set_yticks([])
    a.set_xlabel("1/[S]", fontsize=9); a.set_ylabel("1/v₀", fontsize=9)
axs[0].text(0.12, 0.015, "same y-int (Vmax same)", fontsize=8.5); axs[1].text(-1.05, 0.05, "same\nx-int", fontsize=8.5); axs[2].text(0.1, 0.03, "parallel", fontsize=8.5)
axs[0].legend(fontsize=8, loc="upper left")
saveplot(fig, P("bbfl03-inhibitors"))

# BBFL-04 glycine titration (idealized: protons removed per molecule vs pH), pKa 2.34, 9.60
pH = np.linspace(0.5, 12.5, 500); eq = 1 / (1 + 10 ** (2.34 - pH)) + 1 / (1 + 10 ** (9.60 - pH))
fig, ax = plot(6.2, 3.6)
ax.plot(eq, pH, color=PAL["blue"], lw=2.5)
for e, p, lab, c in [(0.5, 2.34, "pKa1 = 2.34", PAL["green"]), (1.0, 5.97, "pI = 5.97", PAL["red"]), (1.5, 9.60, "pKa2 = 9.60", PAL["green"])]:
    ax.plot([e], [p], "o", color=c); ax.text(e + 0.06, p - 0.9, lab, color=c, fontsize=10)
ax.text(0.03, 11.4, "+H₃N–CH₂–COOH\n(net +1)", fontsize=8.5); ax.text(0.75, 11.4, "+H₃N–CH₂–COO⁻\n(net 0)", fontsize=8.5); ax.text(1.5, 11.4, "H₂N–CH₂–COO⁻\n(net −1)", fontsize=8.5)
ax.set_xlabel("equivalents of OH⁻ added"); ax.set_ylabel("pH"); ax.set_xlim(0, 2); ax.set_ylim(0, 13.5)
saveplot(fig, P("bbfl04-gly"))

# BBFL-07 Hb (Hill n = 2.8) and Mb (hyperbola)
po2 = np.linspace(0, 100, 400)
def hill(p, p50, n): return 100 * p ** n / (p50 ** n + p ** n)
fig, ax = plot(6.4, 3.6)
ax.plot(po2, hill(po2, 2.8, 1), color=PAL["purple"], lw=2.2, label="myoglobin (P50 ≈ 3)")
ax.plot(po2, hill(po2, 26, 2.8), color=PAL["blue"], lw=2.6, label="hemoglobin (P50 ≈ 26)")
ax.plot(po2, hill(po2, 36, 2.8), color=PAL["red"], lw=2, ls="--", label="right shift (CADET)")
ax.plot(po2, hill(po2, 19, 2.8), color=PAL["green"], lw=2, ls="--", label="left shift (HbF, CO)")
ax.axhline(50, color=PAL["line"], ls=":", lw=1)
ax.set_xlabel("PO₂ (mmHg)"); ax.set_ylabel("% O₂ saturation"); ax.set_ylim(0, 102); ax.set_xlim(0, 100); ax.legend(fontsize=9, loc="lower right")
saveplot(fig, P("bbfl07-hb"))

# LAB-04 PCR temperature profile, 3 cycles
fig, ax = plot(6.4, 3.0)
tt, TT = [0], [25]; t0 = 0
for k in range(3):
    for T, d in [(95, 30), (55, 30), (72, 45)]:
        tt += [t0 + 6, t0 + d]; TT += [T, T]; t0 += d
ax.plot(tt, TT, color=PAL["red"], lw=2.3)
for T, lab, x, dy in [(95, "denature\n95 °C", 18, 3), (55, "anneal\n~55 °C", 48, -15), (72, "extend\n72 °C", 86, 3)]:
    ax.text(x, T + dy, lab, ha="center", fontsize=9)
ax.text(t0 - 2, 30, "×2 copies per cycle", ha="right", fontsize=10, color=PAL["blue"])
ax.set_xlabel("time (s)"); ax.set_ylabel("temperature (°C)"); ax.set_ylim(20, 112); ax.set_yticks([25, 55, 72, 95]); ax.set_xlim(0, t0)
saveplot(fig, P("lab04-pcr"))

# LAB-05 Beer-Lambert standard curve
fig, ax = plot(6.0, 3.4)
c = np.array([0, 0.1, 0.2, 0.3, 0.4, 0.5]); A = 1.8 * c
ax.plot(c, A, "o", color=PAL["blue"]); ax.plot([0, 0.55], [0, 0.99], color=PAL["blue"], lw=2, label="standards: A = εlc (slope = εl)")
ax.plot([0, 0.35, 0.35], [0.63, 0.63, 0], color=PAL["red"], ls="--", lw=1.6); ax.plot([0.35], [0.63], "s", color=PAL["red"])
ax.text(0.01, 0.66, "unknown: A = 0.63", color=PAL["red"], fontsize=10); ax.text(0.36, 0.04, "c = 0.35 mM", color=PAL["red"], fontsize=10)
ax.set_xlabel("concentration (mM)"); ax.set_ylabel("absorbance A"); ax.set_xlim(0, 0.56); ax.set_ylim(0, 1.05); ax.legend(fontsize=9, loc="upper left")
saveplot(fig, P("lab05-beer"))
