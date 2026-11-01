"""Inline native-Word-equation (OMML) support for python-docx.

Usage:
    write_rich(paragraph, text, size=..., bold=...)
Text may contain math spans wrapped in ⟦...⟧ using a small linear syntax:
    F_perp  Γ_T  η_g  τ_cap  β_g  g^*  H^2
    frac{a}{b}   int{...}   ( ... )   [ ... ]
Everything else is emitted as normal runs. Before splitting, `mark_math`
auto-wraps a list of known expressions and compound symbol tokens.
"""
import re
from xml.sax.saxutils import escape

from docx.oxml import parse_xml
from docx.shared import Pt

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
NSDECL = f'xmlns:m="{M}" xmlns:w="{W}"'

GREEK = set('αβγδεζηθικλμνξπρστυφχψωΓΔΘΛΞΠΣΦΨΩ')


def mr(t, plain=False):
    rpr = '<m:rPr><m:sty m:val="p"/></m:rPr>' if plain else ''
    return (f'<m:r>{rpr}<w:rPr><w:rFonts w:ascii="Cambria Math" '
            f'w:hAnsi="Cambria Math"/></w:rPr>'
            f'<m:t xml:space="preserve">{escape(t)}</m:t></m:r>')


def ssub(base, sub):
    return (f'<m:sSub><m:e>{base}</m:e>'
            f'<m:sub><m:r><m:t xml:space="preserve">{escape(sub)}</m:t></m:r>'
            f'</m:sub></m:sSub>')


def ssup(base, sup):
    return (f'<m:sSup><m:e>{base}</m:e>'
            f'<m:sup><m:r><m:t xml:space="preserve">{escape(sup)}</m:t></m:r>'
            f'</m:sup></m:sSup>')


def ssubsup(base, sub, sup):
    return (f'<m:sSubSup><m:e>{base}</m:e>'
            f'<m:sub><m:r><m:t xml:space="preserve">{escape(sub)}</m:t></m:r></m:sub>'
            f'<m:sup><m:r><m:t xml:space="preserve">{escape(sup)}</m:t></m:r></m:sup>'
            f'</m:sSubSup>')


def frac(num, den):
    return (f'<m:f><m:fPr><m:type m:val="bar"/></m:fPr>'
            f'<m:num>{num}</m:num><m:den>{den}</m:den></m:f>')


def delim(inner, beg='(', end=')'):
    return (f'<m:d><m:dPr><m:begChr m:val="{escape(beg)}"/>'
            f'<m:endChr m:val="{escape(end)}"/></m:dPr>'
            f'<m:e>{inner}</m:e></m:d>')


def nary_int(inner):
    return ('<m:nary><m:naryPr><m:chr m:val="∫"/>'
            '<m:limLoc m:val="subSup"/><m:supHide m:val="1"/>'
            '<m:subHide m:val="1"/></m:naryPr>'
            '<m:sub/><m:sup/>'
            f'<m:e>{inner}</m:e></m:nary>')


def _brace(s, i):
    """i points at '{'; return (inner, index-after-'}')."""
    assert s[i] == '{'
    depth = 0
    for j in range(i, len(s)):
        if s[j] == '{':
            depth += 1
        elif s[j] == '}':
            depth -= 1
            if depth == 0:
                return s[i + 1:j], j + 1
    raise ValueError('unmatched {')


def _match_paren(s, i):
    depth = 0
    for j in range(i, len(s)):
        if s[j] in '([':
            depth += 1
        elif s[j] in ')]':
            depth -= 1
            if depth == 0:
                return j
    raise ValueError('unmatched paren')


def _sub_arg(s, i):
    """Read _ or ^ argument: {..} or a run of word chars."""
    if i < len(s) and s[i] == '{':
        return _brace(s, i)
    m = re.match(r'[A-Za-z0-9*α-ωΑ-Ω]+', s[i:])
    return m.group(0), i + len(m.group(0))


