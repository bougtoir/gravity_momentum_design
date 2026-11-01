# Supplement Integration Audit — BUILDING_ENVIRONMENT_MAIN_SUPPLEMENT_INTEGRATED.docx

Sources (uploaded, authoritative):
- manuscript_author.docx
- BUILDING_ENVIRONMENT_SUPPLEMENT.docx

Built by `scripts/integrate_supplement.py` (document surgery on the uploaded
files; no regeneration, no re-run of analyses).

## 1. S1–S10 → final-manuscript mapping

| Supp | Content | Integrated at | Form |
|------|---------|---------------|------|
| S1 | Extended MC summaries (mc_summary, suit40, rom) | §2.7 appended sentence | prose + public-repo CSV pointer |
| S2 | Design-transition estimates | §3.6 "Table 4" (was "Table S2") | prose + Table 4 |
| S3 | Sensitivity sweep | §2.11 / §3.9 appended sentence | prose + CSV pointer (Table 5 already reports it) |
| S4 | Convergence diagnostics | §2.7 appended sentence | prose + CSV pointer |
| S5 | Interaction model | §2.8 appended sentence | prose + CSV pointer |
| S6 | Gravity-sweep grid / benefit curves | §2.6 appended sentence | prose + CSV pointer |
| S7 | Negative-control detail | §3.1 appended sentence | prose (~3% UAI agreement) |
| S8 | Falsification criteria A–F | §3.8 appended sentence | prose (none rejected; B≈0 at 1 g; cross-interface) |
| S9 | Trade-offs / Pareto | §4.4 "(Supplement)" removed, full content appended | prose with OMML (x_free, η) |
| S10 | Full transition table | after §3.6 | new main-text Table 4 (12 rows, verbatim) |

## 2. Figures (number · first-citation paragraph · inline location)

| Fig | First cited | Placed after |
|-----|-------------|--------------|
| 1 | §1.4 | same paragraph, image then caption |
| 2 | §2.1 | same paragraph, image then caption |
| 3 | §3.3 | same paragraph, image then caption |
| 4 | §3.4 | same paragraph, image then caption |
| 5 | §3.6 | same paragraph (before Table 4, matching mention order) |
| 6 | §4.5 | same paragraph, image then caption |

## 3. Tables (number · source · first-citation · inline location)

| Table | Source | First cited | Placed after |
|-------|--------|-------------|--------------|
| 1 | main | §2.4 | §2.4 paragraph |
| 2 | main | §2.5 | §2.5 paragraph |
| 3 | main | §3.2 | §3.2 paragraph |
| 4 | Supplement S10 (new) | §3.6 | §3.6 paragraph (after Figure 5, matching mention order) |
| 5 | main (was Table 4, renumbered) | §3.9 | §3.9 paragraph |

## 4. Numbering follows first appearance — confirmed
Figures: 1→2→3→4→5→6. Tables: 1→2→3→4→5. No gaps, no duplicates, no inversion.

## 5. Same-paragraph multi-object order — confirmed
§3.6 mentions Figure 5 then Table 4; document order is Figure 5, caption, Table 4 title, Table 4.

## 6. Terminal "Tables" section deleted — confirmed (Heading 1 "Tables" removed).
## 7. Terminal "Figure captions" section deleted — confirmed.
## 8. All Supplement references removed — confirmed
Zero matches for "Supplement", "supplement", "Table S", "Figure S" in the output.
Four stale pointers rewritten: §2.10 "(see Supplement)" removed; §3.4 raw-demand
pointer → public-repository CSV; §3.6 "Table S2" → "Table 4"; §4.4 "(Supplement)"
→ integrated S9 content.

## 9. No scientific information from S1–S10 lost — confirmed
All ten items represented (see §1). Raw grids retained as public-repo CSV
pointers per the "no raw data dump" rule; the transition table is verbatim.

## 10. No scientific numerical result changed — confirmed
Body numbers untouched; only connective prose, pointers and placement changed.

## 11. Page count: 16 pages (QA PDF).
## 12. Word count: ~3,771 words (paragraph + table text).

## Other checks
- All 25 references intact, numbered [1]–[25]; no new references.
- OMML preserved: 100 inline equations; new prose uses OMML (g*, Γ_T, B_UTI, x_free, η, R²).
- Zero Markdown "*"; only structural w:br in the title/affiliation block.
- QA PDF visually inspected (16 pages): figures+tables inline, captions attached, no stray end sections.
