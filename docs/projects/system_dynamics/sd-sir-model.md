# SIR as System Dynamics

**Difficulty**: Intermediate
**Time**: ~50 minutes
**Learning Focus**: compartmental modelling with stocks and flows; numerical integration (Euler vs RK45)
**Simulator**: SystemDynamicsSimulation (registry `"SystemDynamics"`)

## Overview
An epidemic is a textbook stock-and-flow system: people accumulate in the **Susceptible**, **Infected**, and **Recovered** compartments, and two flows — *infection* and *recovery* — move them between compartments. You will hand-build the classic SIR model from `Stock` and `Flow` primitives, solve the same equations with two integrators, and check that the result conserves the population and reproduces the dedicated `Epidemiological` compartment simulator.

## Setup
Install sim-lab (`pip install sim_lab`) and work in a Jupyter notebook. You will use the `SystemDynamicsSimulation` interface directly so you can wire the flows yourself; see the [System Dynamics doc page](../../simulations/system_dynamics/system_dynamics.md).

## Instructions

1. **Define the epidemic parameters and the three compartments.** The total population `N` is conserved, so the initial conditions must add up to it.

```python
from sim_lab.core import SystemDynamicsSimulation, Stock, Flow
import matplotlib.pyplot as plt

N = 10000          # total population
I0 = 10            # initially infected
beta = 0.3         # transmission rate (per infectious contact)
gamma = 0.1        # recovery rate (1 / infectious period)
```

2. **Wire the two flows.** A flow named `flow_from_<source>_to_<destination>` subtracts its rate from `<source>` and adds it to `<destination>`. Infection moves people S → I at rate `beta·S·I/N`; recovery moves them I → R at rate `gamma·I`. Build the model in a function so you can re-create it with different integrators:

```python
def build_sir(integration_method, days, dt):
    stocks = {
        "susceptible": Stock("susceptible", N - I0),
        "infected":    Stock("infected", I0),
        "recovered":   Stock("recovered", 0.0),
    }

    def infection(state, t):
        return beta * state["susceptible"] * state["infected"] / N

    def recovery(state, t):
        return gamma * state["infected"]

    flows = {
        "flow_from_susceptible_to_infected": Flow("flow_from_susceptible_to_infected", infection),
        "flow_from_infected_to_recovered":    Flow("flow_from_infected_to_recovered", recovery),
    }

    return SystemDynamicsSimulation(
        stocks=stocks, flows=flows,
        days=days, dt=dt,
        integration_method=integration_method,
        random_seed=42,
    )
```

3. **Run three integrators over the same horizon.** `total_time = days * dt`, so fixing `days * dt = HORIZON` keeps every run on the same time axis while you vary the step size `dt`.

```python
HORIZON = 100
fine_dt, coarse_dt = 0.1, 1.0

sim_rk45          = build_sir("RK45",  int(HORIZON / fine_dt),   fine_dt)
sim_euler_fine    = build_sir("euler", int(HORIZON / fine_dt),   fine_dt)
sim_euler_coarse  = build_sir("euler", int(HORIZON / coarse_dt), coarse_dt)

sim_rk45.run_simulation()
sim_euler_fine.run_simulation()
sim_euler_coarse.run_simulation()
```

4. **Plot the infected curve for all three.** `sim.results` is a `(time_points × stocks)` array aligned 1:1 with `sim.time_points`; column 1 is `infected`.

```python
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(sim_rk45.time_points,         sim_rk45.results[:, 1],         label="RK45 (reference)")
ax.plot(sim_euler_fine.time_points,   sim_euler_fine.results[:, 1],  label="Euler, dt=0.1")
ax.plot(sim_euler_coarse.time_points, sim_euler_coarse.results[:, 1], "--", label="Euler, dt=1.0")
ax.set_xlabel("Time"); ax.set_ylabel("Infected"); ax.legend()
ax.set_title("SIR epidemic — integrator comparison"); plt.show()
```

