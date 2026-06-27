# Project Template

Use this structure for every student project. Copy it, fill it in, and keep the
headings and order identical so the gallery stays consistent.

```markdown
# <Project Title>

**Difficulty**: Beginner | Intermediate | Advanced
**Time**: ~XX minutes
**Learning Focus**: <one or two concepts, e.g. "stochastic processes, convergence">
**Simulator**: <ClassName> (registry name `"<RegistryName>"`)

## Overview
Two or three sentences: what the student will model or investigate and why it
matters. Name the real-world system and the question being asked.

## Setup
A one- or two-line reminder of how to get ready (install + which interface).

## Instructions
Numbered, incremental steps. Each step is concrete and runnable. Include a short
starter code block using `from sim_lab.core import <ClassName>` (or
`SimulatorRegistry.create(...)`), and build toward the answer one step at a time.

## Things to explore
Three to five investigation prompts ("what happens if you double X?", "plot Y
against Z"). These are the open-ended hooks.

## Extension ideas
Two or three harder variants or cross-simulator follow-ons for fast finishers.

## Assessment criteria
A short checklist tailored to the project. Simulation projects are assessed on:
- **Reproducibility** — set `random_seed`; same seed gives identical results.
- **Validation** — the result matches a known analytic value or qualitative law.
- **Analysis** — plots/numbers are interpreted, not just produced.
- **Code quality** — clean, parameterised, no magic numbers.
```

## Style notes for authors

- **Every example is reproducible.** Always pass `random_seed=42` (or similar) so
  an instructor running a student's notebook gets the same numbers. State the seed
  in the instructions.
- **Keep starter code plain.** Examples use simple Python; resist adding type
  hints, error handling, or abstractions that obscure the simulation idea. (A
  type-hints pass is a ready-made extension for stronger students.)
- **Validate against theory where possible.** Most simulators have a known
  analytic answer or qualitative law to compare against — name it (e.g. M/M/1
  utilization ρ = λ/(cμ); Lotka-Volterra equilibrium; exponential decay A(t) =
  A₀e^(−kt)). This is what makes a simulation project assessable.
- **One simulator per project** unless the project is explicitly about combining
  two (e.g. SIR-on-Network). Cross-refer the simulator's doc page.
- **Time estimates** assume a student who has read the simulator's documentation
  page. Beginner ≈ 20-30 min, Intermediate ≈ 40-60 min, Advanced ≈ 60-90 min.
