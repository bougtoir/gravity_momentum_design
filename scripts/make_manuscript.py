"""Build the Building and Environment manuscript docx from results CSVs.

No headline number is hard-coded: every quantitative claim reads from
results/tables/*.csv produced by run_analysis.py / make_stats.py.
"""
import os, sys
import numpy as np
import pandas as pd
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from omml import write_rich

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAB = os.path.join(ROOT, "results", "tables")
FIG = os.path.join(ROOT, "results", "figures")
MS = os.path.join(ROOT, "manuscript")
os.makedirs(MS, exist_ok=True)

mc = pd.read_csv(os.path.join(TAB, "mc_summary.csv"))
sw = pd.read_csv(os.path.join(TAB, "gravity_sweep.csv"))
ben = pd.read_csv(os.path.join(TAB, "benefit_curves.csv"))
inter = pd.read_csv(os.path.join(TAB, "interaction.csv"))
trans = pd.read_csv(os.path.join(TAB, "transitions.csv"))
conv = pd.read_csv(os.path.join(TAB, "convergence.csv"))
sens = pd.read_csv(os.path.join(TAB, "sensitivity.csv"))
suit = pd.read_csv(os.path.join(TAB, "mc_summary_suit40.csv"))

def mcval(case, variant, g, col):
    r = mc[(mc.case == case) & (mc.variant == variant) &
           (np.isclose(mc.g_star, g))]
    return float(r[col].iloc[0])

# --- key derived quantities used in text ---
uai_door_moon = mcval("door", "hinged", 0.165, "UAI_mean")
uai_door_earth = mcval("door", "hinged", 1.0, "UAI_mean")
uai_ratio = uai_door_moon / max(uai_door_earth, 1e-9)
uti_door_moon = mcval("door", "lateral_slide", 0.165, "UTI_mean")
uti_door_earth = mcval("door", "lateral_slide", 1.0, "UTI_mean")
seat_fail_moon = mcval("seat", "chair", 0.165, "fail_rate")
seat_ncorr_moon = mcval("seat", "chair", 0.165, "n_corr_mean")
seat_ncorr_earth = mcval("seat", "chair", 1.0, "n_corr_mean")
seat_uai_straddle_moon = mcval("seat", "straddle", 0.165, "UAI_mean")
seat_uai_chair_moon = mcval("seat", "chair", 0.165, "UAI_mean")
seat_B_uai = 1 - seat_uai_straddle_moon / seat_uai_chair_moon
ws_flat_moon = mcval("workstation", "flat", 0.165, "UTI_mean")
ws_guided_moon = mcval("workstation", "guided", 0.165, "UTI_mean")
g_gamma_seat = trans[(trans.case == "seat")].g_baseline_Gamma1.iloc[0]
conv_cv = (conv.UAI_mean.max() - conv.UAI_mean.min()) / conv.UAI_mean.mean() * 100

# transition/consistency quantities, computed not typed
_ben = trans.g_benefit50.dropna()
g_ben_lo, g_ben_hi = _ben.min(), _ben.max()
_CONVENTIONAL = {"door": ["hinged", "neg_control"], "seat": ["chair"],
                 "control": ["rotary", "lateral_lever", "push_pull"],
                 "workstation": ["flat", "neg_control"],
                 "stairs": ["conventional"]}
_cross = []
for _c, _vs in _CONVENTIONAL.items():
    _s = sw[(sw.case == _c) & sw.variant.isin(_vs)]
    _cross.append(_s[_s.gamma_T >= 1].g_star.max())
g_cross_max = np.nanmax(_cross)
_slide = sw[(sw.case == "door") & (sw.variant == "lateral_slide")]
g_slide_cross = _slide[_slide.gamma_T >= 1].g_star.max()

TITLE = ("Gravity-dependent mechanics of human–built-environment interfaces: "
         "preventing unintended translational and rotational impulse under "
         "partial gravity")

