"""Canonical interface cases — ReactionProfile generators.

Each variant produces a force/torque demand profile on the occupant.
Variants are mechanically normalized (same useful task impulse/work proxy,
same task time) as specified in docs/MODEL_SPECIFICATION.md §6.
"""
from __future__ import annotations

import numpy as np
from .params import Occupant, jitter
from .mechanics import ReactionProfile, bell

DT = 0.001


def _profile(T, **kw):
    t = np.arange(0.0, T + DT / 2, DT)
    zeros = np.zeros_like(t)
    return t, ReactionProfile(
        t=t,
        F_perp=kw.get("F_perp", zeros.copy()),
        R_v=kw.get("R_v", zeros.copy()),
        tau=kw.get("tau", zeros.copy()),
        guide_eta=kw.get("guide_eta", zeros.copy()),
        guide_tau=kw.get("guide_tau", zeros.copy()),
        F_task=kw.get("F_task", zeros.copy()),
    )


# ------------------------------------------------------------------ Case 1: door
def door(variant: str, occ: Occupant, rng) -> ReactionProfile:
    """Open door over T=2 s. Peak task force ~32 N (22 N operating + 10 N latch)."""
    T = 2.0
    t = np.arange(0.0, T + DT / 2, DT)
    F_peak = jitter(rng, 45.0, 0.25)  # hatch/door operating + latch force
    # latch spike + sustained operating force
    F_task = F_peak * (bell(t, 0.0, 0.3) * 1.4 + bell(t, 0.1, 2.0))
    h_a = 1.0  # handle height ~ lever arm for yaw torque about feet->COM axis
    # lever arm for body yaw: force at handle height vs COM height -> use (h_a - h_c)? per spec: tau = F_perp * h_a
    if variant == "hinged":
        # pull arc: transverse reaction fraction grows with door angle
        frac = 0.35 + 0.55 * np.clip(t / T, 0, 1)  # φ_s from ~20° to ~55°
        F_perp = F_task * frac
        tau = F_perp * (h_a - 0.5 * occ.h_c) * 0.8
        p = ReactionProfile(t, F_perp=F_perp, R_v=np.zeros_like(t), tau=tau,
                            guide_eta=np.zeros_like(t), guide_tau=np.zeros_like(t),
                            F_task=F_task)
    elif variant == "lateral_slide":
        F_perp = F_task * 0.95
        tau = F_perp * 0.1  # small, at waist height
        p = ReactionProfile(t, F_perp=F_perp, R_v=np.zeros_like(t), tau=tau,
                            guide_eta=np.zeros_like(t), guide_tau=np.zeros_like(t),
                            F_task=F_task)
    elif variant == "vertical_guided":
        # lift along gravity axis: adds to normal; small residual misalignment
        resid = jitter(rng, 0.05, 0.4)
        F_perp = F_task * resid
        R_v = F_task * 0.9  # downward-aligned lift adds to normal force demand
        eta = np.full_like(t, 0.9)
        tau = np.zeros_like(t)
        p = ReactionProfile(t, F_perp=F_perp, R_v=R_v, tau=tau,
                            guide_eta=eta, guide_tau=np.zeros_like(t), F_task=F_task)
    elif variant == "neg_control":
        # restyled hinged door: identical mechanics
        frac = 0.35 + 0.55 * np.clip(t / T, 0, 1)
        F_perp = F_task * frac
        tau = F_perp * (h_a - 0.5 * occ.h_c) * 0.8
        p = ReactionProfile(t, F_perp=F_perp, R_v=np.zeros_like(t), tau=tau,
                            guide_eta=np.zeros_like(t), guide_tau=np.zeros_like(t),
                            F_task=F_task)
    else:
        raise ValueError(variant)
    return p


