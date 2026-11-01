# gravity_momentum_design

Computational research project on **gravity-dependent mechanics of human–built-environment
interfaces**, targeted to *Building and Environment* (Elsevier).

Core proposition: terrestrial built environments implicitly exploit gravity-generated normal
force and friction as passive stabilizing mechanisms. As gravitational acceleration decreases,
body mass/inertia remain while gravity-supplied stabilization declines, so conventional
Earth-derived interfaces increasingly generate task-irrelevant transverse and rotational
impulse. The study tests whether interface geometry can *prevent* unnecessary momentum
generation rather than restrain motion after it occurs.

## Layout

- `src/` — core mechanics library (impulse metrics, occupant model, interfaces)
- `scripts/` — analysis pipeline (gravity sweep, Monte Carlo, sensitivity, figures, manuscript)
- `results/` — figures, tables, diagnostics (generated)
- `manuscript/` — main manuscript sources + docx (generated)
- `supplement/` — supplementary material (generated)
- `submission/` — final submission package + zip
- `audit/` — novelty, journal-fit, hostile-review, reference, final audits
- `docs/` — model specification, literature notes, handoff
- `refs/` — verified reference library (bib + notes)
- `data/` — raw (published-curve digitizations, parameter sources) and processed data
- `tests/` — automated verification of core equations

## Reproduce

```
make all        # runs analysis pipeline -> figures/tables -> manuscript docx -> submission zip
make test       # core-equation verification
```

See `docs/FINAL_HANDOFF.md` (generated at end of project) for exact commands and inventory.