def parse_seq(s):
    out = []
    i = 0
    while i < len(s):
        c = s[i]
        if c == ' ':
            out.append(mr(' ', plain=True))
            i += 1
            continue
        if s.startswith('frac{', i):
            a, j = _brace(s, i + 4)
            b, k = _brace(s, j)
            out.append(frac(parse_seq(a), parse_seq(b)))
            i = k
            continue
        if s.startswith('int{', i):
            a, j = _brace(s, i + 3)
            out.append(mr('∫', plain=True) + mr(' ', plain=True) + parse_seq(a))
            i = j
            continue
        if c == '|':
            j = s.find('|', i + 1)
            if j == -1:
                out.append(mr('|', plain=True)); i += 1; continue
            out.append(delim(parse_seq(s[i + 1:j]), '|', '|'))
            i = j + 1
            continue
        if c in '([':
            j = _match_paren(s, i)
            out.append(delim(parse_seq(s[i + 1:j]),
                             c, ')' if c == '(' else ']'))
            i = j + 1
            continue
        m = re.match(r'[A-Za-zΑ-Ωα-ω]+|\d+\.?\d*', s[i:])
        if m:
            name = m.group(0)
            i += len(name)
            sub = sup = None
            if i < len(s) and s[i] == '_':
                sub, i = _sub_arg(s, i + 1)
            if i < len(s) and s[i] == '^':
                sup, i = _sub_arg(s, i + 1)
            plain = len(name) > 1 or name in GREEK
            base = mr(name, plain=plain)
            if sub and sup:
                out.append(ssubsup(base, sub, sup))
            elif sub:
                out.append(ssub(base, sub))
            elif sup:
                out.append(ssup(base, sup))
            else:
                out.append(base)
            continue
        # any other char → literal math run
        j = i
        while j < len(s) and not re.match(r'[A-Za-zΑ-Ωα-ω0-9 {[(_]|frac\{|int\{', s[j:]):
            j += 1
        out.append(mr(s[i:j], plain=True))
        i = j
    return ''.join(out)


def omath(linear):
    """Return an lxml <m:oMath> element for one linear expression."""
    inner = parse_seq(linear)
    return parse_xml(f'<m:oMath {NSDECL}>{inner}</m:oMath>')


# ------------------------------------------------------------------ marking
EXPRS = [
    (r"UTI = ∫ ?max\(\|F_perp\|\(1−η_g\) − F_cap, 0\) ?dt",
     "⟦UTI = int{max(|F_perp|(1−η_g)−F_cap,0) dt}⟧"),
    (r"F_perp = R − F_parallel", "⟦F_perp = R − F_parallel⟧"),
    (r"N = m·g \+ R_v", "⟦N = m g + R_v⟧"),
    (r"F_cap = μ·f_u·N", "⟦F_cap = μ f_u N⟧"),
    (r"τ_cap = μ·f_u·N·r_f", "⟦τ_cap = μ f_u N r_f⟧"),
    (r"Γ_T = max\|F_perp\|/\(μ f_u m g\)",
     "⟦Γ_T = frac{max|F_perp|}{μ f_u m g}⟧"),
    (r"B_UTI\(g\*\) = 1 − UTI_red/UTI_conv",
     "⟦B_UTI(g^*) = 1 − frac{UTI_red}{UTI_conv}⟧"),
    (r"B_UAI\(g\*\) = 1 − UAI_red/UAI_conv",
     "⟦B_UAI(g^*) = 1 − frac{UAI_red}{UAI_conv}⟧"),
    (r"I_yaw = 0\.013·m·H²", "⟦I_yaw = 0.013 m H^2⟧"),
    (r"m ~ N\(75,9²\)", "⟦m ~ N(75,9^2)⟧"),
    (r"H ~ N\(1\.75,0\.08²\)", "⟦H ~ N(1.75,0.08^2)⟧"),
    (r"μ ~ U\[0\.3,0\.7\]", "⟦μ ~ U[0.3,0.7]⟧"),
    (r"t_react ~ U\[0\.3,0\.6\] ?s?", "⟦t_react ~ U[0.3,0.6]⟧ s"),
    (r"f_u ~ U?\[0\.5,0\.85\] ?s?", "⟦f_u ~ U[0.5,0.85]⟧ s"),
    (r"log\(impulse_redesign/impulse_conventional\)",
     "⟦log(frac{impulse_redesign}{impulse_conventional})⟧"),
    (r"\(1−η_g\)\|F_perp\|", "⟦(1−η_g)|F_perp|⟧"),
    (r"N ≈ mg", "⟦N ≈ m g⟧"),
    (r"μN", "⟦μ N⟧"),
]

