# REFERENCE_CITATION_AUDIT.md

Style check: Building and Environment uses the Elsevier numbered style
(CSL dependent style → elsevier-with-titles; citations as [n], list ordered by
first appearance).

Build mechanism: body text uses {cite:Key} tokens; scripts/make_manuscript.py
resolve_citations() assigns numbers in strict first-appearance order and fails
the build on any undefined key or uncited reference (fail-loud).

Verified on the built BUILDING_ENVIRONMENT_MAIN.docx:
- body citation groups in reading order:
  [1,2,3,4], [5,6,7,8], [9], [10,11], [12], [13,14], [15,16,17], [18,19],
  [20,21], [22], [23,24,25]
- first appearance of each key is monotonically increasing: 1→25, no gaps,
  no duplicates, no reverse-order first citation.
- every bibliography item (1–25) is cited in the body; every body citation
  resolves to a bibliography item. No orphan references, no [Key]-form
  placeholders remain (the [Newman1992; Richter2017; Macaulay2024]
  placeholder was replaced).
- note: "[50,110]" appearing in §2.4 is the mass truncation range, not a
  citation.

Result: PASS.
