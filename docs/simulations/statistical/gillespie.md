# Gillespie SSA Simulation

## Purpose

This simulation implements the original Gillespie (1977) stochastic simulation algorithm (SSA), the canonical exact method for simulating the time evolution of well-mixed chemical kinetics. Rather than approximating reactions with continuous differential equations, the SSA samples each individual reaction event from the correct probability distribution, capturing the intrinsic noise and discreteness that dominate when molecule counts are small. It is an ideal teaching tool for illustrating where deterministic rate equations break down and how identical systems can follow markedly different trajectories purely due to chance.

## Parameters

- `species_names` (`List[str]`): Names of the chemical species. The order of this list defines the vector ordering used everywhere else (stoichiometry entries, counts, and propensities all index species by position).
- `initial_counts` (`List[int]`): Initial molecule count for each species, in the same order as `species_names`. Must be the same length as `species_names`.
- `reactions` (`List[Reaction]`): The reactions defining the system. Each `Reaction` carries a `stoichiometry` vector (net change in each species when the reaction fires once; negative = consumed, positive = produced), a `propensity_function` (a callable taking the current count vector and returning the reaction propensity), and an optional `name`.
- `max_time` (`float`, default `10.0`): The simulated time horizon. The run stops when simulated time reaches this value.
- `days` (`int`, default `100000`): Repurposed as the **maximum number of reaction events** (a safety cap). The natural stop condition is `max_time`; this guards against runaway systems with very small molecule counts or fast rates.
- `random_seed` (`Optional[int]`, default `None`): Seed for the random number generator. Set it for reproducible trajectories.

## Example Code

```python
from sim_lab.core import GillespieSSASimulation, Reaction
import matplotlib.pyplot as plt

# Simple birth-death model: X is produced (birth) and degraded (death).
reactions = [
    Reaction(stoichiometry=[+1], propensity_function=lambda s: 1.0, name="birth"),
    Reaction(stoichiometry=[-1], propensity_function=lambda s: 0.05 * s[0], name="death"),
]

sim = GillespieSSASimulation(
    species_names=["X"],
    initial_counts=[20],
    reactions=reactions,
    max_time=50.0,
    days=20000,
    random_seed=42,
)

sim.run_simulation()
times = sim.get_times()
x_counts = sim.get_species("X")
stats = sim.get_statistics()

print("Final statistics:", stats)

# Plot the stochastic trajectory
plt.figure(figsize=(10, 6))
plt.step(times, x_counts, where="post", label="X (SSA trajectory)")
plt.xlabel("Time")
plt.ylabel("Molecule count")
plt.title("Gillespie SSA: Birth-Death Model")
plt.legend()
plt.show()
```

For the textbook decay example $A \to B$, the `create_decay_model` factory builds the model directly:

```python
from sim_lab.core import create_decay_model

sim = create_decay_model(a0=100, rate=0.1, max_time=50.0, random_seed=42)
sim.run_simulation()
```

## Use Case Ideas

### Investigate Noise in Systems with Small Molecule Counts

Run the birth-death model with a large versus a small initial count and compare the smoothness of the trajectories. Questions to Consider:

  - How does the relative size of fluctuations scale with the molecule count?

  - At what count does the deterministic mean-field prediction become a poor description of any single trajectory?

### Simulate First-Order Decay and Compare to the Analytic Solution

Use the `create_decay_model` factory (reaction $A \to B$ with propensity $k\,A$) and overlay the deterministic solution $A(t) = A_0\,e^{-k t}$ on the stochastic trajectory. Questions to Consider:

  - Does the SSA trajectory track the exponential curve, and where do the largest deviations occur?

  - Run several replicas with different `random_seed` values — how does their ensemble mean compare to the ODE solution?

### Explore Multistability and Extinction

Define a system with nonlinear propensities (e.g. an autocatalytic birth term proportional to $X$ or $X^2$) and observe threshold behavior or extinction events. Questions to Consider:

  - Can a trajectory reach an absorbing state (zero propensity) where the deterministic ODE would predict persistent growth?

  - How does the time to extinction vary with the initial count and the reaction rate?

## Model Description

The Gillespie SSA is built on the **chemical master equation**: the state of the system is the integer count vector $\mathbf{x} = (x_1, \dots, x_N)$, and each reaction $j$ changes the state by its stoichiometric vector $\boldsymbol{\nu}_j$ when it fires. Each reaction has a **propensity** $a_j(\mathbf{x})$, the probability per unit time that reaction $j$ occurs next given the current counts.

The **direct method** advances the system one reaction at a time. With the total propensity

$$a_0(\mathbf{x}) = \sum_{j} a_j(\mathbf{x}),$$

the time to the next reaction is drawn as

$$\tau \sim \mathrm{Exponential}(a_0),$$

and the firing reaction is chosen with probability

$$P(\text{reaction } j) = \frac{a_j(\mathbf{x})}{a_0(\mathbf{x})}.$$

Once reaction $j$ is chosen, the state is updated by $\mathbf{x} \leftarrow \mathbf{x} + \boldsymbol{\nu}_j$ and the clock advanced by $\tau$. This loop repeats until either the simulated time reaches `max_time` or the event cap `days` is hit. If $a_0 = 0$ the system has reached an **absorbing state** and the run halts early.

In the source, `tau` is realised as `-log(r1) / a0` from a uniform draw $r_1 \in (0,1)$, and the reaction is selected by a linear scan over the cumulative propensity until it exceeds the threshold `r2 * a0` (`gillespie_simulation.py`, `run_simulation`). The recorded `times` always begin at $t = 0$, and the `trajectory` records a full count-vector snapshot at every event time.

**Stochastic SSA vs. deterministic ODE rate equations.** The deterministic rate equations approximate the mean behaviour as

$$\frac{d\mathbf{x}}{dt} = \sum_{j} \boldsymbol{\nu}_j\, a_j(\mathbf{x}),$$

treating counts as continuous and ignoring fluctuations. For the decay model $A \to B$ this gives $A(t) = A_0\,e^{-k t}$. The SSA recovers this curve **in expectation** (the mean of many replicas converges to the ODE solution), and in the decay example it conserves $A + B = A_0$ exactly at every step. But any *single* SSA trajectory is a step function reflecting discrete, random events, and the deviations from the ODE — the intrinsic noise — are largest when molecule counts are small, precisely the regime where the continuous ODE approximation breaks down.
