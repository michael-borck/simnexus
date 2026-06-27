# Stochastic Lotka–Volterra (Predator–Prey)
**Difficulty**: Advanced
**Time**: ~75 minutes
**Learning Focus**: Stochastic reaction networks; intrinsic extinction in finite populations
**Simulator**: GillespieSSASimulation (registry `GillespieSSA`)
## Overview
The Lotka–Volterra predator–prey model captures the boom-and-bust cycles of predators and their prey. In its deterministic form the two populations orbit a fixed equilibrium forever. In the *stochastic* form — where each birth, predation, and death is an individual random event — the very same rules can drive a population to zero, ending the system. The central question: do stochastic trajectories orbit the deterministic equilibrium, and how does the risk of extinction grow when populations are small?
## Setup
Install `sim-lab` and build the reactions by hand with `GillespieSSASimulation` and `Reaction`: `pip install sim-lab`.
## Instructions
1. Define the three reactions. `A` is prey, `B` is predator. Each `Reaction` takes a `stoichiometry` vector (net change to `[A, B]`) and a `propensity_function` (reaction rate given the current counts). The predation reaction shares one rate for the prey loss and predator gain, so the deterministic equilibrium simplifies to $A^* = \gamma/\beta$, $B^* = \alpha/\beta$.

```python
import numpy as np
from sim_lab.core import GillespieSSASimulation, Reaction

alpha = 1.0    # prey birth rate
beta  = 0.01   # predation rate (A eaten, B born)
gamma = 1.0    # predator death rate

reactions = [
    Reaction(stoichiometry=[+1, 0], propensity_function=lambda s: alpha * s[0],
             name="prey_birth"),                       # A -> 2A
    Reaction(stoichiometry=[-1, +1], propensity_function=lambda s: beta * s[0] * s[1],
             name="predation"),                        # A + B -> 2B
    Reaction(stoichiometry=[0, -1], propensity_function=lambda s: gamma * s[1],
             name="predator_death"),                   # B -> 0
]
```

2. Build the simulator with a reasonably large starting population so the orbits are visible, and run it with a fixed seed.

```python
A0, B0 = 100, 50
sim = GillespieSSASimulation(
    species_names=["A", "B"],
    initial_counts=[A0, B0],
    reactions=reactions,
    max_time=30.0,
    days=200000,
    random_seed=42,
)
sim.run_simulation()
times = sim.get_times()
A = sim.get_species("A")
B = sim.get_species("B")
```

3. Locate the deterministic equilibrium and **validate** that the stochastic trajectory orbits around it. With a single predation rate, the equilibrium is $A^* = \gamma/\beta$, $B^* = \alpha/\beta$.

```python
A_star, B_star = gamma / beta, alpha / beta
print(f"Deterministic equilibrium: A*={A_star:.1f}, B*={B_star:.1f}")
print(f"Mean A over run: {np.mean(A):.1f},  Mean B over run: {np.mean(B):.1f}")
```

4. Measure extinction risk. Run many replicas with different seeds; extinction occurs when a species hits 0 (and its propensity can no longer fire). Compare the extinction probability at a *large* starting population versus a *small* one.

```python
def extinction_probability(a0, b0, n_runs=100):
    extinct = 0
    for seed in range(n_runs):
        s = GillespieSSASimulation(
            species_names=["A", "B"], initial_counts=[a0, b0],
            reactions=reactions, max_time=50.0, days=200000, random_seed=seed,
        )
        s.run_simulation()
        if s.get_species("A")[-1] == 0 or s.get_species("B")[-1] == 0:
            extinct += 1
    return extinct / n_runs

print("Large pop (100,50):", extinction_probability(100, 50))
print("Small pop  (10, 5):", extinction_probability(10, 5))
```
## Things to explore
- Plot `A` and `B` against time on the same axes: do you see the classic predator-prey oscillation, with predator peaks *lagging* prey peaks?
- Plot the trajectory in the $(A, B)$ phase plane alongside the equilibrium point $(A^*, B^*)$. Does the orbit spiral around it? Does it drift over very long runs?
- Holding the equilibrium fixed, scale both initial populations up by 10×. How does the extinction probability change? (Expect it to fall sharply.)
- Increase the run length `max_time` for a small population: does extinction become near-certain given enough time?
## Extension ideas
- Overlay the deterministic Lotka–Volterra ODE solution (integrate $dA/dt = \alpha A - \beta A B$, $dB/dt = \beta A B - \gamma B$ with a simple integrator) and compare the orbit shape and period to a single SSA trajectory.
- Add logistic self-limitation to the prey (cap births with a carrying capacity $K$) and show that the orbits dampen to a stable fixed point instead of cycling.
- Add immigration reactions ($\emptyset \to A$ and $\emptyset \to B$ with small constant propensities) and measure how they suppress extinction even at low populations.
## Assessment criteria
- [ ] **Reproducibility**: the reference trajectory and the extinction-probability loop both fix `random_seed` (42 for the single run, a per-run seed for the ensemble) so results are repeatable.
- [ ] **Validation — orbits around equilibrium**: the trajectory's mean counts bracket the deterministic equilibrium $(\gamma/\beta,\ \alpha/\beta)$, and the phase-plane orbit encircles it.
- [ ] **Validation — extinction rises at small populations**: extinction probability is shown to increase as the initial counts shrink, demonstrated across many seeds.
- [ ] **Analysis**: the write-up explains why the *stochastic* model can hit zero while the deterministic ODE orbits forever, and connects this to intrinsic noise in finite populations.
- [ ] **Code quality**: the three `Reaction` stoichiometries and propensities correctly encode birth, predation, and death, and `get_species` is used to read each population.
