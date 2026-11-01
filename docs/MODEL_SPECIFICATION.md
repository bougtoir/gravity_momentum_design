# MODEL_SPECIFICATION.md — frozen model specification (Phase 2)

Status: frozen for analysis (v1.0, 2026-09-26). Changes after freeze are logged in
CHANGELOG within this file and propagated to the manuscript methods.

## 1. Occupant model (Level 1 — single rigid body, planar)

The occupant is a planar rigid body standing/acting on a support surface.

State:
- `x_perp(t)`, `v_perp(t)`: task-irrelevant transverse COM position/velocity (m, m/s)
- `theta(t)`, `omega(t)`: yaw angle and angular velocity about the vertical COM axis (rad, rad/s)

Parameters:
- `m` — body mass [kg], N(75, 9²) truncated to [50, 110] (anthropometric spread)
- `h_c` — COM height [m], = 0.55·H with H ~ N(1.75, 0.08²) truncated [1.5, 2.0]
- `I_yaw` — yaw moment of inertia about COM [kg·m²] = m·r_g², r_g ≈ 0.32·(body width ~0.46·H)/2 ≈ 0.23·H·0.32... simplified: I_yaw = c_I·m·H² with c_I = 0.013 (Winter segment scaling ~ cylindrical trunk). Range in MC via H and m.
- `mu` — effective support friction coefficient, uniform [0.3, 0.7] (shoe–floor range from RCOF literature)
- `r_f` — effective support-base half-width for rotational friction torque [m], = 0.12·H/1.75 ≈ foot-stance lever, uniform ±20%

Gravity: `g = g*·g_E`, g_E = 9.80665 m/s². Continuous sweep g* ∈ [0.05, 1.00],
plus annotated Earth 1.00 / Mars 0.38 / Moon 0.165 / 0.25 / 0.50 / 0.75.

## 2. Support mechanics

Normal capacity: `N(t) = m·g + R_v(t)` where `R_v` is the vertical component of the
interface reaction (positive downward). Normal is bounded below by 0 (loss of
contact; flagged) — a `loss_of_support` indicator records N < 0.05·m·g events.

Transverse (friction) capacity: `F_cap(t) = mu·f_u·N(t)` where `f_u` is a
friction-utilization factor U[0.5, 0.85] (occupants cannot commit the full
static friction budget mid-motion; dynamic coefficient and load sharing reduce
the usable fraction).
Rotational (yaw) capacity: `tau_cap(t) = mu·f_u·N(t)·r_f`.

These encode "gravity-supplied stabilization": both capacities scale linearly with g
while body inertia does not.

## 3. Interface reaction

An interface task produces a reaction force `R(t)` and torque `tau_r(t)` on the
occupant. The task-relevant motion axis is `e_d` (unit vector, task-dependent).

Decomposition:
- `F_parallel = (R·e_d)e_d` — produces useful work/motion, NOT penalized.
- `F_perp = R − F_parallel` — task-irrelevant transverse reaction demand.