# ------------------------------------------------------------------ Case 2: seat ingress
def seat(variant: str, occ: Occupant, rng) -> ReactionProfile:
    """Ingress over T=3 s along prescribed COM path.

    Conventional chair: yaw turn Δψ~150° + arc translation -> centripetal F_perp
    and yaw torque. Linear/straddle: near-straight path, geometry captures.
    """
    T = 3.0
    t = np.arange(0.0, T + DT / 2, DT)
    m = occ.m_eff
    I = occ.I_yaw
    v_char = jitter(rng, 0.8, 0.2) * occ.rom_factor  # m/s path speed

    if variant == "chair":
        dpsi = np.radians(150.0)
        r_path = 0.45
        turn_mask = (t >= 0.5) & (t <= 2.0)
        # centripetal reaction during turn
        F_perp = np.zeros_like(t)
        F_perp[turn_mask] = m * v_char ** 2 / r_path
        # plus lateral settle shift
        F_perp += (m * v_char * 0.4) * bell(t, 1.8, 3.0)
        # yaw torque profile to achieve Δψ over the turn (bang-bang angular accel)
        dur = 1.5
        w_peak = dpsi / (dur / 2)  # triangular yaw rate
        tau = np.zeros_like(t)
        half = dur / 2
        inturn = (t >= 0.5) & (t < 0.5 + dur)
        tt = t[inturn] - 0.5
        tau[inturn] = I * (w_peak / half) * np.where(tt < half, 1.0, -1.0)
        eta = np.zeros_like(t)
    elif variant == "linear":
        dpsi = np.radians(20.0)
        F_perp = (m * v_char * 0.25) * bell(t, 1.0, 3.0)
        dur = 0.8
        w_peak = dpsi / (dur / 2)
        tau = np.zeros_like(t)
        inturn = (t >= 1.0) & (t < 1.0 + dur)
        tt = t[inturn] - 1.0
        tau[inturn] = I * (w_peak / (dur / 2)) * np.where(tt < dur / 2, 1.0, -1.0)
        eta = np.zeros_like(t)
    elif variant == "straddle":
        F_perp = (m * v_char * 0.08) * bell(t, 1.0, 3.0)
        dur = 0.4
        dpsi = np.radians(10.0)
        w_peak = dpsi / (dur / 2)
        tau = np.zeros_like(t)
        inturn = (t >= 1.2) & (t < 1.2 + dur)
        tt = t[inturn] - 1.2
        tau[inturn] = I * (w_peak / (dur / 2)) * np.where(tt < dur / 2, 1.0, -1.0)
        eta = np.zeros_like(t)
        eta[t > 0.8] = 0.85  # geometric capture once engaged
    else:
        raise ValueError(variant)
    F_task = np.abs(F_perp) + np.abs(tau) * 0.1
    return ReactionProfile(t, F_perp=F_perp, R_v=np.zeros_like(t), tau=tau,
                           guide_eta=eta, guide_tau=eta * 0.8, F_task=F_task)


# ------------------------------------------------------------------ Case 3: control
def control(variant: str, occ: Occupant, rng) -> ReactionProfile:
    """Deliver fixed useful work W = 4.5 J over T=1.5 s (15 N × 0.3 m)."""
    T = 1.5
    t = np.arange(0.0, T + DT / 2, DT)
    F_peak = jitter(rng, 15.0, 0.25)
    base = F_peak * bell(t, 0.2, 1.4)
    r_k = 0.03
    kappa_r = 0.5  # forearm-to-yaw torque coupling for rotary input
    if variant == "rotary":
        F_perp = base            # tangential hand force is transverse
        tau = base * r_k * kappa_r + F_perp * 0.05 * (occ.h_c * 0.3)
    elif variant == "lateral_lever":
        F_perp = base
        tau = base * 0.4 * occ.h_c  # lever at ~40% COM height offset
    elif variant == "axial_lever":
        F_perp = base * 0.05
        tau = np.zeros_like(t)
    elif variant == "push_pull":
        F_perp = base
        tau = base * 0.1 * occ.h_c
    else:
        raise ValueError(variant)
    R_v = base * 0.95 if variant == "axial_lever" else np.zeros_like(t)
    return ReactionProfile(t, F_perp=F_perp, R_v=R_v, tau=tau,
                           guide_eta=np.zeros_like(t), guide_tau=np.zeros_like(t),
                           F_task=base)


