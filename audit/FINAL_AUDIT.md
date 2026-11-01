# FINAL_AUDIT.md — internal consistency (Phase 14)

- Manuscript numbers all generated from results/tables/*.csv by
  scripts/make_manuscript.py — no hard-coded headline values; rerun pipeline to
  verify. ✓
- g values: Earth 1.000, Mars 0.38, Moon 0.165 used consistently in sweep, MC,
  figures, text. ✓
- Units: UTI [N·s], UAI [N·m·s], Γ_T [–], J_corr [N·s]. ✓
- Figures 1–6 cited in text and captions; Table 3 cell values = MC means. ✓
- Terminology: "partial gravity" used for 0.05–1 g; microgravity referenced
  only in the g→0 limit. ✓
- Negative control verified numerically (UTI/UAI within MC noise of baseline). ✓
- Automated verification: 11/11 pytest tests pass. ✓
- Remaining known limitations listed in Discussion 4.7 and EXTERNAL_VALIDATION.

## Addendum — finishing pass
- Corrected B(g*) manuscript text to match code (B_UTI, B_UAI per channel,
  masked below 1e-3 baseline).
- Fixed sign wording: interaction β_g are significantly positive, correctly
  interpreted as benefit growing as g falls (H4 supported).
- montecarlo.py now matches simulate() failure semantics (freeze failed
  trials; no post-failure correction counting). All downstream tables,
  figures, manuscript numbers and the submission ZIP were regenerated.
- Seat-variant demand difference disclosed in text (prevention = demand
  elimination, reported with raw demand integrals).
- Exact-zero guided-variant results documented as structural consequences of
  idealized perfect guidance, not empirical findings.

## Addendum 2 — Word equation pass
A. Equation repair: all compound math (Γ_T, τ_cap, η_g, β_g, F_perp,
   F_parallel, I_yaw, f_u, r_f, t_react, x_free, J_corr, g*, g_Earth, B_UTI,
   B_UAI, H², m², R², distribution expressions, UTI integral, Γ_T and
   B-fractions) converted to native OMML m:oMath inline equations
   (scripts/omml.py). Bare isolated symbols and acronyms (UTI, UAI, N, m, g)
   remain as text where unambiguous, per spec. 84 equation objects; valid
   OMML (sSub/sSup/f/d/nary nodes); Cambria Math referenced, no embedded fonts.
B. Line cleanup: intra-paragraph newlines (hard line-break artifacts)
   normalized to flowing text; zero equation-induced empty paragraphs.
C. Visual QA: 13-page PDF (manuscript/BUILDING_ENVIRONMENT_MAIN_QA.pdf)
   inspected page by page — subscripts, fractions, integral, delimiters all
   render correctly; Tables 1–4 and Figures 1–6 clean.
D. Scientific freeze: no analysis rerun; no numeric change.
E. Paths: manuscript/BUILDING_ENVIRONMENT_MAIN.docx (+ _inline.docx,
   _QA.pdf); submission/BUILDING_ENVIRONMENT_submission_FINAL.zip.

## Addendum 3 — Office Math / figure equation audit
1. OMML object counts (before→after): MAIN.docx 84→84, inline 84→84,
   SUPPLEMENT 13→13, tables.docx 2→4, figures_editable.pptx 0→8.
2. PPTX math added to captions of Figures 2 (F_parallel, F_perp), 3 (Γ_T,
   g*, g_Earth), 5 (B_UTI(g*), B_UAI(g*) definitions), 6 (Γ_T); figs 1,4
   captions contain no structured math.
3. In-figure math labels are rasterized by design (matplotlib mathtext):
   axis/annotation labels now use proper math typesetting instead of
   literal underscore text; PNGs verified pixel-rendered.
4. All pptx equation objects are live a:m/m:oMathPara — editable, no
   images, no fake subscripts.
5. tables.docx gained OMML in g*(...) headers; body cells audited —
   numbers/units only, plus g*/Γ_T where present.
6. No equation-induced paragraph breaks introduced; pptx captions keep
   math inline via a:m.
7. Visual QA: all 6 PNGs inspected (mathtext correct, no overlaps after
   fig2 caption fix); pptx→PDF inspected slide-by-slide — LO does not
   render a:m (documented limitation); docx PDF QA from prior pass stands.
8. No scientific analysis/results changed.
9. Final ZIP: submission/BUILDING_ENVIRONMENT_submission_FINAL.zip.
- Figure 5 x-axis label corrected to mathtext $g^* = g/g_{Earth}$; ZIP rebuilt.
