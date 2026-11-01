# FINAL_HANDOFF.md — gravity_momentum_design (Building and Environment)

## Summary
- **Final title:** Gravity-dependent mechanics of human–built-environment
  interfaces: preventing unintended translational and rotational impulse under
  partial gravity
- **Central claim:** gravity is an implicit stabilizing component of terrestrial
  interfaces; its loss under partial gravity raises task-irrelevant transverse
  and angular impulse that momentum-aware interface geometry can prevent.
- **Target journal:** Building and Environment (Elsevier), Research Paper.
- **Manuscript words:** ~2,500 main text (abstract 239 ≤ 250) — compact;
  authors may wish to expand Discussion.
- **References:** 25 (all verified real; see audit/REFERENCE_AUDIT.md).
- **Figures/Tables:** 6 figures, 4 main tables + supplement.
- **Gravity range:** g* = 0.05–1.00 (40-pt sweep) + MC at {0.165,0.25,0.38,0.5,0.75,1.0}.
- **Monte Carlo:** N = 2000 per condition (convergence < ~5% mean drift N=250→4000).
- **Canonical cases:** door, seat ingress, control, workstation, circulation (+2 cosmetic negative controls).

## Principal quantitative findings
- Hinged-door UAI grows ~1/g: ~{uai_door_earth} N·m·s at 1 g → ~7.7 N·m·s lunar
  (>>1000×); Γ_T 0.13 → 0.81; lateral-slide Γ_T exceeds 1 below ~0.4 g.
- Chair ingress at 0.165 g: ~4.1 corrective actions/trial, ~16% failure rate;
  essentially zero at 1 g. Straddle-guided seat cuts UAI ~66% at lunar g.
- Guided workstation/circulation drive UTI ≈ 0 at all g while flat baselines
  destabilize below ~0.3–0.4 g.
- Lateral sliding door *increases* UTI vs hinged — direction matters; geometry
  is not generically better.
- Negative controls invariant (within MC noise).

## Hypothesis outcomes
- H1 (gravity-supplied stabilization declines): **supported** (Γ_T ∝ 1/g).
- H2 (UTI reduced): **supported** for guided/support-aligned variants.
- H3 (UAI reduced): **supported**, angular channel dominant for door/seat.
- H4 (benefit grows as g falls): **supported** — significant negative
  gravity×design interaction slopes.
- H5 (passive guidance substitutes for gravity stabilization): **supported**
  in model.
- H6 (cross-interface generalization): **supported** qualitatively across all
  five classes; quantitative transition points differ.

## Sensitivity
Ordering survives μ, m, f_u, t_react, force ±25%. Suit block (+40 kg,
restricted ROM) preserves interaction; absolute impulses scale with mass.

## Validation
Level A directional (parabolic-flight task performance/falls worsen as g falls);
Level B order-of-magnitude; Level C not attempted (no public transverse-impulse
dataset). Stated honestly in manuscript.

## Remaining limitations
Rigid-body occupant; prescribed task kinematics; Coulomb-type friction;
qualitative validation only; exploratory transition thresholds.

## File inventory
- manuscript/BUILDING_ENVIRONMENT_MAIN.docx, _inline.docx
- supplement/BUILDING_ENVIRONMENT_SUPPLEMENT.docx
- submission/ (manuscript, Highlights.docx, CoverLetter.docx, figures PNG,
  figures_editable.pptx, tables.docx, BUILDING_ENVIRONMENT_submission_FINAL.zip)
- src/, scripts/, tests/, results/, docs/, audit/, refs/

## Reproduce
```
cd gravity_momentum_design
make test        # 11/11 verification tests
make analysis    # ~7 min: sweep + MC + sensitivity + suit blocks
make figures stats manuscript submission
```

## Manual author-side actions
- Verify journal-level identifiers for refs 15, 23 in REFERENCE_AUDIT.
- Fill author metadata; confirm current B&E guide details at submission.
- Decide whether to expand the Discussion before submitting.

## Focused finishing-pass changes (2026-09-26)
1. Symbol/equation repair: docx text scanned — no corrupted or reordered
   symbols found; all math glyphs (μ, Γ_T, η_g, τ, β, ∝, ≤, −, ·) render in
   standard Unicode and are consistent across Methods, Results, captions,
   tables, supplement. No repairs needed beyond the corrections below.
