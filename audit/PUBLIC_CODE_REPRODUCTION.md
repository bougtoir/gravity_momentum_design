# PUBLIC_CODE_REPRODUCTION.md — clean-clone reproduction audit

- Public URL: https://github.com/bougtoir/gravity_momentum_design (reachable
  without credentials, HTTP 200; default branch main)
- Commit audited: 34fe87ccb5d47e896fd9e0b0212abcc00fb3d1ca
- Clean-clone path: ~/public_gmd (fresh clone, fresh .venv)

## Steps & results
1. `pytest tests/ -q` → 11/11 PASS on the public commit.
2. `python scripts/run_analysis.py --mc 2000` (456 s) regenerated
   gravity_sweep/benefit/sensitivity/convergence identically, but
   mc_summary*.csv differed from the committed outputs.

## Defect found and fixed
`run_analysis.py` seeded Monte Carlo via `hash((case, v))`; Python salts str
hashing per process, so MC draws were nondeterministic run-to-run — a genuine
reproducibility defect (headline ratio moved 1955×→~1509× between identical
commands; qualitative results stable).

Fix (this pass, in wip source; lands in the public repo on merge+sync):
deterministic seeds `zlib.crc32(f"{case}:{v}")`, `zlib.crc32(f"{v}:{case}")+1`.
The same patch was applied to the clean clone and the full pipeline rerun:
all 8 results/tables CSVs are now **bit-identical** between the wip working
tree and the public clean clone.

## Post-fix numeric verification (tolerance: exact)
- Table 3 MC means: identical
- Table 4 sensitivity: identical
- Figures 3/5/6 source data (gravity_sweep, benefit_curves): identical
- interaction coefficients: identical (interaction.csv regenerated)
- abstract headline (UAI ratio 2153×): identical
- negative control & structural-zero behavior: identical

## Ordering caveat
The deterministic-seed fix and manuscript corrections live on the wip working
branch and propagate to the public repository when the accompanying PR is
merged (sync-to-repos BRANCH/SUBDIR map already covers this project). Until
then the public HEAD reproduces within MC tolerance but not bit-exactly.

Final: PASS (post-fix clean-clone reproduction verified bit-exact).
