# Epidemiological Simulation

## Purpose

This simulation models the spread of an infectious disease through a population using the classic **SIR compartment model**, in which every individual belongs to one of three states: **S**usceptible, **I**nfected, or **R**ecovered. It lets students explore how transmission and recovery rates drive an epidemic, and how quantities such as the basic reproduction number $R_0$ and the herd-immunity threshold predict whether an outbreak will take off. Because the model is compact and its dynamics are governed by just two rates, it is an ideal vehicle for teaching concepts like *flatten-the-curve* and the tipping point at which an epidemic begins to fade.

## Parameters

- `population_size` (`int`): Total number of individuals in the population. Required.
- `initial_infected` (`int`): Number of individuals infected at the start of the simulation. Required.
- `initial_recovered` (`int`, default `0`): Number of individuals already recovered (and assumed immune) at the start.
- `beta` (`float`, default `0.3`): Transmission rate — the per-day rate at which susceptible individuals become infected through contact with infected individuals.
- `gamma` (`float`, default `0.1`): Recovery rate — the per-day rate at which infected individuals recover and move into the recovered compartment.
- `days` (`int`, default `100`): Number of days to simulate.
- `random_seed` (`Optional[int]`, default `None`): Seed for random number generation.

> **Note:** The SIR equations implemented here are fully deterministic, so `random_seed` does not change the resulting trajectory — it is accepted for API consistency with the rest of the toolkit. The constructor also enforces that `initial_infected + initial_recovered` must not exceed `population_size`, otherwise it raises a `ValueError`.

## Example Code

```python
from sim_lab.core import EpidemiologicalSimulation
import matplotlib.pyplot as plt

# Example scenario: a population of 1000 with 5 initial infections.
# beta=0.3, gamma=0.1 -> R0 = 3.0 (a clearly growing epidemic).
sim = EpidemiologicalSimulation(
    population_size=1000,
    initial_infected=5,
    initial_recovered=0,
    beta=0.3,
    gamma=0.1,
    days=100,
    random_seed=42,
)

# run_simulation() returns the infected count for each day.
infected = sim.run_simulation()

# Pull the full SIR time series and key summary statistics.
compartments = sim.get_compartments()
peak_day, peak_value = sim.get_peak_infection()
R0 = sim.get_reproduction_number()
final = sim.get_final_sizes()

print(f"R0 = {R0:.2f}   herd-immunity threshold = {1 - 1/R0:.0%}")
print(f"Peak infection on day {peak_day}: {peak_value:.1f} individuals")
print(f"Final sizes -> {final}")

# Visualise the three compartments over time.
days = range(len(infected))
plt.figure(figsize=(10, 6))
plt.plot(days, compartments["susceptible"], label="Susceptible")
plt.plot(days, compartments["infected"], label="Infected", color="red")
plt.plot(days, compartments["recovered"], label="Recovered", color="green")
plt.axvline(peak_day, color="grey", linestyle="--", alpha=0.7, label=f"Peak (day {peak_day})")
plt.xlabel("Days")
plt.ylabel("Number of individuals")
plt.title("SIR Epidemiological Simulation")
plt.legend()
plt.show()
```

## Use Case Ideas

### Investigate How $R_0$ Determines Whether an Epidemic Takes Off

The basic reproduction number $R_0 = \beta/\gamma$ is the expected number of new infections caused by a single infectious individual in an otherwise fully susceptible population. Sweep `beta` and `gamma` to cross the epidemic threshold. Questions to Consider:

  - With `beta=0.3, gamma=0.1` you get $R_0 = 3$. What happens to the infected curve when you lower `beta` until $R_0 \le 1$?
  - Does the infection still spread when $R_0 < 1$? Compare `get_peak_infection()` across a few $R_0$ values.
  - How does the initial growth of the infected compartment relate to $R_0$?

### Investigate Flatten-the-Curve Through Reduced Transmission

Public-health interventions (distancing, masking, isolation) effectively lower `beta`. Compare two simulations — one with interventions and one without — to see the trade-off between peak load and epidemic duration. Questions to Consider:

  - Lowering `beta` from `0.3` to `0.18` (keeping `gamma=0.1`) changes $R_0$ from 3 to 1.8. How much does the peak infection fall, and how much later does it occur?
  - Does the total number of people ever infected (final recovered count) change much when you only *delay* infections versus truly suppressing them?
  - What `beta` is required to bring $R_0$ close to 1 and "flatten" the curve to a manageable peak?

### Investigate Herd Immunity and the Role of Prior Immunity

