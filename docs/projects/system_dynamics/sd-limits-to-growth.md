# Limits to Growth

**Difficulty**: Intermediate
**Time**: ~45 minutes
**Learning Focus**: exponential vs logistic growth; carrying capacity and feedback structure
**Simulator**: SystemDynamicsSimulation (registry `"SystemDynamics"`)

## Overview
A population with a constant per-capita birth rate grows **exponentially** — forever. Real populations hit a ceiling: as crowding rises, the net growth rate falls, producing the S-shaped **logistic** curve that settles at a carrying capacity `K`. You will encode both dynamics as a single stock driven by one flow, overlay them, and confirm that the logistic run levels off at `K` while the exponential run diverges — and that each matches its closed-form solution.

## Setup
Install sim-lab (`pip install sim_lab`) and work in a Jupyter notebook, using the `SystemDynamicsSimulation` interface. See the [System Dynamics doc page](../../simulations/system_dynamics/system_dynamics.md).

## Instructions

1. **Set the growth parameters.** A single stock `population` accumulates quantity; one inflow `flow_from_env_to_population` sets its derivative (`env` is not a declared stock, so it acts as the infinite "cloud" source of system-dynamics diagrams).

```python
from sim_lab.core import SystemDynamicsSimulation, Stock, Flow
import matplotlib.pyplot as plt
import numpy as np

P0 = 10.0          # starting population
r = 0.1            # intrinsic growth rate
K = 1000.0         # carrying capacity (logistic only)
HORIZON = 100
```

2. **Build the two models.** In the exponential run the flow rate is `r·P`; in the logistic run it is `r·P·(1 − P/K)` — the extra `(1 − P/K)` factor is the density-dependent braking that creates the carrying capacity.

```python
def build_population(mode, days, dt):
    stocks = {"population": Stock("population", P0)}

    if mode == "exponential":
        def growth(state, t):
            return r * state["population"]
    elif mode == "logistic":
        def growth(state, t):
            P = state["population"]
            return r * P * (1 - P / K)

    flows = {"flow_from_env_to_population": Flow("flow_from_env_to_population", growth)}

    return SystemDynamicsSimulation(
        stocks=stocks, flows=flows,
        days=days, dt=dt,
        integration_method="RK45",
        random_seed=42,
    )

dt = 0.1
sim_exp = build_population("exponential", int(HORIZON / dt), dt)
sim_log = build_population("logistic",    int(HORIZON / dt), dt)
sim_exp.run_simulation()
sim_log.run_simulation()
```

3. **Overlay both trajectories.** `sim.results[:, 0]` is the single `population` stock, aligned with `sim.time_points`.

```python
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(sim_exp.time_points, sim_exp.results[:, 0], label="Exponential  dP/dt = rP")
ax.plot(sim_log.time_points, sim_log.results[:, 0], label="Logistic  dP/dt = rP(1 − P/K)")
ax.axhline(K, color="grey", ls=":", label=f"Carrying capacity K = {K:.0f}")
ax.set_xlabel("Time"); ax.set_ylabel("Population"); ax.legend()
ax.set_title("Exponential vs logistic growth"); plt.show()
```

4. **Validate against the closed-form solutions.** The analytic curves are `P0·e^{rt}` for exponential and `K / (1 + ((K−P0)/P0)·e^{−rt})` for logistic. Plot them on top of the simulated points.

```python
t = sim_exp.time_points
exp_analytic = P0 * np.exp(r * t)
log_analytic = K / (1 + ((K - P0) / P0) * np.exp(-r * t))

print("exponential max relative error:", np.max(np.abs(sim_exp.results[:, 0] - exp_analytic) / exp_analytic))
print("logistic max relative error:   ", np.max(np.abs(sim_log.results[:, 0] - log_analytic) / log_analytic))
# (Both should be ~1e-3 — RK45's default solver tolerance. Use relative error because the
# exponential run spans many orders of magnitude.)
```

5. **Confirm the two headline behaviours.** The logistic stock must level off at `K`; the exponential stock must overshoot it dramatically.

```python
print("logistic final value:", sim_log.results[-1, 0], " (should approach K =", K, ")")
print("exponential final value:", sim_exp.results[-1, 0], " (should far exceed K)")
```

## Things to explore
- Halve `r`. How does the logistic curve's *shape* change compared with merely scaling the time axis?
- Push `P0` above `K`. Does the logistic stock still converge to `K`, and from which direction?
- At `P0 = K`, what is the flow rate? Does the stock move at all — and why?
- Add a `flow_from_population_to_env` death outflow at rate `d·P`. What is the new effective growth rate and carrying capacity?

## Extension ideas
- Introduce a **delayed** braking term — e.g. logistic feedback based on the population one time unit ago — to provoke overshoot-and-collapse (a "limits to growth" scenario).
- Couple two logistic stocks with a shared resource auxiliary and watch one drive the other below its solo carrying capacity.
- Re-run the logistic model with Euler at increasing `dt` and find the step size at which Euler overshoots `K` and oscillates. Why does RK45 not do this?

## Assessment criteria
- **Reproducibility** — `random_seed=42` is set; both runs are repeatable to the last digit.
- **Validation (logistic levelling)** — the logistic trajectory is shown to approach `K` (final value within a few percent of `K`).
- **Validation (exponential divergence)** — the exponential trajectory is shown to exceed `K` by a large factor and to match `P0·e^{rt}` to high accuracy.
- **Validation (closed form)** — simulated curves are compared quantitatively (max error reported) to `P0·e^{rt}` and the logistic analytic solution.
- **Analysis** — the student identifies the `(1 − P/K)` factor as the density-dependent feedback that turns divergence into saturation.
- **Code quality** — a single parameterised `build_population(mode, ...)` builds both models; no duplicated stock/flow boilerplate.
