"""Mastery-sheet symbol pass (2026-11-15): turn plain-text subscripts/superscripts into real ones.
   E_K -> E<sub>K</sub>, ΔS_univ -> ΔS<sub>univ</sub>, t_1/2 -> t<sub>1/2</sub>, [K⁺]o -> [K⁺]<sub>o</sub>,
   e^0.655 -> e<sup>0.655</sup>, Kb/Kw/pKb/pKw -> K<sub>b</sub>... Works on rendered sheet HTML only (text between tags,
   never inside <svg>, attributes, or Q-id link text like 'Q #x5E_001'). Idempotent."""
import re
SUBD = str.maketrans('₀₁₂₃₄₅₆₇₈₉', '0123456789')
QID = re.compile(r'#?x[0-9A-Za-z]{1,4}_\d+|#?xp\d+')
US = re.compile(r'(?<![\w#])((?:Δ|δ)?[A-Za-zα-ωΑ-Ω]{1,4}\u0307?°?|KE|PE|Outcomes|Inputs)_(\{[^}<]*\}|1/2|[A-Za-z0-9₀-₉]+)')
MU = re.compile(r'μ_([sk])')
ION = re.compile(r'(\[[A-Z][a-z]?[⁺⁻²³]*\])(o|i|in|out)\b')
CARET = re.compile(r'(?<![\w^])(e|10|2)\^(-?[0-9]+(?:\.[0-9]+)?|\([^)<]{1,12}\))')
KBW = re.compile(r'\b(p?)K(b|w|p|c)\b')
def sub_text(t):
    if '_' not in t and '^' not in t and 'K' not in t and ']' not in t: return t
    keep = {}
    def hold(m):
        k = f'\x00{len(keep)}\x00'; keep[k] = m.group(); return k
    t = QID.sub(hold, t)
    t = re.sub(r'https?://\S+', hold, t)
    def us(m):
        s = m.group(2)
        if s.startswith('{'): s = s[1:-1]
        return f'{m.group(1)}<sub>{s.translate(SUBD)}</sub>'
    t = t.replace('x_AP°_A', 'x<sub>A</sub>P°<sub>A</sub>').replace('x_BP°_B', 'x<sub>B</sub>P°<sub>B</sub>')
    t = MU.sub(r'μ<sub>\1</sub>', t)
    t = US.sub(us, t)
    t = ION.sub(lambda m: f'{m.group(1)}<sub>{m.group(2)}</sub>', t)
    t = CARET.sub(lambda m: f'{m.group(1)}<sup>{m.group(2).strip("()") if m.group(2).startswith("(") and "/" not in m.group(2) else m.group(2)}</sup>', t)
    t = KBW.sub(lambda m: f'{m.group(1)}K<sub>{m.group(2)}</sub>', t)
    t = re.sub(r'\bVm\b', 'V<sub>m</sub>', t)
    t = re.sub(r'\bkcat\b', 'k<sub>cat</sub>', t)
    t = re.sub(r'\](total|eq|0)\b', r']<sub>\1</sub>', t)
    for k, v in keep.items(): t = t.replace(k, v)
    return t
def fix_html(h):
    parts = re.split(r'(<svg.*?</svg>|<button[^>]*class="qref"[^>]*>.*?</button>|<[^>]+>)', h, flags=re.S)
    return ''.join(p if (i % 2) else sub_text(p) for i, p in enumerate(parts))