TOKENS = {
    "F_parallel": "F_parallel", "F_perp": "F_perp", "F_task": "F_task",
    "F_cap": "F_cap", "tau_cap": "τ_cap", "I_yaw": "I_yaw",
    "t_react": "t_react", "r_f": "r_f", "e_d": "e_d", "f_u": "f_u",
    "J_corr": "J_corr", "J_corr_ang": "J_corr_ang", "x_free": "x_free",
    "x_margin": "x_margin", "g_Earth": "g_Earth", "B_UTI": "B_UTI",
    "B_UAI": "B_UAI", "Γ_T": "Γ_T", "τ_cap": "τ_cap", "η_g": "η_g",
    "β_g": "β_g", "m/s²": "m/s^2", "N(75,9²)": "N(75,9^2)",
    "N(1.75,0.08²)": "N(1.75,0.08^2)", "H²": "H^2", "m²": "m^2",
    "R²": "R^2", "9²": "9^2", "0.08²": "0.08^2", "g*": "g^*",
}

_TOKEN_RE = re.compile(
    "|".join(re.escape(k) for k in sorted(TOKENS, key=len, reverse=True)))

_BARE_GREEK = re.compile(r'(?<![A-Za-z_Α-Ωα-ω])([μτηβΓ])(?![A-Za-z_Α-Ωα-ω])')


def mark_math(text):
    """Wrap known math expressions and compound tokens in ⟦...⟧."""
    for pat, rep in EXPRS:
        text = re.sub(pat, rep, text)
    # token pass only outside already-marked spans
    parts = re.split(r'(⟦[^⟧]*⟧)', text)
    for i, seg in enumerate(parts):
        if seg.startswith('⟦'):
            continue
        seg = _TOKEN_RE.sub(lambda m: f"⟦{TOKENS[m.group(0)]}⟧", seg)
        seg = _BARE_GREEK.sub(lambda m: f"⟦{m.group(1)}⟧", seg)
        parts[i] = seg
    return ''.join(parts)


def write_rich(p, text, size=None, bold=None):
    """Write text into paragraph p; ⟦...⟧ spans become inline OMML."""
    text = re.sub(r'\s+', ' ', text).strip()
    text = mark_math(text)
    for seg in re.split(r'(⟦[^⟧]*⟧)', text):
        if not seg:
            continue
        if seg.startswith('⟦') and seg.endswith('⟧'):
            p._p.append(omath(seg[1:-1]))
        else:
            # *...* spans in prose become genuine italic runs
            for sub in re.split(r'(\*[^*]+\*)', seg):
                if not sub:
                    continue
                italic = sub.startswith('*') and sub.endswith('*') and len(sub) > 2
                r = p.add_run(sub[1:-1] if italic else sub)
                if italic:
                    r.italic = True
                if size is not None:
                    r.font.size = Pt(size)
                if bold is not None:
                    r.bold = bold
    return p


# ------------------------------------------------------------------ pptx
A_NS = 'http://schemas.openxmlformats.org/drawingml/2006/main'


def omath_para(linear):
    """<m:oMathPara> element wrapping one linear expression (for pptx a:m)."""
    inner = parse_seq(linear)
    return parse_xml(
        f'<m:oMathPara {NSDECL}><m:oMath>{inner}</m:oMath></m:oMathPara>')


MC_NS = 'http://schemas.openxmlformats.org/markup-compatibility/2006'


def a_m(linear):
    """<a:m> DrawingML math element for a pptx text paragraph (the native
    Office Math container; renders in PowerPoint 2010+)."""
    inner = parse_seq(linear)
    inner = re.sub(r'<w:rPr>.*?</w:rPr>', '', inner, flags=re.S)
    el = parse_xml(f'<a:m xmlns:a="{A_NS}" xmlns:m="{M}"/>')
    el.append(parse_xml(
        f'<m:oMathPara {NSDECL}><m:oMath>{inner}</m:oMath></m:oMathPara>'))
    return el


def pptx_rich(p, text):
    """Write text into a python-pptx paragraph; ⟦...⟧ spans become a:m math.
    Math auto-marking via mark_math() applies to the whole string."""
    import re as _re
    text = mark_math(re.sub(r'\s+', ' ', text).strip())
    for seg in _re.split(r'(⟦[^⟧]*⟧)', text):
        if not seg:
            continue
        if seg.startswith('⟦') and seg.endswith('⟧'):
            p._p.append(a_m(seg[1:-1]))
        else:
            p.add_run().text = seg
    return p