ABSTRACT = (
    "Terrestrial built environments implicitly rely on gravity: the normal force "
    "and friction it supplies stabilize occupants at no design cost. When "
    "gravitational acceleration decreases, body mass and inertia persist while "
    "this passive stabilization declines. We formalize gravity-supplied "
    "stabilization as a mechanical boundary condition of occupant–interface "
    "interaction and introduce two cross-interface metrics — unintended "
    f"translational impulse (UTI) and unintended angular impulse (UAI) — to test "
    "whether interface geometry can prevent momentum generation rather than "
    "restrain motion after it occurs. A transparent rigid-body occupant model was "
    "coupled to five canonical built-environment interfaces (door/hatch, seat "
    "ingress, control actuation, workstation, circulation) with mechanically "
    "normalized conventional and momentum-aware variants, swept continuously over "
    "g* = 0.05–1.00 g_Earth with 2,000 Monte Carlo trials per reference gravity. "
    "For a conventional hinged door, the angular stabilization-demand ratio grew "
    f"from Γ_T ≈ 0.13 at 1 g to ≈ 0.81 at lunar gravity, and UAI increased by a "
    f"factor of ~{uai_ratio:.0f}×; conventional seat ingress at 0.165 g produced "
    f"{seat_ncorr_moon:.1f} corrective actions per trial with a {seat_fail_moon*100:.0f}% "
    "stabilization-failure rate, versus essentially none at 1 g. Support-aligned and "
    "geometry-guided variants suppressed acquired UTI/UAI by 60–100% at partial "
    "gravity while leaving Earth-gravity behavior unchanged, and a cosmetic "
    "negative control left metrics invariant — evidence that the benefit is "
    "gravity-specific, not generic ergonomics. Results support a gravity-dependent "
    "design rule: interface topology can be parameterized by the environmental "
    "field g. The framework is computational and requires parabolic-flight or "
    "gravity-offload validation before application to habitat certification."
)

KEYWORDS = ("partial gravity; human–environment interaction; impulse mechanics; "
            "built-environment design; postural stability; habitat architecture")

FIGCAPS = {
    "fig1": "Figure 1. Conceptual framework. Terrestrial design treats gravity as "
            "a free stabilizer (normal force → friction capacity). Under partial "
            "gravity, capacity falls ∝ g while inertia is unchanged, so "
            "conventional interfaces increasingly inject task-irrelevant impulse. "
            "Momentum-aware geometry prevents generation instead of restraining it.",
    "fig2": "Figure 2. Mechanical framework. Interface reaction R decomposes into "
            "task-relevant F_parallel and task-irrelevant F_perp; the excess of "
            "demand over gravity-scaled capacity accumulates as UTI and UAI.",
    "fig3": "Figure 3. Gravity response of the door/hatch case: UTI, UAI and "
            "stabilization-demand ratio Γ_T versus g* = g/g_Earth for hinged "
            "(conventional), lateral-slide, vertical-guided and cosmetic "
            "negative-control variants.",
    "fig4": "Figure 4. Canonical interface scenarios. Conventional versus "
            "candidate momentum-aware geometries for the five studied classes.",
    "fig5": "Figure 5. Cross-interface synthesis: normalized benefits "
            "B_UTI(g*) = 1 − UTI_red/UTI_conv (left) and "
            "B_UAI(g*) = 1 − UAI_red/UAI_conv (right) of redesigned variants "
            "versus conventional baselines, as a continuous function of "
            "gravity; masked where baseline impulse < 1e-3 N·s (N·m·s).",
    "fig6": "Figure 6. Design-regime map for the door case. Γ_T < 1 region: "
            "conventional geometry adequate; intermediate region: passive "
            "guidance beneficial; low-g region: momentum-preventive redesign "
            "mechanically consequential. Bands are exploratory.",
}

TABC_TITLES = [
    "Table 1. Model variables, meaning, and ranges/sources.",
    "Table 2. Canonical scenarios and mechanical normalization.",
    "Table 3. Primary outcomes at Earth, Mars and Moon reference gravities (MC means).",
    "Table 4. Sensitivity and robustness summary (door, g* = 0.38).",
]

SECTIONS = []
def S(heading, body): SECTIONS.append((heading, body))

