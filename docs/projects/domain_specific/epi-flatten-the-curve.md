# Flatten the Curve

**Difficulty**: Beginner
**Time**: ~25 minutes
**Learning Focus**: the transmission rate $\beta$, peak infection vs. epidemic duration
**Simulator**: `EpidemiologicalSimulation` (registry `"Epidemiological"`)

## Overview

During an outbreak, hospitals can only treat so many patients at once. Public-health
measures like distancing, masking, and isolation do not necessarily *prevent*
infections so much as **spread them over time**, pushing the peak of the epidemic
below the capacity of the healthcare system. This project asks: **how does lowering
the transmission rate $\beta$ change the height and timing of the infection peak?**
You will run the SIR model at a few values of $\beta$ and show the curve
"flattening".

## Setup

Install sim-lab and use the `EpidemiologicalSimulation` class. See the
[Epidemiological Simulation docs](../../simulations/domain_specific/epidemiological.md)
for the parameter reference.

```bash
pip install sim_lab
```

## Instructions

1. **Run a baseline epidemic.** Start with a high transmission rate
   $\beta = 0.3$ and $\gamma = 0.1$ (so $R_0 = 3$). Run the model and note the
   peak infection and the day it occurs.

   ```python
   from sim_lab.core import EpidemiologicalSimulation
   import matplotlib.pyplot as plt

   N = 10000
   sim = EpidemiologicalSimulation(
       population_size=N,
       initial_infected=100,
       beta=0.3,
       gamma=0.1,        # R0 = beta/gamma = 3.0
       days=180,
       random_seed=42,
   )
   infected = sim.run_simulation()
   peak_day, peak = sim.get_peak_infection()
   print("baseline: peak =", round(peak, 1), "on day", peak_day)
   ```

2. **Lower $\beta$ to model distancing.** Drop $\beta$ from $0.3$ to $0.2$ (now
   $R_0 = 2$). Run again and compare — the peak should fall and arrive later.

   ```python
   sim2 = EpidemiologicalSimulation(
       population_size=N,
       initial_infected=100,
       beta=0.2,        # interventions cut transmission -> R0 = 2.0
       gamma=0.1,
       days=180,
       random_seed=42,
   )
   infected2 = sim2.run_simulation()
   peak_day2, peak2 = sim2.get_peak_infection()
   print("distancing: peak =", round(peak2, 1), "on day", peak_day2)
   print("peak reduction:", round(100 * (1 - peak2 / peak)), "%")
   ```

3. **Sweep several values of $\beta$.** Loop over `[0.30, 0.25, 0.20, 0.15]` and
   record the peak and the day it occurs for each. As $\beta$ falls, the peak
   should drop steadily and shift later in time.

   ```python
   days = range(180)
   results = []
   for beta in [0.30, 0.25, 0.20, 0.15]:
       sim = EpidemiologicalSimulation(
           population_size=N,
           initial_infected=100,
           beta=beta,
           gamma=0.1,
           days=180,
           random_seed=42,
       )
       sim.run_simulation()
       pd, pk = sim.get_peak_infection()
       total_infected = sim.get_final_sizes()["recovered"]
       results.append((beta, pd, pk, total_infected))
       plt.plot(days, sim.get_compartments()["infected"], label=f"beta={beta}")

   print("beta   peak_day   peak   total_ever_infected")
   for beta, pd, pk, tot in results:
       print(f"{beta:.2f}   {pd:6d}   {pk:7.1f}   {tot:8.0f}")
   plt.xlabel("Days"); plt.ylabel("Infected")
   plt.legend(); plt.title("Flattening the curve by lowering beta")
   plt.show()
   ```

4. **Compare the total ever-infected.** Look at the final recovered count for each
   run. As long as $R_0$ stays well above 1, the *total* number of people who
   eventually get infected changes only modestly even though the peak falls a lot —
   flattening mostly spreads the same burden over more days.

5. **Check the "equal $R_0$" case.** Run two epidemics that share the same
   $R_0 = 3$ but split $\beta$ and $\gamma$ differently — e.g.
   $(\beta,\gamma) = (0.3, 0.1)$ and $(0.45, 0.15)$. Their peaks differ, but the
   total ever-infected should be nearly identical, because the final attack rate is
   set by $R_0$, not by $\beta$ alone.

## Things to explore

- Draw a horizontal "hospital capacity" line on your plot. Which $\beta$ values
  keep the peak below it?
- What happens to the *duration* of the epidemic (the width of the infected curve)
  as $\beta$ drops?
- Push $\beta$ low enough that $R_0$ approaches 1. Does "flatten" become
  "suppress"? Where is the boundary?
- Keep $\beta = 0.3$ but raise $\gamma$ (faster recovery, e.g. better treatment).
  Does that flatten the curve the same way lowering $\beta$ does?

## Extension ideas

- Add a second plot of the *cumulative* infections for each $\beta$ and relate the
  final value to the herd-immunity threshold $1 - 1/R_0$.
- Model an *intermittent* lockdown: run with $\beta = 0.3$ for a stretch, then
  switch to $\beta = 0.15$ for a window, then back. How does the peak compare to a
  constant-$\beta$ run?
- Estimate the reproduction number from the early growth rate
  ($I_{t+1}/I_t$) and confirm it matches $R_0 = \beta/\gamma$ while susceptibles
  are still plentiful.

## Assessment criteria

- [ ] **Reproducibility** — `random_seed=42` is set on every run; re-running the
      notebook reproduces identical peak values and curves.
- [ ] **Validation** — the student shows that lowering $\beta$ lowers **and delays**
      the peak (e.g. $\beta: 0.30 \to 0.20$ drops the peak from ~3160 to ~1620 and
      pushes it from ~day 28 to ~day 45), **and** that two runs with the same
      $R_0 = 3$ reach a nearly identical total ever-infected (~9,500) — the peak is
      what flattens, the eventual attack rate (set by $R_0$) does not.
- [ ] **Analysis** — the flattened-curve plot is interpreted: why distancing lowers
      the peak, why it delays it, and why the total burden changes only modestly
      while $R_0 > 1$.
- [ ] **Code quality** — the $\beta$ sweep is a single parameterised loop; the SIR
      API (`run_simulation`, `get_peak_infection`, `get_final_sizes`) is used rather
      than indexing raw lists by hand.
