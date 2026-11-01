"""Core rigid-body occupant–interface mechanics.

Implements the frozen model of docs/MODEL_SPECIFICATION.md:
- gravity-supplied friction/normal capacities scale with g;
- interface reactions decompose into task-relevant (F_parallel) and
  task-irrelevant transverse (F_perp) parts;
- excess over capacity generates transverse/angular momentum (UTI/UAI);
- corrective actions arrest accumulated momentum after a reaction delay.
"""
from __future__ import annotations

import numpy as np
from dataclasses import dataclass
from .params import Occupant, G_E


@dataclass
class ReactionProfile:
    """Time series of reaction on the occupant during a task.

    t:        (n,) time [s]
    F_perp:   (n,) signed transverse reaction demand [N] (signed along +x_perp)
    R_v:      (n,) vertical reaction on occupant, +down adds to N [N]
    tau:      (n,) yaw torque demand about COM vertical axis [N·m]
    guide_eta:(n,) passive-guide fraction absorbing transverse demand [0,1]
    guide_tau:(n,) passive-guide fraction for torque [0,1]
    F_task:   (n,) task force magnitude (for useful-work accounting) [N]
    """
    t: np.ndarray
    F_perp: np.ndarray
    R_v: np.ndarray
    tau: np.ndarray
    guide_eta: np.ndarray
    guide_tau: np.ndarray
    F_task: np.ndarray


@dataclass
class SimResult:
    UTI: float            # N·s, transverse impulse acquired by body
    UAI: float            # N·m·s, angular impulse acquired
    UTI_demand: float     # N·s, raw transverse impulse demand (pre-capacity)
    UAI_demand: float
    J_corr: float         # N·s corrective impulse (transverse)
    J_corr_ang: float     # N·m·s corrective angular impulse
    n_corr: int           # corrective actions
    peak_F_perp: float    # N
    peak_v_perp: float    # m/s
    drift_x: float        # m
    yaw_excursion: float  # rad
    task_time: float      # s
    useful_work: float    # J
    gamma_T: float        # max F_perp/(mu m g)
    loss_of_support: int  # count of timesteps with N < threshold
    failed: bool
    traces: dict | None = None


def simulate(profile: ReactionProfile, occ: Occupant, g_star: float,
             record: bool = False) -> SimResult:
    g = g_star * G_E
    t = profile.t
    dt = np.diff(t, prepend=t[0])
    n = len(t)

    m = occ.m_eff
    v_perp = np.zeros(n)
    x_perp = np.zeros(n)
    omega = np.zeros(n)
    theta = np.zeros(n)

    F_perp_excess = np.zeros(n)
    tau_excess = np.zeros(n)
    N = np.zeros(n)
    corr_flags = np.zeros(n, bool)
    los = 0
    J_corr = J_corr_ang = 0.0
    n_corr = 0
    t_last_corr = -np.inf
    failed = False

    x_margin = occ.x_margin
    th_margin = occ.theta_margin
    # restricted ROM reduces correction speed: scale margins by rom_factor
    x_margin_eff = x_margin * occ.rom_factor

    for i in range(n):
        Nv = m * g + profile.R_v[i]
        if Nv < 0.05 * m * g:
            los += 1
        Nv = max(Nv, 0.0)
        N[i] = Nv
        F_cap = occ.mu * occ.fric_use * Nv
        tau_cap = occ.mu * occ.fric_use * Nv * occ.r_f

        # passive guidance absorbs fraction eta of the demand; the residual
        # must be supplied by friction (capacity) or becomes body momentum
        ex = abs(profile.F_perp[i]) * (1.0 - profile.guide_eta[i]) - F_cap
        F_perp_excess[i] = np.sign(profile.F_perp[i]) * max(ex, 0.0)
        tex = abs(profile.tau[i]) * (1.0 - profile.guide_tau[i]) - tau_cap
        tau_excess[i] = np.sign(profile.tau[i]) * max(tex, 0.0)

    # integrate
    for i in range(1, n):
        v_perp[i] = v_perp[i - 1] + F_perp_excess[i] / m * dt[i]
        x_perp[i] = x_perp[i - 1] + v_perp[i] * dt[i]
        omega[i] = omega[i - 1] + tau_excess[i] / occ.I_yaw * dt[i]
        theta[i] = theta[i - 1] + omega[i] * dt[i]

        if ((abs(x_perp[i]) > x_margin_eff or abs(theta[i]) > th_margin)
                and (t[i] - t_last_corr) > occ.t_react):
            corr_flags[i] = True
            n_corr += 1
            t_last_corr = t[i]
            J_corr += m * abs(v_perp[i])
            J_corr_ang += occ.I_yaw * abs(omega[i])
            v_perp[i] = 0.0
            omega[i] = 0.0
            x_perp[i] = np.clip(x_perp[i], -x_margin_eff, x_margin_eff)
            theta[i] = np.clip(theta[i], -th_margin, th_margin)

        if abs(x_perp[i]) > 2.0 * x_margin:
            failed = True
            break

    T = t[-1] - t[0]
    UTI = float(np.sum(np.abs(F_perp_excess) * dt))
    UTI_demand = float(np.sum(np.abs(profile.F_perp) * dt))
    UAI = float(np.sum(np.abs(tau_excess) * dt))
    UAI_demand = float(np.sum(np.abs(profile.tau) * dt))
    # residual momentum arrest at task end counts as corrective
    J_corr += m * abs(v_perp[-1])
    J_corr_ang += occ.I_yaw * abs(omega[-1])

    denom = occ.mu * occ.fric_use * m * g
    gamma_T = float(np.max(np.abs(profile.F_perp)) / denom) if denom > 0 else np.inf
    # task impulse proxy; per-case useful work is normalized at profile level
    useful_work = float(np.sum(profile.F_task) * np.mean(dt))

    out = SimResult(
        UTI=UTI, UAI=UAI, UTI_demand=UTI_demand, UAI_demand=UAI_demand,
        J_corr=J_corr, J_corr_ang=J_corr_ang, n_corr=n_corr,
        peak_F_perp=float(np.max(np.abs(profile.F_perp))),
        peak_v_perp=float(np.max(np.abs(v_perp))),
        drift_x=float(x_perp[-1]), yaw_excursion=float(theta[-1]),
        task_time=T, useful_work=useful_work, gamma_T=gamma_T,
        loss_of_support=los, failed=failed,
    )
    if record:
        out.traces = dict(t=t, F_perp=profile.F_perp, F_excess=F_perp_excess,
                          tau=profile.tau, tau_excess=tau_excess, N=N,
                          x_perp=x_perp, v_perp=v_perp, theta=theta,
                          omega=omega, corr=corr_flags)
    return out


def bell(t: np.ndarray, t0: float, t1: float) -> np.ndarray:
    """Half-sine bell over [t0,t1], zero elsewhere; peak = 1."""
    w = np.zeros_like(t)
    m = (t >= t0) & (t <= t1)
    w[m] = np.sin(np.pi * (t[m] - t0) / (t1 - t0))
    return w