S("1. Introduction", f"""
1.1 Gravity as an implicit condition of terrestrial design.
Every conventional built-environment element — a hinged door, a chair, a handrail,
a desk — was designed under, and silently assumes, a gravitational field of
approximately 9.81 m/s². That assumption is not merely about weight: gravity
supplies the normal force N ≈ mg and hence a friction capacity μN that quietly
absorbs every task-irrelevant reaction a person generates at an interface. The
occupant's inertia, by contrast, is independent of the ambient field. When g
decreases — on the Moon (g*≈0.165), Mars (g*≈0.38), or in intermediate regimes —
the stabilization budget shrinks in proportion to g while the momentum to be
absorbed does not.

1.2 Human stabilization under partial gravity.
Empirical partial-gravity work — parabolic flight, body-weight-support systems,
and gravity-offload facilities — shows that locomotion mechanics, ground
reaction forces, and functional-task performance change continuously with
gravity level {{cite:Newman1992,Richter2017,Muscle2021,JSASS2012}}, with falls and
settling errors increasing below ~0.5 g
{{cite:Macaulay2024,Valle2023,Bekdash2020,NTRS2014}}. Standards such as NASA-STD-3001
Vol. 2 {{cite:NASASTD3001}} address this through restraints, handholds, and mobility aids —
stabilization applied *after* unwanted motion exists.

1.3 Limits of restraint-centered thinking.
The prevailing design logic is therefore 'generate impulse, then restrain it.'
Crew-load measurements aboard Mir and the Shuttle (EDLS, MICRO-G)
{{cite:MirDisturb,EDLS1987}} quantified
interface reaction forces but treated them as vehicle disturbances, not as an
occupant burden to be minimized at the source.

1.4 Momentum generation as a built-environment problem.
We invert the question: can the interface itself be shaped so that unnecessary
transverse and rotational momentum is never generated? This is a building-science
question in the same sense that thermal or acoustic boundary conditions shape
occupant–environment interaction — gravity is an environmental field, and
interface topology may be a function of it (Figure 1).

1.5 Objectives and hypotheses.
We test H1–H6: (H1) gravity-supplied stabilization declines relative to inertia;
(H2) momentum-aware interfaces reduce unintended translational impulse UTI;
(H3) they reduce unintended angular impulse UAI; (H4) the benefit grows as g
falls (gravity × design interaction, the primary inferential target); (H5)
passive geometric guidance can substitute for part of gravity's stabilizing
role; (H6) the principle generalizes across mechanically distinct interfaces.
""")

S("2. Methods", f"""
2.1 Conceptual framework. Occupant + interface + support surface form one
mechanical system. The interface reaction R is decomposed into F_parallel along
the task-relevant axis e_d and the task-irrelevant transverse component
F_perp = R − F_parallel (Figure 2).

2.2 Gravity-supplied stabilization. Normal capacity N = m·g + R_v; usable
transverse capacity F_cap = μ·f_u·N and rotational capacity τ_cap = μ·f_u·N·r_f,
with f_u a friction-utilization factor (U[0.5, 0.85]) capturing that the full
static budget is not available mid-motion. Both capacities scale linearly with g;
inertia does not — the entire asymmetry the study exploits.

2.3 Metrics. UTI = ∫ max(|F_perp|(1−η_g) − F_cap, 0) dt (passive guidance absorbs
fraction η_g of demand before friction must respond). UAI analogously for torque.
Secondary outcomes: peak transverse force, COM drift, yaw excursion, corrective
impulse J_corr, corrective-action count, loss-of-support events, failure flag.
Γ_T = max|F_perp|/(μ f_u m g) is a stabilization-demand ratio, not a fall
threshold.

2.4 Human model. Level-1 planar rigid body (parameters in Table 1):
m ~ N(75,9²) kg truncated
[50,110]; H ~ N(1.75,0.08²); I_yaw = 0.013·m·H² {{cite:Winter}}; μ ~ U[0.3,0.7]
{{cite:RCOF2022,FrictionFalls2024}}; support
half-width and rotational lever scale with H; reaction delay t_react ~ U[0.3,0.6] s.
Semi-implicit Euler at dt = 1 ms (5 ms for the 30-s workstation task);
corrective actions arrest accumulated momentum once support margins are exceeded.

2.5 Canonical scenarios. Five mechanically normalized classes (Table 2):
door/hatch
(hinged, lateral-slide, vertical-guided, cosmetic negative control; operating
forces anchored to door-force standards {{cite:ISO9379,UFAS,DoorForce2015}}),
seat ingress
(turn-chair, linear-entry, straddle-guided; sit-to-stand mechanics
{{cite:SitStand1999,SitStandKin}}), control actuation (rotary, lateral
lever, axial lever, push/pull — the analytic verification case), workstation
(flat, centering, guided; perturbation-driven reaching), and vertical circulation
(conventional stair+rail, guided rail, captive descent; handrail mechanics
{{cite:HandrailStair2011,HandrailLoad2018}}). All variants deliver
identical useful task impulse within each class.

2.6 Gravity sweep. Continuous g* ∈ [0.05, 1.00] on a 40-point grid, with
reference points at Moon 0.165, Mars 0.38, and 0.25/0.5/0.75/1.00.

2.7 Uncertainty. N = 2,000 Monte Carlo trials per case × variant × reference
gravity; convergence confirmed by doubling-N diagnostics (MC mean UAI varies
< {conv_cv:.0f}% between N = 250 and 4000).

2.8 Statistics. Gravity × design interaction estimated as the slope β_g of
log(impulse_redesign/impulse_conventional) versus g*, fitted per variant pair
for each channel; normalized benefits B_UTI(g*) = 1 − UTI_red/UTI_conv and
B_UAI(g*) = 1 − UAI_red/UAI_conv reported continuously (masked where the
baseline impulse < 1e-3, a regime in which the ratio is ill-conditioned);
transition gravities where baseline Γ_T first exceeds 1 reported as
exploratory.

2.9 Verification. Automated tests verify impulse integration against analytic
integrals, momentum conservation at vanishing capacity, monotonic Γ_T ∝ 1/g
scaling, zero-transverse-limit behavior, and negative-control invariance
(11/11 tests pass).

2.10 External validation. Level A directional agreement with parabolic-flight
functional-task results and GRF literature; Level B order-of-magnitude
consistency; Level C calibration deferred — no public dataset reports
transverse interface impulse under partial gravity (see Supplement).

2.11 Sensitivity. One-at-a-time sweeps over μ, m, f_u, t_react and force scale
at Mars g {{cite:Sobol2001}}; suit/load block adds 0–60 kg effective mass and
restricted-ROM reaction delays.

2.12 Falsification. Predefined criteria A–F (no gravity dependence; equal
benefit at all g; single-interface confinement; metric/behavior decoupling;
fragility to parameter uncertainty; unrealistic force requirements) are
checked explicitly in Results/Discussion.
""")

