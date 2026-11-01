"""Verification tests for the core mechanics (Phase 3 items 1-10)."""
import numpy as np
import pytest
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.params import Occupant, G_E
from src.mechanics import ReactionProfile, simulate, bell
from src.cases import door, control, CASES


def prof(t, F):
    z = np.zeros_like(t)
    return ReactionProfile(t=t, F_perp=F, R_v=z, tau=z.copy(),
                           guide_eta=z.copy(), guide_tau=z.copy(),
                           F_task=np.abs(F))


def test_zero_transverse_force_gives_zero_UTI():
    t = np.arange(0, 2.0, 0.001)
    r = simulate(prof(t, np.zeros_like(t)), Occupant(), 1.0)
    assert r.UTI == 0 and r.UAI == 0 and r.drift_x == 0


def test_no_capacity_momentum_conservation():
    """With g→0 (capacity→0), ∫F dt must equal m·|v_end| (corrective excluded)."""
    t = np.arange(0, 1.0, 0.001)
    F = 10.0 * bell(t, 0.2, 0.8)
    occ = Occupant(m=80.0)
    r = simulate(prof(t, F), occ, 1e-6, record=True)
    p_analytic = np.trapezoid(F, t)
    p_model = occ.m_eff * abs(r.traces["v_perp"][-1])
    # small residual friction at g=1e-6 negligible
    assert abs(p_analytic - p_model) / p_analytic < 0.02


def test_earth_g_full_capacity():
    """At 1 g, a modest force below mu*mg produces no excess impulse."""
    t = np.arange(0, 1.0, 0.001)
    F = 10.0 * bell(t, 0.0, 1.0)  # peak 10 N << 0.5*75*9.8 ≈ 368 N
    r = simulate(prof(t, F), Occupant(), 1.0)
    assert r.UTI < 1e-9 and r.n_corr == 0


def test_low_g_produces_excess():
    """Same force at lunar g must exceed capacity and generate UTI."""
    t = np.arange(0, 1.0, 0.001)
    F = 60.0 * bell(t, 0.0, 1.0)
    r_hi = simulate(prof(t, F), Occupant(), 1.0)
    r_lo = simulate(prof(t, F), Occupant(), 0.165)
    assert r_lo.UTI > r_hi.UTI
    assert r_hi.UTI == 0 or r_lo.UTI / max(r_hi.UTI, 1e-9) > 2


def test_gamma_T_scales_inverse_g():
    t = np.arange(0, 1.0, 0.001)
    F = 30.0 * bell(t, 0.0, 1.0)
    r1 = simulate(prof(t, F), Occupant(), 1.0)
    r2 = simulate(prof(t, F), Occupant(), 0.5)
    assert abs(r1.gamma_T / r2.gamma_T - 0.5) < 1e-9


def test_impulse_integration_bell():
    """∫ of half-sine of amplitude A over [0,T] is 2AT/π."""
    t = np.arange(0, 2.0, 0.001)
    F = 20.0 * bell(t, 0.0, 2.0)
    occ = Occupant(mu=0.0)  # no capacity at all
    r = simulate(prof(t, F), occ, 1.0)
    analytic = 2 * 20.0 * 2.0 / np.pi
    assert abs(r.UTI_demand - analytic) / analytic < 1e-3


def test_angular_impulse_pathway():
    t = np.arange(0, 1.0, 0.001)
    p = prof(t, np.zeros_like(t))
    p.tau[:] = 5.0 * bell(t, 0.0, 1.0)
    r = simulate(p, Occupant(mu=0.0), 1.0)
    analytic = 2 * 5.0 * 1.0 / np.pi
    assert abs(r.UAI_demand - analytic) / analytic < 1e-3


def test_negative_control_identical():
    rng1 = np.random.default_rng(7)
    rng2 = np.random.default_rng(7)
    occ = Occupant()
    r_h = simulate(door("hinged", occ, rng1), occ, 0.38)
    r_n = simulate(door("neg_control", occ, rng2), occ, 0.38)
    assert abs(r_h.UTI - r_n.UTI) / max(r_h.UTI, 1e-9) < 1e-9


def test_axial_control_beats_lateral_at_low_g():
    occ = Occupant()
    rng = np.random.default_rng(0)
    r_lat = simulate(control("lateral_lever", occ, rng), occ, 0.165)
    rng = np.random.default_rng(0)
    r_ax = simulate(control("axial_lever", occ, rng), occ, 0.165)
    # axial lever removes both excess UTI and UAI vs lateral lever at lunar g
    assert (r_ax.UTI + r_ax.UAI) < (r_lat.UTI + r_lat.UAI)


def test_monotonic_benefit_direction():
    """Redesigned vertical door should reduce UTI more at low g than at 1 g."""
    occ = Occupant()
    def uti(var, g, seed):
        return simulate(door(var, occ, np.random.default_rng(seed)), occ, g).UTI
    b_lo = 1 - uti("vertical_guided", 0.165, 3) / max(uti("hinged", 0.165, 3), 1e-9)
    b_hi = 1 - uti("vertical_guided", 1.0, 3) / max(uti("hinged", 1.0, 3), 1e-9)
    assert b_lo >= b_hi - 1e-6


def test_all_case_variants_run():
    occ = Occupant()
    rng = np.random.default_rng(1)
    for name, (fn, variants) in CASES.items():
        for v in variants:
            r = simulate(fn(v, occ, rng), occ, 0.38)
            assert np.isfinite(r.UTI) and np.isfinite(r.UAI)
