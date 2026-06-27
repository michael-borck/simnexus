# Stochastic Decay vs the ODE Solution
**Difficulty**: Intermediate
**Time**: ~45 minutes
**Learning Focus**: Exact stochastic kinetics; ensemble averaging vs deterministic rate equations
**Simulator**: GillespieSSASimulation (registry `GillespieSSA`)
## Overview
A single molecule of `A` decays into `B` at random — you cannot predict *when* any one molecule reacts, only the rates. The Gillespie stochastic simulation algorithm (SSA) samples each individual reaction event from the correct distribution, producing a noisy, step-like trajectory. The deterministic ODE $A(t)=A_0 e^{-kt}$ instead describes the smooth *average* behavior. The central question: does averaging many independent SSA runs reproduce the ODE curve, and what does a *single* trajectory look like by comparison?
## Setup
Install `sim-lab` and use the `create_decay_model` factory: `pip install sim-lab`.
## Instructions
1. Build the decay model $A \to B$ with the factory: `a0` molecules of A, first-order rate `k`, running to `max_time`. Then run it once with a fixed seed and read off the time grid and species counts.

```python
import numpy as np
from sim_lab.core import create_decay_model

a0, k = 100, 0.1
sim = create_decay_model(a0=a0, rate=k, max_time=50.0, random_seed=42)
sim.run_simulation()

times = sim.get_times()
A = sim.get_species("A")
B = sim.get_species("B")
```

2. **Validate the conservation law**: at every recorded event time, $A + B$ must equal $A_0$ exactly (each decay converts one A into one B). Print the maximum deviation — it should be 0.

```python
total = np.array(A) + np.array(B)
print("Max |A+B - A0|:", np.max(np.abs(total - a0)))   # expect 0
```

3. Overlay the analytic ODE solution $A(t) = A_0 e^{-kt}$ on the single SSA trajectory to see the noise.

```python
ode = a0 * np.exp(-k * np.array(times))
# Plot sim.get_times() vs A (step plot) and times vs ode (line) to compare.
print("Final A (SSA):", A[-1], " Final A (ODE):", round(ode[-1], 2))
```

4. Average *many* independent runs to test whether the ensemble mean tracks the ODE. Each run needs a different seed; interpolate every trajectory onto a common time grid before averaging.

```python
grid = np.linspace(0, 50, 200)
n_runs = 200
A_runs = []
for seed in range(n_runs):
    s = create_decay_model(a0=a0, rate=k, max_time=50.0, random_seed=seed)
    s.run_simulation()
    A_runs.append(np.interp(grid, s.get_times(), s.get_species("A")))

A_mean = np.mean(A_runs, axis=0)
ode_grid = a0 * np.exp(-k * grid)
print("Max |ensemble mean - ODE|:", round(np.max(np.abs(A_mean - ode_grid)), 2))
```
## Things to explore
- Reduce `a0` to 10 (then 5). How does the single-trajectory noise change relative to the ODE curve? Where is the ODE approximation a poor description of any one run?
- At `a0=100`, plot a handful of individual trajectories in light grey behind the ensemble mean and the ODE. Does the mean sit on top of the ODE while the individuals scatter?
- Compare the spread (standard deviation across runs) of `A` over time to the theoretical Poisson noise $\sqrt{A(t)}$. Are they close?
- Double the rate `k`. Does the ensemble-mean-vs-ODE agreement change, or only the timescale?
## Extension ideas
- Estimate the distribution of the *time at which A first reaches 50* (its half-life) across many runs and compare its mean and spread to the deterministic half-life $\ln 2 / k$.
- Add a reverse reaction $B \to A$ and derive the new ODE equilibrium $A_{\text{eq}}/B_{\text{eq}}$; confirm the SSA ensemble mean converges to it.
- Replace first-order decay with a second-order dimerization $2A \to B$ (propensity $k\,A(A-1)/2$) and compare the stochastic mean to the (different) ODE solution.
## Assessment criteria
- [ ] **Reproducibility**: the single reference run uses `random_seed=42`, and the ensemble loop uses a seed-per-run so the whole study is repeatable.
- [ ] **Validation — conservation**: $A + B = A_0$ is verified exactly at every event time (max deviation reported as 0).
- [ ] **Validation — ensemble ≈ ODE**: the mean of many runs is shown to track $A_0 e^{-kt}$, with the max deviation reported and discussed.
- [ ] **Analysis**: the write-up contrasts a single noisy SSA trajectory with the smooth ODE and explains *why* the mean recovers the deterministic law.
- [ ] **Code quality**: `create_decay_model`, `get_species`, and `get_times` are used correctly, and trajectories are interpolated onto a common grid before averaging.