5. **Validate conservation of the population.** Because every flow just moves people between compartments, the net derivative of `S+I+R` is exactly zero — so Euler conserves it *exactly* (a linear invariant), as does RK45.

```python
for name, sim in [("RK45", sim_rk45), ("Euler fine", sim_euler_fine), ("Euler coarse", sim_euler_coarse)]:
    total = sim.results.sum(axis=1)          # S + I + R at every time point
    print(f"{name}: total ranges {total.min():.2f} .. {total.max():.2f} (expected {N})")
```

6. **Validate the trajectory against the dedicated compartment model.** Build the equivalent `EpidemiologicalSimulation` (an SIR integrated with a 1-day Euler step) and overlay its infected curve on the RK45 reference. They should track each other closely, with the small gap attributable to the coarser `dt = 1` step.

```python
from sim_lab.core import EpidemiologicalSimulation

epi = EpidemiologicalSimulation(
    population_size=N, initial_infected=I0, beta=beta, gamma=gamma,
    days=HORIZON + 1, random_seed=42,
)
epi.run_simulation()
epi_comp = epi.get_compartments()

ax.cla()
ax.plot(sim_rk45.time_points, sim_rk45.results[:, 1], label="System Dynamics (RK45)")
ax.plot(range(len(epi_comp["infected"])), epi_comp["infected"], "o", ms=3, label="Epidemiological (dt=1)")
ax.set_xlabel("Time"); ax.set_ylabel("Infected"); ax.legend()
ax.set_title("SIR: stock-and-flow vs dedicated compartment model"); plt.show()
```

7. **Check the epidemic's signature numbers.** The basic reproduction number is `R0 = beta / gamma`; the herd-immunity threshold is `1 - 1/R0`. Compare the final recovered fraction of your RK45 run against that threshold.

```python
R0 = beta / gamma
final_recovered_fraction = sim_rk45.results[-1, 2] / N
print("R0 =", R0)
print("herd-immunity threshold =", 1 - 1 / R0)
print("final recovered fraction =", final_recovered_fraction)
```

## Things to explore
- Raise `transmission_rate` until `R0 < 1` (i.e. `beta < gamma`). Does the infected curve still peak, or does the epidemic fail to take off?
- Vary `dt` for the Euler run from `1.0` down to `0.01`. How large can `dt` get before Euler visibly drifts from RK45 on the infected peak?
- Replace the S→I flow with frequency-dependent transmission `beta·S·I` (no `/N`). How does that change `R0` and the peak?
- Start with `I0 = 1` vs `I0 = 1000`. Which has the larger relative error between Euler-dt=1 and RK45, and why?

## Extension ideas
- Add a fourth compartment `exposed` (SEIR): a flow I → E (latency) and E → I. Re-check conservation over four stocks.
- Add a vaccinated inflow that moves S → R directly (a `flow_from_susceptible_to_recovered`). What vaccination fraction suppresses the peak below the healthcare capacity `I = 1000`?
- Compare runtime: which is faster for a short run, Euler or RK45? Where does the crossover sit as `HORIZON` grows?

## Assessment criteria
- **Reproducibility** — `random_seed=42` is set; re-running produces identical curves and numbers.
- **Validation (conservation)** — `S+I+R` is shown to equal `N` at every time step for all integrators (tolerance < 1e-6).
- **Validation (cross-model)** — the stock-and-flow infected trajectory matches the `Epidemiological` compartment model (same peak timing and final size); the coarse Euler (`dt=1`) curve sits closest to the `Epidemiological` curve.
- **Validation (theory)** — reported `R0 = beta/gamma` and the final recovered fraction is compared to the herd-immunity threshold `1 - 1/R0`.
- **Analysis** — the student explains *why* Euler-dt=1 drifts more than Euler-dt=0.1 and why RK45 stays accurate, rather than just plotting the curves.
- **Code quality** — the model is built once in a parameterised `build_sir(...)` function; no magic numbers buried in the plotting code.
