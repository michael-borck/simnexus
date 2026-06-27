# Predator-Prey Simulation

## Purpose

This simulation models the coupled dynamics of a prey species and its predator using the classic **Lotka-Volterra** equations. It lets students explore why predator and prey populations rise and fall in characteristic, lagged cycles, and how the four ecological rates that govern those cycles interact. It is a foundational teaching tool for nonlinear dynamics, phase-portrait analysis, and the intuition behind equilibrium and stability in interacting populations.

## Parameters

- `initial_prey` (`float`): Initial prey population size.
- `initial_predators` (`float`): Initial predator population size.
- `prey_growth_rate` (`float`): Natural per-capita growth rate of prey in the absence of predators ($\alpha$).
- `predation_rate` (`float`): Rate at which predators encounter and consume prey ($\beta$).
- `predator_death_rate` (`float`): Natural per-capita death rate of predators when no prey are available ($\gamma$).
- `predator_growth_factor` (`float`): Efficiency with which consumed prey are converted into new predators ($\delta$).
- `carrying_capacity` (`float`, optional): Environmental carrying capacity for the prey; when set, prey growth becomes logistic. Default `None`.
- `competition_factor` (`float`, optional): Intraspecies competition coefficient; when set, a density-dependent loss term is subtracted from both populations. Default `None`.
- `days` (`int`): Number of days to simulate. Default `100`.
- `dt` (`float`): Time step used by the explicit Euler integrator. Default `0.1`.
- `stochastic` (`bool`): When `True`, Gaussian noise is added to each step's derivatives. Default `False`.
- `random_seed` (`int`, optional): Seed for reproducible stochastic runs. Default `None`.

**Factory function — `create_predator_prey_model`**

A convenience constructor (also importable from `sim_lab.core`) that returns a preconfigured `PredatorPreySimulation` for common variants:

- `model_type` (`str`): one of `"basic"`, `"logistic"`, `"stochastic"`, `"competition"`. Default `"basic"`.
- `initial_prey` (`float`): default `100`.
- `initial_predators` (`float`): default `20`.
- `days` (`int`): default `100`.
- Additional rates may be supplied through `**kwargs`. Each variant supplies sensible defaults — `prey_growth_rate=0.1`, `predation_rate=0.01`, `predator_death_rate=0.05`, `predator_growth_factor=0.005` — with `"logistic"` adding `carrying_capacity=1000`, `"stochastic"` enabling noise, and `"competition"` adding `competition_factor=0.001`.

The simulator is registered as `"PredatorPrey"`, so you may also build it with `SimulatorRegistry.create("PredatorPrey", ...)`.

## Example Code

```python
from sim_lab.core import PredatorPreySimulation
import matplotlib.pyplot as plt

# Classic Lotka-Volterra scenario: prey (e.g. rabbits) and predators (e.g. foxes).
sim = PredatorPreySimulation(
    initial_prey=120,
    initial_predators=40,
    prey_growth_rate=0.1,          # alpha: prey birth rate
    predation_rate=0.002,          # beta: prey lost per predator encounter
    predator_death_rate=0.1,       # gamma: predator death rate without food
    predator_growth_factor=0.001,  # delta: prey-to-predator conversion
    days=100,
    dt=0.02,
)

results = sim.run_simulation()
prey = results["prey"]
predators = results["predators"]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

# Left: population time series — note the characteristic lagged cycles.
ax1.plot(prey, label="Prey", color="tab:green")
ax1.plot(predators, label="Predators", color="tab:red")
ax1.set_xlabel("Days")
ax1.set_ylabel("Population")
ax1.set_title("Population Dynamics Over Time")
ax1.legend()

# Right: cyclic phase portrait (predators vs prey).
ax2.plot(prey, predators, color="tab:blue", label="Trajectory")

# Non-trivial equilibrium: prey* = gamma / delta, predator* = alpha / beta.
eq_prey = sim.predator_death_rate / sim.predator_growth_factor
eq_predators = sim.prey_growth_rate / sim.predation_rate
ax2.scatter([eq_prey], [eq_predators], color="black", zorder=5, label="Equilibrium")

ax2.set_xlabel("Prey population")
ax2.set_ylabel("Predator population")
ax2.set_title("Phase Portrait (Cyclic Orbit)")
ax2.legend()

plt.tight_layout()
plt.show()
```

