# System Dynamics Simulation

## Purpose

This simulation models continuous, feedback-driven systems — populations, epidemics, economies, ecosystems — as coupled ordinary differential equations (ODEs) built from three classic building blocks: **stocks** (accumulations), **flows** (rates of change), and **auxiliaries** (derived quantities). It is a teaching tool for understanding how structure (who flows into whom) produces dynamic behaviour such as exponential growth, oscillation, and S-shaped saturation. Learners can switch between a transparent Euler integrator and SciPy's adaptive `RK45` solver to see how numerical method choice affects the result.

## Parameters

- `stocks` (`Dict[str, Stock]`): Dictionary of stock variables — the state variables that accumulate or deplete over time. Keys are stock names; values are `Stock` instances.
- `flows` (`Dict[str, Flow]`): Dictionary of flow variables — the rates of change that move quantity between stocks. Keys must follow the naming convention `flow_from_<source>_to_<destination>` (see Model Description); values are `Flow` instances.
- `auxiliaries` (`Optional[Dict[str, Auxiliary]]`, default `None`): Dictionary of auxiliary variables — intermediate quantities computed from the current stocks and flows (e.g. a net change or a ratio). They are recorded for output but do not alter the ODEs.
- `days` (`int`, default `100`): Number of time steps to simulate. Together with `dt` this sets the total simulated time.
- `dt` (`float`, default `1.0`): Time step size. The total simulated time is `days * dt`.
- `integration_method` (`str`, default `'RK45'`): The ODE integration method. Use `'euler'` for a fixed-step explicit Euler scheme, or any method accepted by `scipy.integrate.solve_ivp` (e.g. `'RK45'`, `'RK23'`, `'Radau'`, `'LSODA'`).
- `random_seed` (`Optional[int]`, default `None`): Seed for the random number generator, useful when a flow or auxiliary introduces stochasticity.

## Example Code

```python
from sim_lab.core import SystemDynamicsSimulation, Stock, Flow, Auxiliary
import matplotlib.pyplot as plt

# Exponential population growth: a births inflow and a deaths outflow.
birth_rate, death_rate = 0.05, 0.02

stocks = {
    "population": Stock("population", initial_value=100),
}

flows = {
    # The name "flow_from_<src>_to_<dst>" wires the flow between stocks.
    # "births" and "deaths" are not declared stocks, so they act as an
    # infinite source and sink (the classic "clouds" of system dynamics).
    "flow_from_births_to_population": Flow(
        "flow_from_births_to_population",
        lambda state, t: state["population"] * birth_rate,
    ),
    "flow_from_population_to_deaths": Flow(
        "flow_from_population_to_deaths",
        lambda state, t: state["population"] * death_rate,
    ),
}

# An auxiliary records a derived quantity — here the net change per time
# unit — computed from the current stocks and flows. It does not feed back
# into the ODEs; it is simply logged for inspection.
auxiliaries = {
    "net_change": Auxiliary(
        "net_change",
        lambda state, flow_rates, t: (
            flow_rates["flow_from_births_to_population"]
            - flow_rates["flow_from_population_to_deaths"]
        ),
    ),
}

sim = SystemDynamicsSimulation(
    stocks=stocks,
    flows=flows,
    auxiliaries=auxiliaries,
    days=150,
    dt=0.1,
    integration_method="RK45",
)

results = sim.run_simulation()

# sim.results holds one row of stock values per time point and is aligned
# 1:1 with sim.time_points, so it is the clean pair to plot. (Column 0 is
# the single "population" stock; see Model Description for the result dict.)
plt.figure(figsize=(10, 6))
plt.plot(sim.time_points, sim.results[:, 0], label="Population")
plt.xlabel("Time")
plt.ylabel("Population")
plt.title("Exponential Population Growth (System Dynamics)")
plt.legend()
plt.show()
```

For quick experiments, the helper `create_predefined_model` builds a ready-made model in one call — for example an SIR epidemic:

```python
from sim_lab.core import create_predefined_model

sir = create_predefined_model(
    "sir",
    population=10000,
    initial_infected=10,
    transmission_rate=0.3,
    recovery_rate=0.1,
    days=100,
    dt=0.1,
)
sir_results = sir.run_simulation()
```

## Use Case Ideas

### Investigate Exponential Growth and the Birth–Death Balance

Use the example above (or `create_predefined_model("population", ...)`) to explore how a constant per-capita birth and death rate produce exponential growth or decline. Questions to Consider:

- With a net rate $(b-d)$, the analytic solution is $P(t)=P_0 e^{(b-d)t}$. Does the simulated curve match this closed form?
- What happens to the doubling time $t_2 = \ln 2/(b-d)$ as the death rate approaches the birth rate?
- When $d>b$, does the population decay to zero exponentially, and how quickly?

### Investigate an SIR Epidemic via `create_predefined_model`

Switch to the `"sir"` predefined model and explore how the basic reproduction number $R_0 = \beta/\gamma$ shapes the outbreak. Questions to Consider:

- How does the peak size and timing of the infected pool change as you raise `transmission_rate` ($\beta$)?
- At what recovery rate ($\gamma$) does the epidemic fail to take off ($R_0 < 1$)?
- Does the total recovered pool at the end match the classic herd-immunity threshold $1 - 1/R_0$?