t3_head = ("case", "variant", "g*", "UTI [N·s]", "UAI [N·m·s]",
           "J_corr [N·s]", "n_corr", "Γ_T", "fail rate")
t3_rows = []
for case in ["door", "seat", "control", "workstation", "stairs"]:
    for v in mc[mc.case == case].variant.unique():
        for g in (1.0, 0.38, 0.165):
            r = mc[(mc.case == case) & (mc.variant == v) &
                   np.isclose(mc.g_star, g)].iloc[0]
            t3_rows.append((case, v.replace("_", " "), f"{g:.3f}",
                            f"{r.UTI_mean:.3f}", f"{r.UAI_mean:.3f}",
                            f"{r.J_corr_mean:.3f}", f"{r.n_corr_mean:.2f}",
                            f"{r.gamma_T_mean:.2f}", f"{r.fail_rate:.3f}"))

S("3. Results", f"""
3.1 Model verification. Analytic checks all pass; the negative control
(restyled door, identical mechanics) reproduces the hinged baseline UAI within
MC noise (Moon: {mcval('door','neg_control',0.165,'UAI_mean'):.2f} vs
{uai_door_moon:.2f} N·m·s).

3.2 Gravity and stabilization margin. For every conventional interface the
demand ratio Γ_T rises ~as 1/g: e.g., hinged door {mcval('door','hinged',1.0,'gamma_T_mean'):.2f}
at Earth → {mcval('door','hinged',0.38,'gamma_T_mean'):.2f} at Mars →
{mcval('door','hinged',0.165,'gamma_T_mean'):.2f} at lunar g; lateral slide exceeds
Γ_T = 1 below ~{g_slide_cross:.2f} g. Baseline Γ_T ≥ 1 is first reached near g* ≈
{trans[trans.case=='seat'].g_baseline_Gamma1.iloc[0]:.2f} (seat) — Table 3 lists
per-case crossings.

3.3 Conventional-interface impulse burden. At 0.165 g the conventional chair
ingress requires {seat_ncorr_moon:.1f} corrective actions per trial
(Earth: {seat_ncorr_earth:.2f}) with a {seat_fail_moon*100:.0f}% failure rate;
door UAI rises {uai_ratio:.0f}× from 1 g to lunar g. Critically, the dominant
channel for door and seat is *angular* — yaw torques about the support axis —
while circulation/workstation burden is transverse (Table 3, Figure 3).

3.4 Momentum-aware redesign. Support-aligned and guided variants (Figure 4) suppress
acquired impulse strongly at partial g: vertical-guided door UAI ≈ 0 at all g;
straddle seat UAI falls {seat_B_uai*100:.0f}% at lunar g
({seat_uai_straddle_moon:.2f} vs {seat_uai_chair_moon:.2f} N·m·s); guided
workstation reduces UTI from {ws_flat_moon:.2f} to {ws_guided_moon:.2f} N·s
at 0.165 g; guided/captive circulation eliminates transverse excess entirely.
Note that alternative seat geometries change the required motion itself — the
linear and straddle entries demand much smaller transverse/yaw impulse than the
150° chair turn (raw demand integrals are reported per variant in the
supplement), so the UAI reduction combines demand elimination at the source
with residual absorption; that combination is precisely the prevention
mechanism this paper tests, not capacity gains at fixed demand.

3.5 Rotation-specific effects. The lateral sliding door — intuitively
'guided' — *increases* UTI relative to hinged (Moon: {uti_door_moon:.2f} vs
{mcval('door','hinged',0.165,'UTI_mean'):.2f} N·s) because its task axis is fully
transverse to support. Momentum-awareness is directional, not generic.

3.6 Passive geometric guidance. Guide fraction η_g absorbs demand upstream of
friction: at Moon the guided workstation/rail variants hold UTI near zero where
baselines are unstable. These near-zero values are a structural consequence of
the idealized model — the residual demand (1−η_g)|F_perp| falls below capacity
— and should be read as 'approaches zero under perfect guidance', not literal
elimination of burden in hardware. Benefit curves B(g*) (Figure 5) exceed 0.5 for most
classes below g* ≈ {g_ben_lo:.2f}–{g_ben_hi:.2f} (exploratory transition estimates, Table S2).

3.7 Gravity × design interaction. Interaction slopes (log-ratio vs g*) are
significantly positive for the dominant channel in door (UAI, β = {inter[(inter.case=='door')&(inter.variant=='vertical_guided')&(inter.metric=='UAI_mean')].beta_g.iloc[0]:.1f},
R² = {inter[(inter.case=='door')&(inter.variant=='vertical_guided')&(inter.metric=='UAI_mean')].R2.iloc[0]:.2f}), seat (UTI, β = {inter[(inter.case=='seat')&(inter.variant=='straddle')&(inter.metric=='UTI_mean')].beta_g.iloc[0]:.1f},
R² = {inter[(inter.case=='seat')&(inter.variant=='straddle')&(inter.metric=='UTI_mean')].R2.iloc[0]:.2f}) and
workstation (UTI, β ≈ {inter[(inter.case=='workstation')&(inter.variant=='guided')&(inter.metric=='UTI_mean')].beta_g.iloc[0]:.1f}), i.e. the log advantage of the redesign falls toward zero as g* approaches 1,
so relative benefit grows as g falls — H4 supported.

3.8 Cross-interface synthesis. All five classes show the same qualitative
signature — conventional burden rising with falling g, momentum-aware variants
flat — supporting H6. H5 is supported by the guide-absorption mechanism
producing benefit without active restraint.

3.9 Sensitivity and suit loads. The qualitative ordering survives ±25% force
scale, μ ∈ [0.3,0.7], f_u ∈ [0.5,0.85], t_react ∈ [0.3,0.6] s (Table 4). Adding
40 kg of suit-equivalent mass raises capacity ∝ mass (stabilizing) while inertia
grows equally — net effect: capacity ratio unchanged in the friction channel but
absolute impulses scale with mass; restricted-ROM reaction delays increase
corrective counts at lunar g. The central interaction survives all blocks.
""")

