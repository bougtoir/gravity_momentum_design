"""Parameter definitions and sampling for the gravity-momentum model.

All values follow docs/MODEL_SPECIFICATION.md. Sources noted inline;
uncertain parameters use broad uniform/truncated-normal ranges rather than
fabricated empirical distributions.
"""
from __future__ import annotations

import numpy as np
from dataclasses import dataclass, field, replace

G_E = 9.80665  # m/s^2
G_MOON = 0.165
G_MARS = 0.38


@dataclass
class Occupant:
    m: float = 75.0        # kg
    H: float = 1.75        # m
    mu: float = 0.5        # support friction coefficient
    fric_use: float = 0.68 # friction utilization: usable fraction of mu*N mid-motion
    t_react: float = 0.45  # s, corrective-action delay
    suit_mass: float = 0.0 # kg added load
    rom_factor: float = 1.0  # 1.0 normal; <1 restricted ROM (slower, weaker)

    @property
    def m_eff(self):
        return self.m + self.suit_mass

    @property
    def h_c(self):
        return 0.55 * self.H

    @property
    def I_yaw(self):
        return 0.013 * self.m_eff * self.H ** 2

    @property
    def r_f(self):
        return 0.12 * self.H / 1.75

    @property
    def x_margin(self):
        return 0.15 * self.H / 1.75

    @property
    def theta_margin(self):
        return 0.2  # rad


def sample_occupant(rng: np.random.Generator, suit_mass: float = 0.0,
                    restricted_rom: bool = False) -> Occupant:
    m = np.clip(rng.normal(75.0, 9.0), 50.0, 110.0)
    H = np.clip(rng.normal(1.75, 0.08), 1.5, 2.0)
    mu = rng.uniform(0.3, 0.7)
    fric_use = rng.uniform(0.5, 0.85)
    t_react = rng.uniform(0.3, 0.6)
    rom = 1.0
    if restricted_rom:
        t_react *= 1.5
        rom = 0.7
    return Occupant(m=m, H=H, mu=mu, fric_use=fric_use, t_react=t_react,
                    suit_mass=suit_mass, rom_factor=rom)


def jitter(rng: np.random.Generator, base: float, rel: float) -> float:
    """Multiplicative jitter: base * U(1-rel, 1+rel)."""
    return base * rng.uniform(1.0 - rel, 1.0 + rel)
