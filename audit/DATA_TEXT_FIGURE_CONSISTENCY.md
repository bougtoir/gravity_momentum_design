# DATA_TEXT_FIGURE_CONSISTENCY.md — canonical cross-check (post-seed-fix run)

All manuscript numbers are generated from results/tables/*.csv by
make_manuscript.py / make_stats.py; none typed. Verified rebuilt values:

| Claim | Text | Source | Match |
|-------|------|--------|-------|
| door UAI increase Earth→Moon | ~2153× | mc_summary door/hinged 0.165/1.0 UAI (7.410/0.00344) | yes |
| seat corrective actions @Moon | 3.8 (Earth 0.02) | mc_summary seat/chair n_corr_mean | yes |
| seat failure rate | 16% | seat/chair fail_rate 0.1645 | yes |
| straddle-seat UAI reduction | ~99% | 0.095 vs 13.554 N·m·s | yes |
| workstation UTI @Moon | 2.47 → 0.00 N·s | flat vs guided UTI (2.470, 0.0) | yes |
| lateral-slide vs hinged UTI | 7.25 vs 0.69 N·s | mc_summary door Moon | yes |
| interaction β (dominant channels) | 9.2 / 7.2 / 19.9 | interaction.csv | yes |
| negative control | within MC noise (7.48 vs 7.41) | door neg_control UAI | yes |
| transitions B≥0.5 | 0.10–0.37 | transitions.csv g_benefit50 | yes (computed) |
| Γ_T=1 crossing, lateral slide | ~0.20 g | gravity_sweep.csv | yes (computed; was wrongly "~0.4") |
| conventional max crossing | ~0.37 g | seat chair crossing | yes (computed; was "~0.4") |
| Table 3 cells | — | generated from mc_summary rows | yes |
| Table 4 cells | — | generated from sensitivity.csv | yes |
| Figures 3/5/6 | — | plotted from same CSVs | yes |

Consistency across artifacts: Abstract, §3.x Results, Tables, Highlights use
the same CSV-derived quantities; supplement S1–S9 reference the same files.

Result: PASS (all quantitative statements trace to generated outputs).
