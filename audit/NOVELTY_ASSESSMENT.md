# NOVELTY_ASSESSMENT.md — gravity_momentum_design

Date: 2026-09-26 (initial; rechecked before submission)

## Searches performed

Targeted searches for prior concepts equivalent to the proposed framework:

| Query concept | Result |
|---|---|
| "momentum-minimizing architecture / habitat design" | No direct match. Closest: spacecraft rotational-stability-by-geometry work (arXiv:2408.00155) and artificial-gravity architecture (Hall 2016) — these treat the *vehicle* as the body to stabilize, not the occupant–interface couple. |
| "inertia-aware habitat design" | No prior work found treating occupant inertia vs gravity-supplied stabilization as a design variable. |
| "gravity-dependent furniture/interface topology" | Lunar-habitat interior literature (Waclavicek 2019; DSM lunar 2023; LIQUIFER/ISAE MBSE thesis) covers zoning, modularity, mobility aids — *qualitative* design process, no impulse-based mechanical model. |
| "transverse impulse minimization habitat" | None found. |
| "reaction-force-minimizing architecture" | None for occupants; reaction forces are studied as *disturbances to the vehicle* (EDLS Mir, MICRO-G) or as crew-load measurement problems (CrewLoads1987) — i.e., forces exerted on the spacecraft, not momentum burden imposed on the occupant. |
| partial-gravity biomechanics | Rich literature on locomotion/GRF/stability (Newman 1992; Richter 2017; Macaulay 2024; Sylos-Labini-style BWS studies) — all *observe* how gravity changes gait; none propose redesigning the *interface* to prevent impulse generation. |
| friction / required coefficient of friction | RCOF gait literature treats friction as a slip-fall determinant at fixed 1 g — we invert it: friction *capacity* scales with g while task forces do not. |

## Established knowledge vs proposed contribution

Established (cite, do not claim):
- GRF, joint moments, stride parameters, and task times change monotonically with g (Newman 1992; Richter 2017; Macaulay 2024).
- Restraints, handholds, and mobility aids are standard in microgravity/partial-g design (NASA-STD-3001V2).
- Crew–spacecraft reaction loads are measurable and matter for microgravity quality (EDLS 2001).
- Friction margins govern slip/fall risk at 1 g (RCOF literature).

Proposed contributions (to be tested, not asserted):
1. Gravity-supplied stabilization formalized as an implicit component of terrestrial interface mechanics (Gamma_T ratio).
2. UTI/UAI as cross-interface design quantities (impulse *generation* at the interface, not restraint after the fact).
3. Momentum-prevention vs restraint paradigm tested mechanically across 5 interface classes.
4. Continuous gravity-response analysis f(g*) rather than Earth/Moon/Mars categories.
5. Exploratory design-transition regimes in g*.

## Novelty verdict

No prior work found combining (a) a mechanical metric of task-irrelevant impulse at the
occupant–interface boundary with (b) a continuous-gravity redesign framework across
built-environment element classes. Claim "first" is NOT asserted; the claim is a novel
*framework + quantitative test*, positioned against the restraint/mobility-aid literature
it complements.

## Risk to novelty

- An astronautics reviewer may say interface forces are "known" (crew-induced loads). Defense: that literature measures loads on the *vehicle* for microgravity quality or verifies actuator/suit forces; it does not compute impulse burden on the occupant nor optimize geometry to prevent it.
- A building-science reviewer may call this aerospace. Defense: the object of study is the *built-environment element* (door, seat, workstation, stair) and its mechanical boundary condition g — the same class of environmental-dependence argument as thermal/acoustic design rules.