## Use Case Ideas

### Investigate Population Cycles and Phase Lag

Begin by running the basic model and observing how the two populations oscillate, with predator peaks consistently trailing prey peaks. Questions to Consider:

  - Why do predator peaks follow prey peaks with a consistent time lag rather than occurring simultaneously?

  - How does the amplitude of the cycle change when you vary the initial populations while keeping the rates fixed?

  - What does the shape of the orbit in the phase portrait tell you about the relationship between the two species?

### Investigate the Effect of Predation and Growth Rates

Hold the initial populations fixed and sweep the four rate parameters one at a time to see how each reshapes the cycle. Questions to Consider:

  - How does increasing `predation_rate` move the equilibrium point and alter the size of the orbit?

  - What happens to the cycle period as `prey_growth_rate` rises?

  - If predators convert prey into offspring more efficiently (higher `predator_growth_factor`), does the system become more or less stable?

### Investigate Stability: Carrying Capacity, Competition, and Noise

Extend the basic model with `carrying_capacity`, `competition_factor`, and `stochastic=True` to study how the closed orbit breaks down. Questions to Consider:

  - How does adding a `carrying_capacity` (logistic prey growth) turn a closed cycle into a spiral that settles toward equilibrium?

  - Does intraspecies `competition_factor` dampen the oscillations or shift the equilibrium?

  - Under `stochastic=True`, does environmental noise eventually destroy the cycle, and how does the time step `dt` affect numerical drift over long runs?

## Model Description

The `PredatorPreySimulation` class integrates the **Lotka-Volterra** coupled ordinary differential equations, the canonical model of an autonomous prey-predator pair. Let $x$ denote the prey population and $y$ the predator population. With rates $\alpha$ (`prey_growth_rate`), $\beta$ (`predation_rate`), $\gamma$ (`predator_death_rate`), and $\delta$ (`predator_growth_factor`), the dynamics are:

- Prey growth minus loss to predation: $\frac{dx}{dt} = \alpha x - \beta x y$
- Predator gain from feeding minus natural death: $\frac{dy}{dt} = \delta x y - \gamma y$

These are implemented verbatim in `get_derivatives`. The prey term $\beta x y$ couples the equations: abundant prey fuels predator growth, which then suppresses prey, which in turn starves predators — producing the closed, counter-rotating cycles visible in the phase portrait.

**Numerical integration.** Each `step()` advances both populations with the explicit (forward) Euler method:

$$x_{n+1} = \max\!\left(0,\; x_n + \frac{dx}{dt}\,\Delta t\right), \qquad y_{n+1} = \max\!\left(0,\; y_n + \frac{dy}{dt}\,\Delta t\right)$$

The $\max(0,\cdot)$ guard keeps populations non-negative. `run_simulation()` resets state, takes `int(days / dt)` steps, and returns `{"prey": [...], "predators": [...]}` sampled down to one value per simulated day.

**Optional extensions.** When `carrying_capacity` $K$ is set, prey growth becomes logistic by subtracting $\alpha x^2 / K$. When `competition_factor` $c$ is set, a density-dependent loss $c x^2$ is subtracted from prey and $c y^2$ from predators. With `stochastic=True`, Gaussian noise $\mathcal{N}(0,\,0.05\cdot\text{population})$ is added to each derivative before the Euler update.

**Equilibrium.** Setting both derivatives to zero gives the trivial extinction point $(0,0)$ plus the coexistence equilibrium, computed by `get_equilibrium_points()`:

$$x^{*} = \frac{\gamma}{\delta}, \qquad y^{*} = \frac{\alpha}{\beta}$$

In the pure Lotka-Volterra model the trajectory orbits this point indefinitely, which is exactly the cyclic phase portrait plotted above.

See `src/sim_lab/core/predator_prey_simulation.py` for the full implementation, including `get_phase_diagram()` for the underlying vector field.
