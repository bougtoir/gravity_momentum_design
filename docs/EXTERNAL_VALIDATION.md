# EXTERNAL_VALIDATION.md — Phase 7

Validation level labels per model spec §17: A = qualitative direction,
B = relative magnitude, C = calibrated quantitative.

## Level A (directional) — supported

| Empirical finding (partial gravity) | Model counterpart |
|---|---|
| Macaulay et al. 2024 (npj Microgravity): at 0.25–0.75 g task times rise and number of falls/settle errors increase vs 1 g | our conventional-interface n_corr and fail_rate rise monotonically as g* falls (e.g. seat chair: fail_rate 0.016→0.159 from 0.38→0.165 g; n_corr 0→4.1) |
| Newman 1992; Richter et al. 2017: locomotion/GRF mechanics change continuously with g, with gait transitions at lunar-like g | our response functions are continuous in g* with a sharp knee near ~0.3–0.4 g where Γ_T crosses 1 |
| Crew-load literature (EDLS Mir; MICRO-G): in weightlessness every interface push is a net body impulse — restraints needed | limit g→0 recovers "every Newton of transverse reaction becomes body momentum" — our capacity term → 0 |

## Level B (relative magnitude) — partial

- Parabolic-flight data show seat egress/stand-up times increase by tens of
  percent at 0.5–0.75 g and larger at lunar g; our conventional-chair corrective
  impulse rises ~10× from 0.5 g → 0.165 g while redesigned variants stay near
  zero. Direction and approximate magnitude class (order-of-magnitude burden
  growth) are consistent; exact task protocols differ, so no pointwise fit.

## Level C — not performed

No public dataset reports transverse impulse at occupant–interface boundaries
under partial gravity. Calibration is explicitly deferred to the experimental
agenda (parabolic flight or ARGOS-class offload) described in the Discussion.

## Honest caveat

The validation establishes that *something destabilizing grows as g decreases*
and that our metric grows in the same direction — it does not validate absolute
UTI/UAI magnitudes. The manuscript states this.