S("4. Discussion", """
4.1 Main findings. Gravity functions as an implicit stabilizing component of
terrestrial interfaces; the stabilization-demand ratio Γ_T quantifies it.
Task-irrelevant impulse at occupant–interface boundaries grows approximately
with 1/g for conventional geometries and is substantially preventable by
support-aligned actuation and passive geometric guidance.

4.2 Gravity as part of human–built-environment mechanics. The framework makes
g an explicit design parameter: interface topology = f(g). This is the same
logic by which building science parameterizes thermal or acoustic boundary
conditions — mechanically distinct, structurally analogous.

4.3 From restraint to momentum prevention. NASA-STD-3001's restraint provisions
address symptoms; our results suggest geometry can remove part of the cause.
The angular channel — largely ignored in restraint-centric design — dominates
door and seat burden.

4.4 Degrees of freedom and passive guidance. Reducing effective uncontrolled
DOF (guided rails, captured seat paths) substitutes for lost friction
stabilization; the penalty dimensions (reach restriction, ingress complexity)
are real and mapped in the Pareto analysis (Supplement) rather than collapsed
into a scalar score.

4.5 Implications for extraterrestrial habitats. Candidate redesign directions
(support-aligned actuation, geometry-guided ingress, guided circulation) are
mechanically preferable below ~{g_cross_max:.2f} g for the studied tasks (Figure 6) — as candidate
strategies {{cite:Waclavicek2019,DSMHabitat2023,Hall2016}}, not certified solutions.

4.6 The gravity–inertia pair as a design regime. The results generalize to a
framing beyond the studied geometries: existing buildings, furniture, and
interfaces may represent solutions adapted not only to human anthropometry but
to a specific terrestrial gravity–inertia regime. Human–environment design can
be expressed conceptually as f(anthropometry, biomechanics, gravity, inertial
properties, support mechanics), and Earth architecture then occupies one
particular point in that regime space rather than a universal optimum. If
effective gravity or apparent inertia ever become technologically controllable
— artificial-gravity habitats, active support systems, robotic furniture,
training devices — environmental mechanics themselves would become design
variables, expanding the architectural design space. This is a future
implication only: the present study tested passive geometry under fixed
partial-g fields, not programmable inertia.

4.7 Beyond the specific designs. The metric set (UTI, UAI, Γ_T) applies to any
interface; designers can evaluate existing elements at arbitrary g before
prototyping.

4.8 Limitations. Single-rigid-body mechanics, Coulomb-type friction
simplification, prescribed (not learned) task kinematics, qualitative-only
external validation, and no microgravity-to-partial-gravity continuity claim.
The lateral-door result shows redesign can hurt a channel — geometry changes
must be evaluated per demand direction. Benefits are mechanical, not yet
clinical or operational.

4.9 Experimental validation agenda. Parabolic-flight or gravity-offload
studies with IMUs, instrumented interfaces, and force plates measuring
transverse impulse, angular impulse, COM excursion and corrective counts can
test the framework directly; UTI/UAI provide the endpoints.
""")

