# Instructor Guide

SimLab is built for teaching. This guide explains *why* it works in a classroom,
how the simulation paradigms map to courses, and how to run a project-based unit.

## Why SimLab for teaching

- **One consistent interface.** Every simulator inherits from `BaseSimulation` and
  exposes `run_simulation()`, `reset()`, and `get_parameters_info()`. Students
  learn the pattern once and can then use any of the 18 simulators.
- **Reproducible by design.** Every stochastic simulator takes a `random_seed`, so
  two students with the same parameters get identical results — essential for
  grading and for discussing "is this difference real or noise?".
- **Paradigms, not black boxes.** Because the engines are simple and readable
  (an event loop, an ODE integrator, a lattice update), students can open the
  source and see *how* each method works, not just what it outputs.
- **Plain Python output.** Results are lists/NumPy arrays, so plotting and
  analysis use the matplotlib/NumPy students already know — no proprietary tooling.

## Mapping paradigms to courses

| Paradigm | Natural home in the curriculum |
|---|---|
| Basic (Stock Market, Resource, Product) | Intro programming; business/finance electives |
| Discrete-event & Queueing | Operations research; systems modelling |
| Statistical (Monte Carlo, Markov, Gillespie) | Probability & statistics; scientific computing |
| Cellular automata | Discrete maths; complex systems; computation |
| Agent-based (incl. Boids) | Complex systems; social science; ALife |
| System dynamics | Modelling & simulation; environmental/social policy |
| Network | Network science; epidemiology; CS theory |
| Ecological / Epidemiological / Supply Chain | Domain electives (biology, public health, business) |

The same toolkit therefore serves an intro CS course (loops + plotting with the
basic sims), a simulation-modelling course (compare paradigms), and a domain
elective (epidemiology, supply chain).

## Suggested course patterns

**Intro programming (no prerequisites).** Use the basic simulators. Students
parameterise a run, capture results, and plot them — reinforcing variables,
loops, functions, and lists. Projects: *Viral Product Launch*, *Estimate π*.

**Simulation & modelling.** The paradigms *are* the syllabus. One week per
paradigm: read the doc page, run the example, complete a project, compare results
across paradigms. Projects: *M/M/1 vs M/M/c*, *Stochastic Decay vs ODE*,
*Flocking vs Milling*, *Forest Fire & Self-Organised Criticality*.

**Domain elective.** Anchor on the domain-specific simulators and use the others
as supporting context. Epidemiology elective: *Herd Immunity Threshold* +
*Flatten the Curve* + *Epidemic Spread on Networks*. Supply-chain elective:
*The Bullwhip Effect* + *Multi-Echelon Inventory*.

## Running a project-based unit

1. **Pick projects from the [Project Gallery](projects/index.md)** — each lists
   difficulty, time, and the simulator it uses.
2. **Students read the simulator's documentation page first** (linked from the
   project), then the project brief.
3. **Require reproducibility.** Every submission must state its `random_seed` and
   reproduce identical output when re-run. See the [Assessment Guide](assessment-guide.md).
4. **Require a result + an interpretation.** A plot with no commentary is not
   done. The assessment criteria on each project spell out what "done" means.

## Adapting to your students

The project briefs are starting points. Common adaptations:

- **Make it easier:** provide the starter code and ask only for parameter
  exploration + interpretation.
- **Make it harder:** require students to extend the simulator (e.g. add an SEIR
  compartment; add a second predator to Lotka-Volterra) or to validate against an
  analytic result they derive themselves.
- **Assess modelling judgement, not coding:** weight the *analysis* and
  *validation* criteria more heavily than code quality for non-CS audiences.