# ------------------------------------------------------------------ Case 4: workstation
def workstation(variant: str, occ: Occupant, rng, k_guidance: float | None = None,
                x_free: float = 0.05) -> ReactionProfile:
    """30 s reaching sequence; transverse perturbation impulses every ~4 s.

    Guidance modeled as restoring contact: once |x| > x_free the guide supplies
    fraction eta of demand; implemented via guide_eta time series driven by a
    precomputed drift proxy (simple: constant eta after first engagement).
    """
    T = 30.0
    dt_ws = 0.005  # coarse grid OK: perturbations are 0.2 s windows
    t = np.arange(0.0, T + dt_ws / 2, dt_ws)
    m = occ.m_eff
    F_perp = np.zeros_like(t)
    eta = np.zeros_like(t)

    # perturbation impulses: magnitude ~ N(0, (5 N·s)^2) over 0.2 s windows
    lam = 4.0
    nxt = rng.exponential(lam)
    while nxt < T - 0.3:
        P = rng.normal(0, 5.0)
        dur = 0.2
        mask = (t >= nxt) & (t < nxt + dur)
        F_perp[mask] += P / dur
        nxt += rng.exponential(lam) + dur

    if variant == "flat":
        pass
    elif variant in ("centering", "guided"):
        eta_val = 0.8 if variant == "centering" else 0.9
        eta[:] = eta_val  # guide engaged throughout contact with geometry
    elif variant == "neg_control":
        pass  # cosmetic trim: identical mechanics
    else:
        raise ValueError(variant)
    return ReactionProfile(t, F_perp=F_perp, R_v=np.zeros_like(t),
                           tau=np.zeros_like(t), guide_eta=eta,
                           guide_tau=np.zeros_like(t),
                           F_task=np.abs(F_perp))


# ------------------------------------------------------------------ Case 5: stairs
def stairs(variant: str, occ: Occupant, rng) -> ReactionProfile:
    """8 s stair descent; per-step lateral perturbation impulses at 1.2 Hz."""
    T = 8.0
    t = np.arange(0.0, T + DT / 2, DT)
    f_step = 1.2
    F_perp = np.zeros_like(t)
    eta = np.zeros_like(t)
    steps = np.arange(0.3, T, 1.0 / f_step)
    for s in steps:
        P = rng.normal(0, 2.0)
        mask = (t >= s) & (t < s + 0.15)
        F_perp[mask] += P / 0.15
    if variant == "conventional":
        pass
    elif variant == "guided_rail":
        eta[:] = 0.7
    elif variant == "captive":
        eta[:] = 0.95
    else:
        raise ValueError(variant)
    return ReactionProfile(t, F_perp=F_perp, R_v=np.zeros_like(t),
                           tau=np.zeros_like(t), guide_eta=eta,
                           guide_tau=np.zeros_like(t),
                           F_task=np.abs(F_perp))


CASES = {
    "door": (door, ["hinged", "lateral_slide", "vertical_guided", "neg_control"]),
    "seat": (seat, ["chair", "linear", "straddle"]),
    "control": (control, ["rotary", "lateral_lever", "axial_lever", "push_pull"]),
    "workstation": (workstation, ["flat", "centering", "guided", "neg_control"]),
    "stairs": (stairs, ["conventional", "guided_rail", "captive"]),
}

# conventional baseline per case for benefit computation
BASELINE = {
    "door": "hinged",
    "seat": "chair",
    "control": "lateral_lever",
    "workstation": "flat",
    "stairs": "conventional",
}
