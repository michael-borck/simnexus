# Herd Immunity Threshold

**Difficulty**: Intermediate
**Time**: ~50 minutes
**Learning Focus**: the basic reproduction number $R_0$, the herd-immunity threshold $1-1/R_0$
**Simulator**: `EpidemiologicalSimulation` (registry `"Epidemiological"`)

## Overview

A vaccine does not have to reach every person to stop an outbreak — once enough of the population is immune, each infected person passes the disease on to fewer than one other on average, and the epidemic dies out. This project asks: **what fraction of a population must be immune for an epidemic to fizzle, and how does that fraction relate to $R_0$?** You will pre-immunise part of the population, sweep $R_0 = \beta/\gamma$, and find the vaccination fraction $p > 1 - 1/R_0$ at which the infected curve never takes off.

## Setup

Install sim-lab and use the `EpidemiologicalSimulation` class directly. See the
[Epidemiological Simulation docs](../../simulations/domain_specific/epidemiological.md)
for the full parameter reference.

```bash
pip install sim_lab
```

## Instructions

1. **Set up a clearly growing epidemic.** With $\beta=0.3$, $\gamma=0.1$ you get
   $R_0 = 3$ and a herd-immunity threshold of $1 - 1/R_0 = 66.7\%$. Run the model
   with no prior immunity and confirm the outbreak takes off.

   ```python
   from sim_lab.core import EpidemiologicalSimulation
   import matplotlib.pyplot as plt

   N = 10000
   sim = EpidemiologicalSimulation(
       population_size=N,
       initial_infected=100,
       initial_recovered=0,   # nobody immune yet
       beta=0.3,
       gamma=0.1,             # R0 = beta/gamma = 3.0
       days=180,
       random_seed=42,
   )
   sim.run_simulation()
   peak_day, peak = sim.get_peak_infection()
   print("R0 =", sim.get_reproduction_number())
   print("herd threshold 1 - 1/R0 =", 1 - 1 / sim.get_reproduction_number())
   print("peak infected =", round(peak, 1), "on day", peak_day)
   ```

2. **Pre-immunise the population with `initial_recovered`.** Vaccinating a fraction
   $p$ moves $p \cdot N$ people straight into the recovered compartment and
   reduces the initial susceptibles to $S_0 = N(1 - p) - I_0$. Try a fraction
   *below* the threshold first ($p = 0.5$) and watch the outbreak still grow.

   ```python
   p = 0.50
   sim = EpidemiologicalSimulation(
       population_size=N,
       initial_infected=100,
       initial_recovered=int(p * N),   # 50% pre-immune
       beta=0.3,
       gamma=0.1,
       days=180,
       random_seed=42,
   )
   sim.run_simulation()
   peak_day, peak = sim.get_peak_infection()
   final = sim.get_final_sizes()
   print("vaccinated", int(p * 100), "% -> peak =", round(peak, 1), "on day", peak_day)
   ```

3. **Sweep the vaccination fraction across the threshold.** Loop over several
   values of $p$ from $0$ to $0.85$, run each, and record the peak infection. The
   outbreak should collapse (peak stays at the initial infected count) once
   $S_0/N$ drops below $1/R_0 = 1/3$.

   ```python
   fractions = [0.0, 0.5, 0.6, 0.667, 0.70, 0.80, 0.85]
   rows = []
   for p in fractions:
       sim = EpidemiologicalSimulation(
           population_size=N,
           initial_infected=100,
           initial_recovered=int(p * N),
           beta=0.3,
           gamma=0.1,
           days=180,
           random_seed=42,
       )
       sim.run_simulation()
       _, peak = sim.get_peak_infection()
       s0_over_n = (N - 100 - int(p * N)) / N
       rows.append((p, s0_over_n, peak))

   print("frac  S0/N   1/R0   peak")
   for p, s, peak in rows:
       print(f"{p:.3f}  {s:.3f}  {1/3:.3f}  {peak:8.1f}")
   ```

4. **Find the critical vaccination fraction.** Identify the smallest $p$ at which
   the peak no longer rises above the initial infected count (the curve only ever
   declines). Compare it with the analytic threshold $1 - 1/R_0$.

5. **Cross-check at a second $R_0$.** Repeat the sweep with $\beta=0.4$, $\gamma=0.1$
   ($R_0 = 4$, threshold $1 - 1/4 = 75\%$) and confirm the tipping point shifts to
   the new $1 - 1/R_0$.

6. **Plot it.** Overlay the infected curves for $p = 0$, $0.5$, and $0.7$ on one
   axes to show the outbreak shrinking and finally disappearing as $p$ crosses the
   threshold.

## Things to explore

- What happens exactly *at* the threshold ($p = 1 - 1/R_0$)? Is the outbreak
  suppressed, or does the discrete-time model wobble around the tipping point?
- How does the *final attack rate* (total ever infected, i.e. final recovered minus
  the pre-immune) fall as $p$ approaches the threshold?
- If you halve $\gamma$ (people stay infectious twice as long), does the required
  vaccination fraction rise or fall? Why?
- Instead of vaccinating, set `initial_recovered` to model *natural immunity* from
  a prior wave — is the threshold the same?

## Extension ideas

- Derive the threshold from the **effective reproduction number**
  $\mathcal{R}_t = R_0 \cdot S_t/N$: show analytically that the epidemic shrinks
  once $\mathcal{R}_t < 1$, i.e. $S_t/N < 1/R_0$.
- Repeat the whole sweep for an $R_0$ typical of measles ($\approx 15$) versus
  seasonal flu ($\approx 1.3$) and discuss why some diseases need near-universal
  coverage.
- Turn vaccination into an *imperfect* intervention by also reducing $\beta$ for
  the vaccinated — how does a leaky vaccine change the threshold?

## Assessment criteria

- [ ] **Reproducibility** — `random_seed=42` is set on every run; re-running the
      notebook reproduces identical peak values and curves.
- [ ] **Validation** — the critical vaccination fraction found by the sweep matches
      the herd-immunity threshold $1 - 1/R_0$ to within the model's resolution, and
      the student explicitly states the rule: *the outbreak dies out once the
      susceptible fraction $S_0/N$ falls below $1/R_0$*. Verified at two values of
      $R_0$ (e.g. $R_0=3$ and $R_0=4$).
- [ ] **Analysis** — the overlaid plot is interpreted: why the peak collapses above
      the threshold, why it grows below it, and what the small deviations from the
      analytic threshold mean.
- [ ] **Code quality** — the sweep is a parameterised loop (no magic numbers
      repeated per scenario); the SIR API (`get_peak_infection`,
      `get_reproduction_number`, `get_final_sizes`) is used rather than re-reading
      raw compartments by hand.
