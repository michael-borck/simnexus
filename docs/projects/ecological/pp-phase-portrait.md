# Predator-Prey Phase Portrait

**Difficulty**: Intermediate
**Time**: ~45 minutes
**Learning Focus**: Lotka–Volterra dynamics; phase-portrait analysis and the coexistence equilibrium
**Simulator**: PredatorPreySimulation (registry `"PredatorPrey"`)

## Overview
The Lotka–Volterra equations predict that prey and predators chase each other in endless, lagged cycles — and that in a *phase portrait* (predators plotted against prey) those cycles show up as **closed orbits encircling a fixed equilibrium point**. You will run the basic model, draw its phase portrait, mark the coexistence equilibrium, and verify that the trajectory loops around that point instead of spiralling in or out.

## Setup
Install sim-lab (`pip install sim_lab`) and use a Jupyter notebook with the `PredatorPreySimulation` class. See the [Predator-Prey doc page](../../simulations/ecological/predator_prey.md).

## Instructions

1. **Configure a classic prey–predator pair and run it.** With the simulator's parameter names the dynamics are `dx/dt = α·x − β·x·y` (prey) and `dy/dt = δ·x·y − γ·y` (predators), where `α` = `prey_growth_rate`, `β` = `predation_rate`, `γ` = `predator_death_rate`, `δ` = `predator_growth_factor`. A small `dt` keeps the Euler integrator's drift low so the orbit looks clean.

```python
from sim_lab.core import PredatorPreySimulation
import matplotlib.pyplot as plt
import numpy as np

sim = PredatorPreySimulation(
    initial_prey=120, initial_predators=40,
    prey_growth_rate=0.1,        # alpha
    predation_rate=0.002,        # beta
    predator_death_rate=0.1,     # gamma
    predator_growth_factor=0.001,# delta
    days=300, dt=0.01,
    random_seed=42,
)
results = sim.run_simulation()
prey, predators = results["prey"], results["predators"]
```

2. **Locate the coexistence equilibrium.** Setting both derivatives to zero gives the fixed point `(γ/δ, α/β)` — in parameter names, `prey* = predator_death_rate / predator_growth_factor` and `predator* = prey_growth_rate / predation_rate`. The simulator's `get_equilibrium_points()` returns exactly this (plus the trivial `(0, 0)`).

```python
eq_prey = sim.predator_death_rate / sim.predator_growth_factor      # gamma / delta
eq_predators = sim.prey_growth_rate / sim.predation_rate            # alpha / beta
print("equilibrium from formula:", (eq_prey, eq_predators))
print("equilibrium from sim:    ", sim.get_equilibrium_points()[-1])  # coexistence point
```

3. **Draw the phase portrait with the equilibrium marked.**

```python
fig, ax = plt.subplots(figsize=(8, 7))
ax.plot(prey, predators, color="tab:blue", label="Trajectory")
ax.scatter([eq_prey], [eq_predators], color="black", zorder=5,
           label=f"Equilibrium ({eq_prey:.0f}, {eq_predators:.0f})")
ax.set_xlabel("Prey population"); ax.set_ylabel("Predator population")
ax.set_title("Lotka-Volterra phase portrait"); ax.legend(); plt.show()
```

4. **Validate that the orbit is closed.** A closed orbit (i) encircles the equilibrium and (ii) returns close to its starting point after each period. Estimate the cycle period from the prey time series, then check the gap between the trajectory's start and its position one period later.

```python
# Crude period estimate: time between successive prey maxima.
prey_arr = np.array(prey)
maxima = [i for i in range(1, len(prey_arr) - 1)
          if prey_arr[i] > prey_arr[i - 1] and prey_arr[i] > prey_arr[i + 1]]
period = maxima[1] - maxima[0] if len(maxima) >= 2 else None
print("estimated period (days):", period)

# Does the trajectory come back near its start after one period?
start = np.array([prey[0], predators[0]])
one_period_later = np.array([prey[period], predators[period]])
print("distance start -> start+1period:", np.linalg.norm(start - one_period_later))
print("(small relative to orbit size => orbit is approximately closed)")
```

5. **(Optional) Add the vector field as background.** `get_phase_diagram()` returns a grid of `(dx/dt, dy/dt)` arrows that shows *why* the trajectory curls around the equilibrium.

```python
field = sim.get_phase_diagram(num_points=20)
ax.quiver(field["X"], field["Y"], field["U"], field["V"], color="lightgrey", alpha=0.6)
```

## Things to explore
- The forward-Euler integrator slowly *gains* energy on this system, so the orbit drifts outward over many cycles. Halve `dt` (to `0.005`) and double `days` — does the spiral tighten?
- Start exactly on the equilibrium `(100, 50)`. Does the stock stay put, or does numerical noise start a tiny orbit?
- Sweep `prey_growth_rate` and watch how the cycle *period* (≈ `2π/√(α·γ)`) scales.
- Move the initial condition closer to, then farther from, the equilibrium. How does the orbit's radius respond?

## Extension ideas
- Turn on logistic prey growth with `carrying_capacity`. The closed orbit should collapse into a spiral that settles onto a new equilibrium — confirm it and plot both portraits side by side.
- Run two trajectories from different initial conditions on the same axes and show that each traces its *own* closed orbit around the shared equilibrium.
- Replace Euler with an RK4 integrator written by hand (the simulator exposes `get_derivatives`). Does RK4 preserve the closed orbit noticeably better than Euler over the same horizon?

## Assessment criteria
- **Reproducibility** — `random_seed=42` is set; the run is repeatable to the last value.
- **Validation (equilibrium)** — the equilibrium marked on the portrait equals `γ/δ` = `predator_death_rate / predator_growth_factor` for prey and `α/β` = `prey_growth_rate / predation_rate` for predators (and matches `get_equilibrium_points()`).
- **Validation (closed orbits)** — the trajectory is shown to encircle the equilibrium and to return near its starting point after one period (start-to-start+period distance small relative to the orbit radius).
- **Analysis** — the student explains the direction of rotation (prey boom → predator boom → prey crash → predator crash) and notes the Euler outward drift as a numerical artefact, not model behaviour.
- **Code quality** — the equilibrium is computed from parameters (not hardcoded numbers); plotting is separated from the simulation logic.
