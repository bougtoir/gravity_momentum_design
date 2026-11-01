"""Vectorized Monte Carlo integrator: same equations as mechanics.simulate,
but integrates N trials simultaneously (timestep loop, vector ops across trials).

All profiles in one batch must share the same t grid (per case they do).
"""
from __future__ import annotations

import numpy as np
from .params import Occupant, G_E
from .mechanics import ReactionProfile


def simulate_batch(profiles: list[ReactionProfile], occs: list[Occupant],
                   g_star: float) -> dict[str, np.ndarray]:
    nt = len(profiles)
    t = profiles[0].t
    n = len(t)
    dt = t[1] - t[0]
    g = g_star * G_E

    F_perp = np.stack([p.F_perp for p in profiles])        # nt x n
    R_v = np.stack([p.R_v for p in profiles])
    tau = np.stack([p.tau for p in profiles])
    eta = np.stack([p.guide_eta for p in profiles])
    eta_t = np.stack([p.guide_tau for p in profiles])

    m = np.array([o.m_eff for o in occs])
    mu = np.array([o.mu for o in occs])
    fu = np.array([o.fric_use for o in occs])
    rf = np.array([o.r_f for o in occs])
    Iy = np.array([o.I_yaw for o in occs])
    xm = np.array([o.x_margin * o.rom_factor for o in occs])
    thm = np.array([o.theta_margin for o in occs])
    tre = np.array([o.t_react for o in occs])

    v = np.zeros(nt); x = np.zeros(nt)
    w = np.zeros(nt); th = np.zeros(nt)
    UTI = np.zeros(nt); UAI = np.zeros(nt)
    UTI_d = np.zeros(nt); UAI_d = np.zeros(nt)
    Jc = np.zeros(nt); Jca = np.zeros(nt)
    ncorr = np.zeros(nt, int); tlc = np.full(nt, -1e9)
    los = np.zeros(nt, int); failed = np.zeros(nt, bool)
    peakF = np.abs(F_perp).max(axis=1)
    peak_v = np.zeros(nt)

    for i in range(n):
        Nv = m * g + R_v[:, i]
        los += (Nv < 0.05 * m * g)
        Nv = np.maximum(Nv, 0.0)
        Fcap = mu * fu * Nv
        tcap = mu * fu * Nv * rf
        Fex = np.sign(F_perp[:, i]) * np.maximum(
            np.abs(F_perp[:, i]) * (1.0 - eta[:, i]) - Fcap, 0.0)
        tex = np.sign(tau[:, i]) * np.maximum(
            np.abs(tau[:, i]) * (1.0 - eta_t[:, i]) - tcap, 0.0)
        UTI += np.abs(Fex) * dt
        UTI_d += np.abs(F_perp[:, i]) * dt
        UAI += np.abs(tex) * dt
        UAI_d += np.abs(tau[:, i]) * dt
        v += Fex / m * dt
        x += v * dt
        w += tex / Iy * dt
        th += w * dt
        peak_v = np.maximum(peak_v, np.abs(v))
        need = ((np.abs(x) > xm) | (np.abs(th) > thm)) & ~failed
        ok = need & (t[i] - tlc > tre)
        if ok.any():
            ncorr += ok
            tlc[ok] = t[i]
            Jc += m * np.abs(v) * ok
            Jca += Iy * np.abs(w) * ok
            v[ok] = 0.0; w[ok] = 0.0
            x[ok] = np.clip(x[ok], -xm[ok], xm[ok])
            th[ok] = np.clip(th[ok], -thm[ok], thm[ok])
        failed |= np.abs(x) > 2.0 * np.array([o.x_margin for o in occs])
        # failed trials stop accumulating momentum and corrections, matching
        # mechanics.simulate which breaks on failure
        if failed.any():
            v[failed] = 0.0
            w[failed] = 0.0

    Jc += m * np.abs(v)
    Jca += Iy * np.abs(w)
    denom = mu * fu * m * g
    gamma_T = np.where(denom > 0, peakF / denom, np.inf)

    return dict(UTI=UTI, UAI=UAI, UTI_demand=UTI_d, UAI_demand=UAI_d,
                J_corr=Jc, J_corr_ang=Jca, n_corr=ncorr,
                peak_F_perp=peakF, peak_v_perp=peak_v,
                drift_x=x, yaw_excursion=th,
                gamma_T=gamma_T, loss_of_support=los, failed=failed)


def summarize(arrs: dict[str, np.ndarray], prefix="") -> dict[str, float]:
    """Mean [CI lo, hi] for each metric; returns flat dict for CSV."""
    out = {}
    for k, v in arrs.items():
        if not np.issubdtype(v.dtype, np.floating):
            v = v.astype(float)
        out[f"{prefix}{k}_mean"] = float(np.mean(v))
        out[f"{prefix}{k}_p5"] = float(np.percentile(v, 5))
        out[f"{prefix}{k}_p95"] = float(np.percentile(v, 95))
    return out