2. B(g*) definitions: analysis code already computes per-channel
   B_UTI = 1 − UTI_red/UTI_conv and B_UAI = 1 − UAI_red/UAI_conv (masked where
   baseline < 1e-3). The manuscript Methods/caption text incorrectly said
   "UTI_red/UAI_conv"; corrected to match code and figure axes.
3. Interaction sign: model is slope β_g of
   log(impulse_redesign/impulse_conventional) vs g*. The reported β are
   positive and significant (door UAI +9.1, seat UTI +7.1, workstation UTI
   +19.7); text now says "significantly positive" and explains that a positive
   slope means the redesign advantage falls toward zero as g* → 1, i.e.
   relative benefit grows as g falls — H4 supported.
4. Structural zeros: near-zero UTI/UAI in guided variants are structural —
   residual demand (1−η)|F| falls below capacity in the idealized model;
   manuscript now states this explicitly ("approaches zero under perfect
   guidance") and does not present it as an empirical surprise.
5. Figures 1 and 4 redrawn cleanly (boxed flow diagram; per-class
   conventional vs momentum-aware panels with readable labels).
6. Added Discussion 4.6 "The gravity–inertia pair as a design regime"
   (calibrated future-implication paragraph).
7. Scientific result changes: one genuine defect fixed — the vectorized MC
   integrator kept counting corrective actions/momentum for failed trials
   while the single-trial simulator stops at failure; montecarlo.py now
   freezes failed trials consistently. MC summary values changed slightly
   (e.g. seat chair lunar: n_corr 4.1→3.8, UAI 16→13.6 N·m·s); all
   manuscript numbers regenerate from CSVs, so text stays consistent.
   Qualitative conclusions unchanged. Also added manuscript disclosure that
   seat redesigns change required demand itself (prevention mechanism).
8. Final manuscript: manuscript/BUILDING_ENVIRONMENT_MAIN.docx (+ _inline).
9. Final ZIP: submission/BUILDING_ENVIRONMENT_submission_FINAL.zip.

## Word-equation finishing pass (2026-09-26, second pass)
- All mathematical notation converted to native OMML equation objects
  (scripts/omml.py linear-syntax builder; 84 inline m:oMath elements:
  Greek+subscript Γ_T/τ_cap/η_g/β_g/F_perp/F_parallel/I_yaw/f_u/r_f/t_react,
  fractions Γ_T and B_UTI/B_UAI definitions, integral UTI definition,
  superscripts g*/H²/m², scaled delimiters for parens/brackets/|·|).
- Intra-paragraph hard line breaks removed (whitespace normalized at
  write time); no equation-induced empty paragraphs.
- Same treatment applied to supplement, highlights, cover letter, and
  tables.docx symbol cells (mu→μ, eta→η etc.).
- QA: BUILDING_ENVIRONMENT_MAIN_inline.docx exported to
  manuscript/BUILDING_ENVIRONMENT_MAIN_QA.pdf (13 pp) and every page
  visually inspected — equations render correctly, tables clean,
  figures legible. (PDF is a QA artifact only.)
- Analysis remained frozen; no scientific result changed in this pass.

## Figure/OMML finishing pass (2026-09-26, third pass)
- figures_editable.pptx: 0 → 8 native Office Math objects (a:m > m:oMathPara)
  across figure captions — F_parallel, F_perp, Γ_T fraction, B_UTI/B_UAI
  definitions, g* = g/g_Earth. Editable, schema-standard DrawingML math.
- All six figure PNGs regenerated with matplotlib mathtext labels
  (properly typeset Γ_T, g^*, F_⊥/F_∥, μ f_u N, η_g, B_UTI = 1 −
  UTI_red/UTI_conv, UTI/UAI integrals) — no malformed underscore notation
  in any raster label.
- tables.docx: header cells (g*(B≥0.5), g*(Γ_T≥1)) now OMML; body cells
  routed through the same rich writer.
- OMML counts: MAIN 84, inline 84, supplement 13, tables 4, pptx 8.
- Caveat: LibreOffice does not render DrawingML <a:m> math (viewer
  limitation); PowerPoint renders natively. Raster figure labels carry the
  typeset math, so submission PNGs are unaffected.
- Science frozen; figures redrawn from same data, no numeric change.
- Figure 5 x-axis label corrected to mathtext $g^* = g/g_{Earth}$ (matches
  Figures 3/6); no scientific result changed.
