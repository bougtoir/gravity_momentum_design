"""Main analysis pipeline: gravity sweep, Monte Carlo, convergence,
sensitivity, suit-load sensitivity. Writes results/tables/*.csv.

Usage: python scripts/run_analysis.py [--mc N]
"""
from __future__ import annotations

import argparse
import zlib
import numpy as np
import pandas as pd
import sys, os, time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.params import Occupant, sample_occupant, G_E, G_MOON, G_MARS
from src.mechanics import simulate
from src.montecarlo import simulate_batch, summarize
from src.cases import CASES, BASELINE

REF_G = [0.165, 0.25, 0.38, 0.5, 0.75, 1.0]
GRID = np.linspace(0.05, 1.0, 40)
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "results", "tables")
os.makedirs(OUT, exist_ok=True)


def deterministic_sweep():
    rows = []
    occ = Occupant()
    for case, (fn, variants) in CASES.items():
        for v in variants:
            rng = np.random.default_rng(12345)  # fixed seed per variant for sweep
            prof = fn(v, occ, rng)
            for g in GRID:
                r = simulate(prof, occ, g)
                rows.append(dict(case=case, variant=v, g_star=g,
                                 UTI=r.UTI, UAI=r.UAI,
                                 UTI_demand=r.UTI_demand, UAI_demand=r.UAI_demand,
                                 J_corr=r.J_corr, J_corr_ang=r.J_corr_ang,
                                 n_corr=r.n_corr, gamma_T=r.gamma_T,
                                 peak_F_perp=r.peak_F_perp, drift_x=r.drift_x,
                                 yaw_excursion=r.yaw_excursion,
                                 loss_of_support=r.loss_of_support,
                                 failed=int(r.failed)))
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUT, "gravity_sweep.csv"), index=False)
    return df


def monte_carlo(N: int, suit_mass: float = 0.0, restricted_rom: bool = False,
                tag=""):
    rows = []
    for case, (fn, variants) in CASES.items():
        for v in variants:
            for g in REF_G:
                # process-stable seeds (built-in hash() is salted per process)
                rng = np.random.default_rng(
                    zlib.crc32(f"{case}:{v}".encode()) % 2**32)
                occs = [sample_occupant(rng, suit_mass=suit_mass,
                                        restricted_rom=restricted_rom)
                        for _ in range(N)]
                rngp = np.random.default_rng(
                    zlib.crc32(f"{v}:{case}".encode()) % 2**32 + 1)
                profs = [fn(v, occs[i], rngp) for i in range(N)]
                arrs = simulate_batch(profs, occs, g)
                s = summarize(arrs)
                n_fail = int(np.sum(arrs["failed"]))
                rows.append(dict(case=case, variant=v, g_star=g, N=N,
                                 suit_mass=suit_mass, restricted_rom=restricted_rom,
                                 fail_rate=n_fail / N, **s))
    df = pd.DataFrame(rows)
    name = f"mc_summary{tag}.csv"
    df.to_csv(os.path.join(OUT, name), index=False)
    return df


def convergence(case="door", variant="hinged", g=0.38,
                Ns=(250, 500, 1000, 2000, 4000)):
    fn = CASES[case][0]
    rows = []
    for N in Ns:
        rng = np.random.default_rng(42)
        occs = [sample_occupant(rng) for _ in range(N)]
        rngp = np.random.default_rng(43)
        profs = [fn(variant, occs[i], rngp) for i in range(N)]
        arrs = simulate_batch(profs, occs, g)
        rows.append(dict(N=N, UTI_mean=arrs["UTI"].mean(),
                         UTI_p95=np.percentile(arrs["UTI"], 95),
                         UAI_mean=arrs["UAI"].mean(),
                         gamma_mean=arrs["gamma_T"].mean()))
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUT, "convergence.csv"), index=False)
    return df


def benefit_curves(sweep: pd.DataFrame):
    rows = []
    for case in sweep.case.unique():
        base = BASELINE[case]
        b = sweep[(sweep.case == case) & (sweep.variant == base)].set_index("g_star")
        for v in sweep[sweep.case == case].variant.unique():
            if v in (base, "neg_control"):
                continue
            d = sweep[(sweep.case == case) & (sweep.variant == v)].set_index("g_star")
            eps = 1e-3
            bu = b.UTI.reindex(d.index); ba = b.UAI.reindex(d.index)
            bj = b.J_corr.reindex(d.index)
            rows.append(pd.DataFrame(dict(
                case=case, variant=v, g_star=d.index,
                B_UTI=np.where(bu > eps, 1 - d.UTI / bu.clip(lower=1e-12), np.nan),
                B_UAI=np.where(ba > eps, 1 - d.UAI / ba.clip(lower=1e-12), np.nan),
                B_Jcorr=np.where(bj > eps, 1 - d.J_corr / bj.clip(lower=1e-12), np.nan),
            )))
    df = pd.concat(rows)
    df.to_csv(os.path.join(OUT, "benefit_curves.csv"), index=False)
    return df


def sensitivity(case="door", variant="hinged", g=0.38, N=1000):
    """One-at-a-time parameter sensitivity on the deterministic sim."""
    fn = CASES[case][0]
    rows = []
    base_occ = Occupant()

    def run(occ=None, prof_mod=None, tag="", val=None):
        o = occ or base_occ
        prof = fn(variant, o, np.random.default_rng(7))
        if prof_mod == "force_x1.5":
            prof.F_perp *= 1.5; prof.tau *= 1.5; prof.F_task *= 1.5
        r = simulate(prof, o, g)
        rows.append(dict(param=tag, value=val, UTI=r.UTI, UAI=r.UAI,
                         gamma_T=r.gamma_T, J_corr=r.J_corr))

    run(tag="baseline", val=0)
    for mu in (0.3, 0.5, 0.7):
        run(Occupant(mu=mu), tag="mu", val=mu)
    for m in (55, 75, 95):
        run(Occupant(m=m), tag="mass", val=m)
    for fu in (0.5, 0.68, 0.85):
        run(Occupant(fric_use=fu), tag="fric_use", val=fu)
    for tr in (0.3, 0.45, 0.6):
        run(Occupant(t_react=tr), tag="t_react", val=tr)
    run(prof_mod="force_x1.5", tag="force_scale", val=1.5)
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "sensitivity.csv"), index=False)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mc", type=int, default=2000)
    args = ap.parse_args()
    t0 = time.time()
    print("sweep..."); sw = deterministic_sweep()
    print("benefit..."); benefit_curves(sw)
    print(f"MC N={args.mc}..."); monte_carlo(args.mc)
    print("convergence..."); convergence()
    print("sensitivity..."); sensitivity()
    print("suit..."); monte_carlo(1000, suit_mass=40.0, tag="_suit40")
    print("restricted ROM..."); monte_carlo(1000, suit_mass=40.0,
                                          restricted_rom=True, tag="_suit40_rom")
    print(f"done in {time.time()-t0:.1f}s")