Note the distinction: `F_perp` is task-irrelevant for the *occupant's* stabilization,
even when the reaction direction is the task-relevant direction for the *device*
(e.g., a lateral sliding door: the lateral pull is useful to the door but must be
reacted by the occupant's friction). See §6 per-case definitions of e_d.

## 4. Outcome metrics (primary)

- **UTI** [N·s] = ∫|F_perp_excess(t)| dt, where
  `F_perp_excess = max(|F_perp|·(1−η_g) − F_cap, 0)` — passive guidance absorbs
  fraction η_g of the demand; the residual must be supplied by friction or
  becomes body momentum.
- **UAI** [N·m·s] = ∫|tau_excess(t)| dt,
  `tau_excess = max(|tau_r|·(1−η_τ) − tau_cap, 0)`.
- Secondary: peak F_perp, transverse COM drift x_perp(T), residual v_perp(T),
  corrective impulse J_corr = m·v_perp(T) + ∫S dt, yaw excursion theta(T),
  task time, useful work, loss-of-support count, reach/confinement penalty.

- **Gamma_T** = max_t |F_perp(t)| / (mu·m·g) — stabilization-demand ratio
  (dimensionless); >1 means friction alone cannot supply the reaction at that
  instant. NOT a universal fall threshold (biomechanical caveat stated).

- Normalized benefit: `B_UTI(g*) = 1 − UTI_redesigned/UTI_conventional`
  (likewise B_UAI). Estimated continuously over g*.

## 5. Dynamics integration

Explicit semi-implicit Euler, dt = 1 ms (step-size sensitivity at 0.25–4 ms in
verification):

```
v_perp += (F_perp_signed_excess/m)·dt
x_perp += v_perp·dt
omega  += (tau_excess/I_yaw)·dt
theta  += omega·dt
```

Corrections: when the occupant deploys a corrective action (handhold grab, extra
step) — modeled as an impulse that arrests accumulated transverse/angular momentum
with a reaction delay `t_react` ~ U[0.3, 0.6] s (literature reaction-time range) —
residual momentum is zeroed and J_corr accumulated. Corrective actions fire when
|x_perp| or |theta| exceeds the support margin (x_margin = 0.15·H/1.75·... =
support half-width s_b; theta_margin = 0.2 rad).

A task ends at prescribed duration T_task. Failure flag if x_perp exits
x_margin·k_fail (2× margin) before correction.

## 6. Canonical interface cases

### Case 1 — Door/hatch
Task: open a door of normalized opening area A_d = 0.8 m², useful work W_use fixed.
- `hinged`: pull perpendicular to door plane at handle radius l_h = 0.76 m from
  hinge; occupant stands offset → reaction has transverse component magnitude
  F_task·sin(φ_s) applied at height h_a = 1.0 m (lever arm → yaw torque
  τ = F_perp·h_a). Opening over T = 2.0 s, F_task bell-shaped, peak from
  ADA-type operating force ~22 N plus latch 10 N, half-sine profile.
- `lateral-slide`: force along floor-parallel slide axis; occupant pulls toward
  self → transverse reaction = full F_task; no yaw lever (h_a ≈ waist → small).
- `vertical-guided`: lift axis along gravity; R_v > 0 adds to N; F_perp ≈ 0.05·F
  residual misalignment (parameter); guide fraction η_g = 0.9 on residual.
- `neg_control` (negative control): hinged door with restyled handle — identical
  force profile; must yield identical UTI/UAI within numerical tolerance.

Normalization: all variants perform identical useful work (peak force × stroke
matched to W_use ±5%), same T_task.

### Case 2 — Seat ingress
Task: move COM from approach point to seated position over T = 3.0 s along a
prescribed path; force demands are the centripetal/transverse reactions needed to
follow the path.
- `chair`: conventional — approach facing forward, turn Δψ = 150°, then translate
  laterally+backward and descend. Path curvature produces F_perp = m·v²/r_path
  (r_path = 0.45 m turn) plus yaw angular impulse ∫τ = I·Δω for reorientation,
  applied at h_a = h_c (torque about COM).
- `linear`: straight-ahead slide-in, Δψ = 20°, r_path → ∞ (no turn arc).
- `straddle`: forward approach onto saddle, Δψ = 10°, guide fraction η_g = 0.85
  while captured by geometry, near-linear settle.
Normalization: same start/end COM positions and T_task; v(t) = smoothed trapezoid.

### Case 3 — Control/actuation (analytic verification case)
Task: deliver fixed useful torque impulse or work: W = τ·θ or F·s.
- `rotary knob`: hand applies tangential force F_t at knob radius r_k = 0.03 m;
  torque τ = F_t·r_k for T = 1.5 s; reaction F_t transverse at h_a; reaction
  torque on body = τ (about forearm→yaw coupling κ_r = 0.5).
- `lateral lever`: push laterally, F_task lever stroke 0.3 m; full transverse.
- `axial lever (support-aligned)`: push along gravity axis → adds to N, F_perp
  residual 5%, guide η=0.
- `push/pull linear`: pull toward body, e_d = fore-aft; treated as transverse
  (fore-aft motion is not task-relevant for stance). Distinct axis flag.
All variants deliver identical work W_ctrl = F·s (F peak ~15 N).

### Case 4 — Workstation
Task: perform reaching sequence — body receives small perturbation impulses
P_pert ~ N(0, (5 N·s)²) each Δt_pert ~ Exp(mean 4 s) over T = 30 s (represents
reach-induced transients); occupant corrects drift via friction.
- `flat`: η_g = 0, guidance stiffness k = 0.
- `centering`: weak concavity, restoring F = −k_x x − k_y y with k = 40 N/m
  equivalent guide η_g ramped by |x| (contact model: guide engages for
  |x| > x_free = 0.05 m with η=0.8).
- `guided`: stronger, k = 120 N/m, η = 0.9, x_free = 0.02 m.
Penalties: reach penalty = k·x_reach_max·n_reach (extra work N·m proxy),
confinement proxy = x_free reduction. Sweep k ∈ [0, 200] N/m for Pareto.
Negative control alternative: a flat workstation with cosmetic edge trim —
identical mechanics.

### Case 5 — Vertical circulation (stairs/ladder)
Task: descend/ascend H_story = 3 m equivalent, T = 8 s; per-step lateral
perturbation impulse P_step ~ N(0, (2 N·s)²) at f_step = 1.2 Hz.
- `conventional`: stair + single handrail: guide only after corrective grab
  (η = 0 en route; correction capacity τ/hand-hold).
- `guided rail`: bilateral rail gives η_g = 0.7 continuous transverse guidance.
- `pole/captive descent`: η_g = 0.95, near-full constraint (mechanical only;
  egress/safety caveats noted).
Simplified drift integrator, deviation channels: lateral drift, fall-direction
deviation (N deficit), yaw.

## 7. Monte Carlo

N = 2000 virtual trials per (case, variant, g* ∈ {0.165, 0.25, 0.38, 0.5, 0.75, 1.0})
for distributions; continuous response curves use analytic/deterministic mean
parameter vector evaluated on dense g* grid (n_g = 40) — MC reserved for the
reference gravity points to keep compute bounded. Convergence: double-N check on
principal estimates; report change in mean/CI width.

Varied parameters: m, H, mu, F_task magnitude (±25% lognormal-ish truncated),
speed (±20%), I via H, t_react, P_pert/P_step, guide η (±10% rel).
Sources/assumptions logged per parameter in Table 1.

## 8. Suit/load sensitivity (separate block)

Added mass m_suit ∈ {0, 20, 40, 60} kg (shirt-sleeve → EVA-like added mass),
I scaled ∝ (m+m_suit)·H², same mu — tests the inertia-vs-weight divergence.
Restricted-ROM proxy: t_react +50%, v_max −30%.

## 9. Falsification criteria (predefined)

A. UTI/UAI consequence does not grow as g decreases → framework weakened.
B. Equal benefit at 1 g and low g → generic ergonomics, not gravity-specific.
C. Effect confined to one interface class → no cross-interface generalization.
D. Reduced UTI does not reduce corrective demand/drift.
E. Results vanish under parameter uncertainty.
F. Benefits require unrealistic operating forces (>100 N peak).

## 10. Statistical model

B(g*) curves via bootstrap CI over MC trials; gravity×design interaction tested by
log-linear regression of UTI on g* and design indicator with interaction term on
MC outputs (robust: fit to per-trial logs). Effect sizes reported.

## Changelog

- v1.0 2026-09-26: initial freeze.
