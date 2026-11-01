"""Integrate BUILDING_ENVIRONMENT_SUPPLEMENT.docx into manuscript_author.docx.

Produces BUILDING_ENVIRONMENT_MAIN_SUPPLEMENT_INTEGRATED.docx:
- S1-S10 content folded into the corresponding main-text paragraphs
- every figure/table placed inline immediately after its first-citation
  paragraph, captions below figures, titles above tables
- tables renumbered by first appearance (new transition table becomes
  Table 4; the sensitivity summary becomes Table 5)
- terminal "Tables" and "Figure captions" sections deleted
- all Supplement cross-references removed
Science is frozen: only connective prose and pointer rewrites are added.
"""
import copy
import sys

import docx
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph

sys.path.insert(0, __file__.rsplit('/', 1)[0])
from omml import write_rich  # noqa: E402

MAIN = sys.argv[1]
SUPP = sys.argv[2]
OUT = sys.argv[3]

doc = docx.Document(MAIN)
supp = docx.Document(SUPP)
body = doc.element.body


def para(pred):
    for p in doc.paragraphs:
        if pred(p.text):
            return p
    raise LookupError(pred)


def replace_text(p, old, new):
    hits = 0
    for t in p._p.findall('.//' + qn('w:t')):
        if t.text and old in t.text:
            t.text = t.text.replace(old, new)
            hits += 1
    if hits == 0:
        raise LookupError(f'{old!r} not found in {p.text[:60]!r}')


def append_rich(p, text):
    # append runs (and ⟦...⟧ OMML spans) to the end of an existing paragraph
    write_rich(p, ' ' + text)


def blocks():
    out = []
    for ch in body.iterchildren():
        if ch.tag == qn('w:p'):
            out.append(Paragraph(ch, doc))
        elif ch.tag == qn('w:tbl'):
            out.append(Table(ch, doc))
    return out


def insert_after(anchor_el, elements):
    """Insert elements (in order) directly after anchor element."""
    cur = anchor_el
    for el in elements:
        cur.addnext(el)
        cur = el


# ---------------------------------------------------------------- 1. text edits
p = para(lambda t: t.startswith('2.10 External validation'))
replace_text(p, ' (see Supplement)', '')

p = para(lambda t: t.startswith('3.4 Momentum-aware redesign'))
replace_text(p,
             '(raw demand integrals are reported per variant in the supplement)',
             '(raw demand integrals per variant are released as mc_summary.csv '
             'in the public repository)')

p = para(lambda t: t.startswith('3.6 Passive geometric guidance'))
replace_text(p, 'Table S2', 'Table 4')

p = para(lambda t: t.startswith('3.9 Sensitivity and suit loads'))
replace_text(p, '(Table 4)', '(Table 5)')
append_rich(p, 'The full one-at-a-time sweep is released as sensitivity.csv.')

p = para(lambda t: t.startswith('4.4 Degrees of freedom'))
replace_text(p, 'mapped in the Pareto analysis (Supplement)',
             'mapped in the Pareto trade-off')
append_rich(p,
            'Guidance strength trades impulse suppression against '
            'confinement/reach penalty: centering (⟦x_free⟧ 0.05 m, ⟦η⟧ = 0.8) '
            'versus guided (⟦x_free⟧ 0.02 m, ⟦η⟧ = 0.9) both fully suppress '
            'UTI at low g in this model, so the choice is driven by secondary '
            'penalties rather than stability; we report a multi-objective '
            'summary rather than a scalar composite score.')

p = para(lambda t: t.startswith('4.5 Implications'))
# (no edit; placeholder in case)

# ------------------------------------------------------- 2. supplement prose
p = para(lambda t: t.startswith('2.6 Gravity sweep'))
append_rich(p,
            'The full 40-point response grid and per-variant benefit curves '
            'are released as gravity_sweep.csv and benefit_curves.csv in the '
            'public repository.')  # S6

p = para(lambda t: t.startswith('2.7 Uncertainty'))
append_rich(p,
            'Extended Monte Carlo summaries — means and 5–95th percentiles for '
            'every case × variant × ⟦g*⟧ cell, including the 40 kg suit-mass '
            'and restricted-ROM configurations — are released as '
            'mc_summary.csv, mc_summary_suit40.csv and mc_summary_suit40_rom.csv; '
            'doubling-N convergence diagnostics (N = 250–4000) as '
            'convergence.csv in the public repository.')  # S1 + S4

p = para(lambda t: t.startswith('2.8 Statistics'))
append_rich(p,
            'Fitted slopes, p-values and ⟦R^2⟧ per variant pair are released '
            'as interaction.csv.')  # S5