### Investigate Numerical Integration Accuracy (Euler vs RK45)

Keep the model fixed and vary only `integration_method` and `dt` to study how the integrator trades speed for accuracy. Questions to Consider:

- How large can `dt` get before Euler visibly drifts from the analytic exponential, and does `RK45` stay accurate at the same step?
- For the oscillatory `lotka_volterra` model, does Euler's energy leak (growing amplitude) while `RK45` conserves the cycle?
- Which method is faster for a short run, and how does that flip as `days` grows?

## Model Description

The simulation represents a system as a set of stocks whose values evolve continuously in time. Each stock $S_i$ obeys an ODE formed by summing the flows that touch it:

$$\frac{dS_i}{dt} = \sum_{\text{flows into } i} \text{rate} \;-\; \sum_{\text{flows out of } i} \text{rate}$$

### Building Blocks

The model is assembled from three classes (all importable from `sim_lab.core`):

- **`Stock(name, initial_value)`** — an accumulation (a state variable). Holds `current_value` and a `history` list. It is the only kind of object whose time evolution is integrated.
- **`Flow(name, rate_function)`** — a rate of change. `rate_function` has signature `(state: Dict[str, float], time: float) -> float`, where `state` is the dictionary of current stock values, and returns the flow's instantaneous rate.
- **`Auxiliary(name, formula)`** — a derived quantity. `formula` has signature `(state, flow_rates, time) -> float`, so it can inspect both stocks and the just-computed flow rates. Auxiliaries are evaluated and recorded during integration but do **not** enter the ODEs (flow rate functions receive only the stock `state`).

### Wiring Flows Between Stocks

A flow is wired into the ODEs purely by its **name**, parsed in `derivatives()`. A name matching the pattern

```
flow_from_<source>_to_<destination>
```

subtracts its rate from the `<source>` stock's derivative and adds it to the `<destination>` stock's derivative. If `<source>` or `<destination>` is not a declared stock (as with `births` and `deaths` above), that end is simply ignored and acts as an infinite source or sink — the standard "cloud" of stock-and-flow diagrams. Flows whose names do not match the convention contribute to no stock and serve as pure recorders.

### Integration

The total simulated time is `total_time = days * dt`. Two code paths live in `run_simulation()`:

- **`integration_method='euler'`** — fixed-step explicit Euler. With $N = \text{total\_time}/dt$ steps and $\mathbf{y}$ the vector of stock values:

  $$\mathbf{y}_{n+1} = \mathbf{y}_n + \Delta t \cdot f(\mathbf{y}_n,\, t_n)$$

- **any other value** — delegated to `scipy.integrate.solve_ivp` with `method=integration_method` (default `'RK45'`, an adaptive Runge–Kutta pair). The solution is evaluated on `np.linspace(0, total_time, days + 1)` time points.

After integration, `run_simulation()` repopulates each stock's `history` by appending the solver's output rows onto the initial value it was seeded with — so a stock's `history` is one element longer than `sim.time_points` (the initial value is duplicated at $t=0$). For plotting, the cleanly aligned 1:1 pair is `sim.results` (one row of stock values per time point) against `sim.time_points`; `run_simulation()` also returns a dictionary with keys `stock_<name>`, `flow_<name>`, and `aux_<name>` for inspection. (Flow and auxiliary histories grow by one entry per internal derivative evaluation, so with adaptive solvers they are longer than the stock trajectory and are best read as logs rather than time-aligned series.)

### Predefined Models

The helper `create_predefined_model(model_type, **kwargs)` returns a configured `SystemDynamicsSimulation` for three classic systems. Each builds its stocks and flows from primitives exactly as in the example above:

| `model_type` | stocks | key keyword arguments (with defaults) | resulting dynamics |
| --- | --- | --- | --- |
| `"population"` | `population` | `birth_rate=0.03`, `death_rate=0.01`, `initial_population=1000`, `days=100`, `dt=0.1` | exponential growth, $\frac{dP}{dt}=(b-d)P$ |
| `"lotka_volterra"` | `prey`, `predators` | `prey_growth_rate=0.1`, `predation_rate=0.01`, `predator_death_rate=0.05`, `predator_growth_rate=0.005`, `initial_prey=100`, `initial_predators=20`, `days=100`, `dt=0.01` | predator–prey limit cycles |
| `"sir"` | `susceptible`, `infected`, `recovered` | `population=10000`, `initial_infected=10`, `initial_recovered=0`, `transmission_rate=0.3`, `recovery_rate=0.1`, `days=100`, `dt=0.1` | the SIR epidemic equations below |

The SIR predefined model instantiates the canonical compartmental ODEs:

$$\frac{dS}{dt} = -\frac{\beta S I}{N}, \qquad \frac{dI}{dt} = \frac{\beta S I}{N} - \gamma I, \qquad \frac{dR}{dt} = \gamma I$$

using flows `flow_from_susceptible_to_infected` (rate $\beta S I/N$) and `flow_from_infected_to_recovered` (rate $\gamma I$).
