"""Statistical synthesis (Phase 8-9): gravity×design interaction on log UTI/UAI,
design-transition gravity estimates. Writes results/tables/interaction.csv and
transitions.csv."""
import os, sys
import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAB = os.path.join(ROOT, "results", "tables")

mc = pd.read_csv(os.path.join(TAB, "mc_summary.csv"))

rows = []
for case in mc.case.unique():
    d = mc[mc.case == case]
    base = d[d.variant == {"door": "hinged", "seat": "chair", "control": "lateral_lever",
                           "workstation": "flat", "stairs": "conventional"}[case]]
    alts = d[~d.variant.isin(list(base.variant) + ["neg_control"])]
    for v in alts.variant.unique():
        dv = alts[alts.variant == v]
        for metric in ("UTI_mean", "UAI_mean"):
            y = np.log(dv[metric].values + 1e-6) - np.log(
                base[metric].values + 1e-6)
            g = dv.g_star.values
            X = sm.add_constant(g)
            fit = sm.OLS(y, X).fit()
            rows.append(dict(case=case, variant=v, metric=metric,
                             beta_g=fit.params[1], beta_g_p=fit.pvalues[1],
                             R2=fit.rsquared))
interaction = pd.DataFrame(rows)
interaction.to_csv(os.path.join(TAB, "interaction.csv"), index=False)

# Transition gravities: lowest g* where benefit first exceeds 0.5 (sweep data)
sw = pd.read_csv(os.path.join(TAB, "gravity_sweep.csv"))
ben = pd.read_csv(os.path.join(TAB, "benefit_curves.csv"))
rows = []
BASE = {"door": "hinged", "seat": "chair", "control": "lateral_lever",
        "workstation": "flat", "stairs": "conventional"}
EPS = 1e-3  # N·s: benefit undefined where baseline burden ~0
for (case, v), grp in ben.groupby(["case", "variant"]):
    grp = grp.sort_values("g_star", ascending=False)
    base_sw = sw[(sw.case == case) & (sw.variant == BASE[case])].set_index("g_star")
    valid = base_sw.UTI.reindex(grp.g_star) > EPS
    hit = grp[(grp.B_UTI >= 0.5) & valid.values]
    g_tr = hit.g_star.max() if len(hit) else np.nan
    # Γ_T crossing for baseline
    bd = sw[(sw.case == case) & (sw.variant ==
            {"door": "hinged", "seat": "chair", "control": "lateral_lever",
             "workstation": "flat", "stairs": "conventional"}[case])]
    cross = bd[bd.gamma_T >= 1.0]
    g_cap = cross.g_star.max() if len(cross) else np.nan
    rows.append(dict(case=case, variant=v, g_benefit50=g_tr,
                     g_baseline_Gamma1=g_cap))
pd.DataFrame(rows).to_csv(os.path.join(TAB, "transitions.csv"), index=False)
print(interaction.round(3).to_string(index=False))
print(pd.read_csv(os.path.join(TAB, "transitions.csv")).round(3).to_string(index=False))
