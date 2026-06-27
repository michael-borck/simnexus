# Assessment Guide

How to grade simulation projects fairly and consistently. The core idea: a
simulation result is only useful if it is **reproducible**, **validated**, and
**interpreted** — so assess those, not just "did it run".

## The four criteria

Every project brief lists an **Assessment criteria** checklist drawn from these
four dimensions.

### 1. Reproducibility
- Did the student set and report `random_seed`?
- Does re-running the submission produce **identical** numbers/plots?
- *Why it matters:* without reproducibility, neither the student nor the grader
  can tell signal from noise. It is the foundation everything else rests on.

### 2. Validation
- Does the result match a **known analytic value or qualitative law**?
  - Queueing: utilization ρ = λ/(cμ); average queue length trends with ρ.
  - Lotka-Volterra: closed orbits around the equilibrium (γ/δ, α/β).
  - Exponential decay: A(t) = A₀·e^(−kt); Gillespie SSA matches it in expectation.
  - Monte Carlo π: the estimate converges to π as sample count grows.
  - SIR: peak infection rises with R₀ = β/γ; herd-immunity threshold 1 − 1/R₀.
- Did the student *state* what they validated against and show the comparison?

### 3. Analysis
- Are the plots and numbers **interpreted**, not just produced?
- Does the student explain *why* a parameter change had the observed effect?
- Is there a clear answer to the project's central question?

### 4. Code quality
- Clean, parameterised (no magic numbers buried in loops), readable.
- Appropriate use of the simulator's API (e.g. `get_statistics()`, not hand-rolled
  re-implementation).
- For non-CS audiences, weight this lightly; for CS courses, weight it normally.

## Sample rubric (out of 20)

| Criterion | Excellent | Adequate | Needs work |
|---|---|---|---|
| Reproducibility (4) | Seed set & stated; re-run identical | Seed set but not stated | Not reproducible |
| Validation (6) | Compared to correct analytic/theoretic result, with reasoning | Qualitative check only | No validation |
| Analysis (6) | Clear, correct interpretation; answers the question | Describes results but little interpretation | Numbers/plots with no commentary |
| Code quality (4) | Clean, parameterised, idiomatic | Works but messy | Broken or copy-pasted blindly |

## Tips

- **Grade the notebook.** Have students submit the notebook *with outputs* and the
  `random_seed` in the first cell. You can re-run it to confirm reproducibility.
- **Reward judgement over volume.** A short notebook that validates against
  theory and interprets one result beats ten plots with no commentary.
- **Use the "Things to explore" as extension credit**, not requirements — they
  differentiate strong students without bloating the base task.
- **Cross-paradigm comparison is gold.** If a student can explain *why* the
  stochastic Gillespie result fluctuates around the deterministic ODE, they
  understand simulation deeply — reward it.