p = para(lambda t: t.startswith('3.1 Model verification'))
append_rich(p,
            'The cosmetic control reproduces baseline mechanics within Monte '
            'Carlo noise (door: UAI within ~3% at lunar ⟦g*⟧).')  # S7

p = para(lambda t: t.startswith('3.8 Cross-interface synthesis'))
append_rich(p,
            'Falsification criteria A–F were evaluated explicitly: none '
            'triggered rejection; benefit is gravity-specific (⟦B_UTI⟧ ≈ 0 at '
            '1 ⟦g*⟧) and cross-interface.')  # S8

# -------------------------------------------- 3. collect figure/table blocks
bl = blocks()


def blk_para(text_start):
    for b in bl:
        if isinstance(b, Paragraph) and b.text.startswith(text_start):
            return b
    raise LookupError(text_start)


def table_after(para_obj):
    el = para_obj._p.getnext()
    assert el.tag == qn('w:tbl'), 'expected table after title para'
    return Table(el, doc)


fig_blocks = {}      # num -> (caption_para, image_para)
for i in range(1, 7):
    cap = blk_para(f'Figure {i}.')
    img_el = cap._p.getnext()
    assert img_el.tag == qn('w:p') and img_el.findall(
        './/' + qn('a:blip')), f'Figure {i}: image not after caption'
    fig_blocks[i] = (cap, Paragraph(img_el, doc))

tbl_blocks = {}      # num -> (title_para, table)
for n in range(1, 5):
    tp = blk_para(f'Table {n}.')
    tbl_blocks[n] = (tp, table_after(tp))

# new transition table cloned from supplement S10
sup_tbl = supp.tables[0]._tbl
new_tbl = copy.deepcopy(sup_tbl)
t4_title = doc.add_paragraph()
write_rich(t4_title,
           'Table 4. Exploratory transition gravities: first ⟦g*⟧ at which '
           'the baseline stabilization-demand ratio ⟦Γ_T⟧ ≥ 1, and the first '
           '⟦g*⟧ at which normalized benefit ⟦B_UTI⟧ ≥ 0.5. A dash marks no '
           'transition within the swept range.')

# -------------------------------------------- 4. move blocks inline, renumber
# anchor paragraphs by first citation
anchors = {
    'fig1': para(lambda t: t.startswith('1.4 Momentum generation')),
    'fig2': para(lambda t: t.startswith('2.1 Conceptual framework')),
    'tbl1': para(lambda t: t.startswith('2.4 Human model')),
    'tbl2': para(lambda t: t.startswith('2.5 Canonical scenarios')),
    'tbl3': para(lambda t: t.startswith('3.2 Gravity and stabilization')),
    'fig3': para(lambda t: t.startswith('3.3 Conventional-interface')),
    'fig4': para(lambda t: t.startswith('3.4 Momentum-aware redesign')),
    'fig5tbl4': para(lambda t: t.startswith('3.6 Passive geometric')),
    'tbl5': para(lambda t: t.startswith('3.9 Sensitivity and suit loads')),
    'fig6': para(lambda t: t.startswith('4.5 Implications')),
}


def move_fig(n, anchor):
    cap, img = fig_blocks[n]
    els = [img._p, cap._p]          # image first, caption below
    insert_after(anchor._p, els)


def move_tbl(n, anchor, title_override=None):
    tp, tb = tbl_blocks[n]
    if title_override:
        for r in list(tp._p):
            tp._p.remove(r)
        write_rich(tp, title_override)
    insert_after(anchor._p, [tp._p, tb._tbl])


move_fig(1, anchors['fig1'])
move_fig(2, anchors['fig2'])
move_tbl(1, anchors['tbl1'])
move_tbl(2, anchors['tbl2'])
move_tbl(3, anchors['tbl3'])
move_fig(3, anchors['fig3'])
move_fig(4, anchors['fig4'])
# §3.6 cites Figure 5 then the new transition table (Table 4), in that order
move_fig(5, anchors['fig5tbl4'])
insert_after(fig_blocks[5][0]._p, [t4_title._p, new_tbl])
# sensitivity table renumbered 4 -> 5
tp4, _ = tbl_blocks[4]
replace_text(tp4, 'Table 4.', 'Table 5.')
move_tbl(4, anchors['tbl5'])
# fig6 last
move_fig(6, anchors['fig6'])

# ------------------------------------------------ 5. delete terminal sections
for b in list(blocks()):
    if isinstance(b, Paragraph) and b.style.name == 'Heading 1' \
            and b.text.strip() in ('Tables', 'Figure captions'):
        body.remove(b._p)

doc.save(OUT)
print('saved', OUT)