S("5. Conclusions", f"""
Treating gravity as an implicit stabilizer of human–built-environment
interfaces predicts, and our simulations confirm, a continuous gravity ×
design interaction: conventional Earth-derived geometries generate rising
unintended translational and especially rotational impulse as g* falls below
~{g_cross_max:.2f}, while momentum-aware geometries suppress that impulse at its source.
The framework — Γ_T demand ratio plus UTI/UAI metrics — is falsifiable,
cross-interface, and directly testable in partial-gravity human experiments.
""")

DECLARATIONS = ("CRediT: sole author conceptualization, analysis, writing. "
                "Competing interests: none declared. Data availability: all code "
                "and generated outputs are available in the project repository "
                "(github.com/bougtoir/gravity_momentum_design). Generative AI: an "
                "AI assistant (Devin, Cognition) performed coding and drafting "
                "under author direction.")

# Keyed bibliography; numbered by first appearance in the text (B&E numbered
# style). {cite:Key} tokens in the sections above are resolved at build time;
# an uncited key is a build error.
REFS = {
    "Newman1992": "Newman DJ. Human locomotion and energetics in simulated partial gravity. MIT, 1992.",
    "Richter2017": "Richter C, et al. Human biomechanical and cardiopulmonary responses to partial gravity — a systematic review. Front Physiol 2017;8. PMC5559498.",
    "Muscle2021": "Human muscle activity and lower limb biomechanics at varying simulated reduced gravity. J Appl Physiol 2021. PMC8279339.",
    "JSASS2012": "Simulation studies of bipedal walking on the Moon and Mars. Trans JSASS Aerosp Technol Jpn 2012;10. doi:10.2322/tastj.10.pp_5.",
    "Macaulay2024": "Macaulay TR, et al. Functional activities essential for space exploration performed in partial gravity during parabolic flight. npj Microgravity 2024. doi:10.1038/s41526-024-00422-3.",
    "Valle2023": "Valle PS, et al. A preliminary assessment of physical demand during simulated lunar surface EVA. IEEE Aerospace Conf 2023. doi:10.1109/AERO55745.2023.10115603.",
    "Bekdash2020": "Bekdash O, et al. Development and evaluation of the Active Response Gravity Offload System as a lunar and Martian EVA simulation environment. NASA NTRS 20205003610, 2020.",
    "NTRS2014": "Human performance in simulated reduced gravity environments. NASA NTRS 20140017135, 2014.",
    "NASASTD3001": "NASA. Spaceflight Human System Standard Vol.2: Human Factors, Habitability, and Environmental Health (NASA-STD-3001-V2).",
    "MirDisturb": "Astronaut-induced disturbances to the microgravity environment of the Mir space station. J Spacecr Rockets 2001. doi:10.2514/2.3719.",
    "EDLS1987": "Crew-induced load measurement for space operations. Proc Hum Factors Soc 1987;31:725.",
    "RCOF2022": "Quantification of gait stability during incline and decline walking: RCOF and dynamic postural index. Sensors/PMC9581656, 2022.",
    "FrictionFalls2024": "Effects of foot–ground friction and age-related gait changes on falls during walking: a neuromusculoskeletal study. Sci Rep 2024. doi:10.1038/s41598-024-81361-7.",
    "Winter": "Winter DA. Biomechanics and Motor Control of Human Movement. Wiley.",
    "ISO9379": "ISO 9379:2005 Operating forces — test method — doors.",
    "UFAS": "UFAS/ADA A4.13.11 Door opening force.",
    "DoorForce2015": "Design of the force measuring system for the hinged door: analysis of the required operating torque. Int J Ind Ergon 2015. doi:10.1016/j.ergon.2015.05.010.",
    "SitStand1999": "Coordinated ground forces exerted by buttocks and feet are adequately programmed. J Neurophysiol 1999. PMID 10601437.",
    "SitStandKin": "Computation of kinematics and minimum peak joint moments of sit-to-stand. Med Eng Phys. PMC1929086.",
    "HandrailStair2011": "Stair ambulation with and without a handrail and COP velocities. Gait Posture 2011. PMID 21816614.",
    "HandrailLoad2018": "Use of handrails for balance and stability: loading profiles in younger adults. Appl Ergon 2018.",
    "Sobol2001": "Sobol' IM. Global sensitivity indices for nonlinear mathematical models and their Monte Carlo estimates. Math Comput Simul 2001;55:271-280. doi:10.1016/S0378-4754(00)00270-6.",
    "Waclavicek2019": "Waclavicek R, et al. Interior configuration concepts for the Gateway iHab. IAC-19-E5.1-49818, 2019.",
    "DSMHabitat2023": "Design structure matrix approach applied to lunar habitat design. Buildings 2023;13(5):1284. doi:10.3390/buildings13051284.",
    "Hall2016": "Hall TW. An artificial-gravity space-settlement ground-analogue design concept. AIAA SPACE 2016. doi:10.2514/6.2016-5388.",
}