The herd-immunity threshold $1 - 1/R_0$ is the fraction of the population that must be immune for the epidemic to decline. Use `initial_recovered` to pre-immunise part of the population (e.g. via vaccination). Questions to Consider:

  - With $R_0 = 3$, the threshold is $1 - 1/3 \approx 67\%$. Set `initial_recovered` above and below this fraction of `population_size` — how does the infected curve differ?
  - Is the analytical threshold exact in this discrete simulation, or is it approximate? Where do the small deviations come from?
  - What happens to `get_final_sizes()` as `initial_recovered` approaches the threshold?

## Model Description

The simulation implements the classic **SIR model** with three compartments and a fixed population of size $N$ (`population_size`):

$$\frac{dS}{dt} = -\beta \frac{S I}{N}, \qquad \frac{dI}{dt} = \beta \frac{S I}{N} - \gamma I, \qquad \frac{dR}{dt} = \gamma I$$

where $S + I + R = N$ is conserved. The class is documented for epidemiological models such as SIR and SEIR, but the current implementation solves the **SIR** system. The initial susceptible count is derived from the other inputs:

$$S_0 = N - I_0 - R_0$$

with $I_0$ = `initial_infected` and $R_0$ = `initial_recovered` (note: this $R_0$ is the initial *recovered* count, distinct from the reproduction number — the latter is written $\mathcal{R}_0$ or `R0` in the code).

Rather than solving the ODEs analytically, the simulation steps forward one day at a time using the explicit update rules defined in `run_simulation()` (a discrete-time / Euler integration with step $\Delta t = 1$ day):

$$\text{new\_infections} = \beta \cdot \frac{S_t \, I_t}{N}, \qquad \text{new\_recoveries} = \gamma \cdot I_t$$

$$S_{t+1} = S_t - \text{new\_infections}, \quad I_{t+1} = I_t + \text{new\_infections} - \text{new\_recoveries}, \quad R_{t+1} = R_t + \text{new\_recoveries}$$

Susceptible and infected counts are clamped at $0$ to absorb floating-point error. The term $\beta S I / N$ is **frequency-dependent (mass-action)** transmission: each infected individual makes $\beta$ effective contacts per day, and a fraction $S/N$ of those contacts land on susceptible people.

### The basic reproduction number $\mathcal{R}_0$

`get_reproduction_number()` returns

$$\mathcal{R}_0 = \frac{\beta}{\gamma}$$

This is the expected number of secondary infections produced by one infected individual in a fully susceptible population. Early in an outbreak $S \approx N$, so the infected compartment grows whenever $\mathcal{R}_0 > 1$ and shrinks whenever $\mathcal{R}_0 < 1$ — the condition $\mathcal{R}_0 = 1$ is the epidemic threshold.

As the epidemic progresses and susceptibles are depleted, growth is governed by the **effective reproduction number**

$$\mathcal{R}_t = \mathcal{R}_0 \cdot \frac{S_t}{N}$$

The epidemic peaks exactly when $\mathcal{R}_t = 1$ (i.e. when $S_t/N = 1/\mathcal{R}_0$), which is why `get_peak_infection()` returns a turning point for $\mathcal{R}_0 > 1$.

### Herd-immunity threshold

An epidemic cannot sustain itself once too few susceptibles remain. The **herd-immunity threshold** — the immune fraction needed to start shrinking the epidemic — is

$$p_c = 1 - \frac{1}{\mathcal{R}_0}$$

For example, $\mathcal{R}_0 = 3$ gives $p_c \approx 67\%$. Setting `initial_recovered` above this fraction (as a proportion of `population_size`) suppresses the outbreak, demonstrating how vaccination short of full coverage still protects the population.

### Flatten the curve

Reducing $\beta$ (through distancing, masks, or isolation) lowers $\mathcal{R}_0$, which both lowers the peak $I_t$ and delays it. Because healthcare capacity is finite, "flattening" the curve — spreading infections over more days so the peak never exceeds capacity — is valuable even when the *final* attack rate changes only modestly. This is captured directly by comparing `get_peak_infection()` across runs with different `beta` values.

### Results API

After calling `run_simulation()`, the following methods summarise the run:

- `get_compartments()` — returns the full time series for `susceptible`, `infected`, and `recovered`.
- `get_peak_infection()` — returns `(peak_day, peak_value)`, the day and magnitude of maximum infections.
- `get_reproduction_number()` — returns $\mathcal{R}_0 = \beta/\gamma$.
- `get_final_sizes()` — returns the last-day value of each compartment.

See [src/sim_lab/core/epidemiological_simulation.py](../../../src/sim_lab/core/epidemiological_simulation.py) for the full implementation.
