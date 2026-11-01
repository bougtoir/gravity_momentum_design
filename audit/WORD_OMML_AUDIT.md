# WORD_OMML_AUDIT.md — preservation audit

OMML object counts in the rebuilt package (word/document.xml scan):
- BUILDING_ENVIRONMENT_MAIN.docx: 84 inline OMML expressions
- BUILDING_ENVIRONMENT_MAIN_inline.docx: 84
- BUILDING_ENVIRONMENT_SUPPLEMENT.docx: 13
- tables.docx: 4 (header symbols)
- Highlights.docx: 1; CoverLetter.docx: 0 (no math expected)
- figures_editable.pptx: native a:m Office Math in slide captions —
  slides 2,3,5,6 carry 2/3/2/1 a:m elements respectively (fig1/fig4 captions
  contain no compound math), preserved.

Raster figures: mathtext labels (Γ_T, g*, B_UTI etc.) render
subscripts/superscripts correctly; fig5 xlabel fixed in prior pass.

No regression to underscore notation: source uses ⟦...⟧ linear math parsed to
native OMML; plain-text fallback only for non-math prose.

Result: PASS.
