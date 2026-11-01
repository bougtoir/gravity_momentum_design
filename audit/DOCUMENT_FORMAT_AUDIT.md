# DOCUMENT_FORMAT_AUDIT.md

Scan of all Word artifacts in submission/ (word/document.xml):
- w:br manual line breaks: 0 in every file (MAIN, inline, supplement, tables,
  CoverLetter, Highlights).
- Empty non-math paragraphs: 0 in MAIN and inline.
- No repeated-space layout or character-count wrapping found; the docx builders
  emit one paragraph per logical block and rely on Word layout for wrapping.
- Table cells contain short structured text only (allowed).
- markdown "*" remnants: 0 across all six files (emphasis converted to real
  italic runs: "after", "angular", "increases" verified italic in MAIN).

Result: PASS.