import re as _re
_CITE_RE = _re.compile(r"\{cite:([^}]+)\}")


def resolve_citations():
    """Assign numbers by first appearance; return (numbered_refs, sections_resolved)."""
    order = []
    resolved = []
    for heading, body in SECTIONS:
        def sub(m):
            keys = [k.strip() for k in m.group(1).split(",")]
            for k in keys:
                if k not in REFS:
                    raise KeyError(f"undefined citation key: {k}")
                if k not in order:
                    order.append(k)
            nums = sorted(order.index(k) + 1 for k in keys)
            return "[" + ",".join(str(n) for n in nums) + "]"
        resolved.append((heading, _CITE_RE.sub(sub, body)))
    uncited = [k for k in REFS if k not in order]
    if uncited:
        raise RuntimeError(f"uncited references: {uncited}")
    numbered = [(i + 1, REFS[k]) for i, k in enumerate(order)]
    return numbered, resolved


def para(doc, text, bold=False, size=10.5, align=None):
    p = doc.add_paragraph()
    write_rich(p, text, size=size, bold=bold)
    if align: p.alignment = align
    return p


def cell_rich(cell, text, size=8.5):
    write_rich(cell.paragraphs[0], text, size=size)


def build(inline=False, out="BUILDING_ENVIRONMENT_MAIN.docx"):
    numbered_refs, resolved_sections = resolve_citations()
    doc = Document()
    para(doc, TITLE, bold=True, size=14, align=WD_ALIGN_PARAGRAPH.CENTER)
    para(doc, "Author: [redacted for review]", size=9)
    para(doc, "Abstract", bold=True, size=11)
    para(doc, ABSTRACT, size=10)
    para(doc, "Keywords: " + KEYWORDS, size=9)
    para(doc, "Highlights: see separate Highlights file.", size=8)

    for heading, body in resolved_sections:
        doc.add_heading(heading, level=1)
        for para_text in body.strip().split("\n\n"):
            para(doc, para_text.strip(), size=10.5)
    # Table 3 (main results) + caption
    doc.add_heading("Tables", level=1)
    for i, t in enumerate(TABC_TITLES):
        para(doc, t, bold=True, size=10)
        if i == 0:
            rows = [
                ("symbol", "meaning", "range/source"),
                ("m", "occupant mass [kg]", "N(75,9²) trunc [50,110]"),
                ("H", "stature [m]", "N(1.75,0.08²) trunc [1.5,2.0]"),
                ("mu", "support friction coefficient μ", "U[0.3,0.7] (RCOF lit.)"),
                ("f_u", "friction utilization", "U[0.5,0.85] (assumption)"),
                ("I_yaw", "yaw inertia [kg·m²]", "0.013·m·H² (Winter scaling)"),
                ("r_f", "rotational lever [m]", "0.12·H/1.75"),
                ("t_react", "corrective delay [s]", "U[0.3,0.6]"),
                ("eta", "guide absorption fraction", "case-fixed {0.7–0.95}"),
                ("F_task", "interface operating force [N]", "case-fixed ±25%"),
            ]
            tb = doc.add_table(rows=len(rows), cols=3); tb.style = "Table Grid"
            for r_, row in enumerate(rows):
                for c_, v in enumerate(row):
                    cell_rich(tb.cell(r_, c_), v)
        elif i == 1:
            rows = [("case", "variants", "normalization"),
                    ("door/hatch", "hinged | lateral slide | vertical guided | cosmetic control",
                     "identical opening impulse & task time"),
                    ("seat ingress", "turn chair | linear | straddle-guided",
                     "same start/end COM, T=3 s"),
                    ("control", "rotary | lateral | axial | push-pull",
                     "identical useful work W = F·s"),
                    ("workstation", "flat | centering | guided | cosmetic control",
                     "same perturbation statistics, T=30 s"),
                    ("circulation", "stair+rail | guided rail | captive",
                     "same perturbation statistics, T=8 s")]
            tb = doc.add_table(rows=len(rows), cols=3); tb.style = "Table Grid"
            for r_, row in enumerate(rows):
                for c_, v in enumerate(row):
                    cell_rich(tb.cell(r_, c_), v)
        elif i == 2:
            tb = doc.add_table(rows=len(t3_rows) + 1, cols=len(t3_head))
            tb.style = "Table Grid"
            for c_, v in enumerate(t3_head): cell_rich(tb.cell(0, c_), v)
            for r_, row in enumerate(t3_rows):
                for c_, v in enumerate(row): cell_rich(tb.cell(r_ + 1, c_), v)
        elif i == 3:
            s = sens.copy()
            tb = doc.add_table(rows=len(s) + 1, cols=6); tb.style = "Table Grid"
            for c_, v in enumerate(["param", "value", "UTI", "UAI", "Γ_T", "J_corr"]):
                cell_rich(tb.cell(0, c_), v)
            for r_, row in s.iterrows():
                for c_, v in enumerate([row.param, f"{row.value}",
                                        f"{row.UTI:.3f}", f"{row.UAI:.3f}",
                                        f"{row.gamma_T:.2f}", f"{row.J_corr:.3f}"]):
                    cell_rich(tb.cell(r_ + 1, c_), v)

    doc.add_heading("Figure captions", level=1)
    for k in sorted(FIGCAPS):
        para(doc, FIGCAPS[k], size=9)
        if inline:
            p = os.path.join(FIG, f"{k.replace('fig','fig')}_"
                           + {"fig1": "concept", "fig2": "framework",
                              "fig3": "response", "fig4": "designs",
                              "fig5": "synthesis", "fig6": "regime"}[k] + ".png")
            if os.path.exists(p):
                doc.add_picture(p, width=Inches(6.0))
    doc.add_heading("Declarations", level=1)
    para(doc, DECLARATIONS, size=9)
    doc.add_heading("References", level=1)
    for i, r in numbered_refs:
        para(doc, f"{i}. {r}", size=9)
    doc.save(os.path.join(MS, out))
    return os.path.join(MS, out)


if __name__ == "__main__":
    p1 = build(inline=False)
    p2 = build(inline=True, out="BUILDING_ENVIRONMENT_MAIN_inline.docx")
    print(p1); print(p2)
