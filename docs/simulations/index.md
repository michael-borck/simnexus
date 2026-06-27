# SimLab Simulations

SimLab offers a comprehensive collection of simulation tools for modeling complex
systems. Every simulator inherits from `BaseSimulation`, registers itself with the
`SimulatorRegistry`, validates its parameters, and supports reproducible stochastic
runs through `random_seed`.

## Organising principle: modelling paradigm

Simulations are grouped by **how state and time advance** — the modelling paradigm —
because that is how the subject is taught and how the engines differ underneath. A
given simulator also belongs to one or more application domains (finance, ecology,
social science, physics, ...).

| Paradigm | How time/state advance | Simulators |
|---|---|---|
| **Basic** (discrete-time stochastic) | fixed time steps, random perturbation | [Stock Market](basic/stock_market.md), [Resource Fluctuations](basic/resource_fluctuations.md), [Product Popularity](basic/product_popularity.md) |
| **Discrete-event** | state jumps at scheduled events | [Discrete Event](discrete_event/discrete_event.md), [Queueing](discrete_event/queueing.md) |
| **Statistical / stochastic** | repeated sampling | [Monte Carlo](statistical/monte_carlo.md), [Markov Chain](statistical/markov_chain.md), [Gillespie SSA](statistical/gillespie.md) |
| **Cellular automata** | synchronous lattice updates | [Cellular Automaton](cellular/cellular_automaton.md), [Game of Life](cellular/game_of_life.md), [Forest Fire](cellular/forest_fire.md) |
| **Agent-based** | autonomous interacting agents | [Agent-Based](agent_based/agent_based.md), [Boids](agent_based/boids.md) |
| **Continuous** (ODE / system dynamics) | continuous time integration | [System Dynamics](system_dynamics/system_dynamics.md) |
| **Network** | processes on graphs | [Network](network/network.md) |

Applied to specific fields: [Predator-Prey](ecological/predator_prey.md)
(Lotka-Volterra ecology), [Epidemiological](domain_specific/epidemiological.md)
(SIR/SEIR disease spread), and [Supply Chain](domain_specific/supply_chain.md)
(multi-tier inventory).

## Basic Simulations

- [Stock Market](basic/stock_market.md) — price fluctuations with volatility, drift, and market events
- [Resource Fluctuations](basic/resource_fluctuations.md) — resource price dynamics with supply disruptions
- [Product Popularity](basic/product_popularity.md) — product demand with growth, marketing, and promotions
- [Modelling Market Dynamics](basic/modelling_market_dynamics.md) — theory behind the market models

## Discrete Event Simulations

- [Discrete Event](discrete_event/discrete_event.md) — general-purpose event-driven engine
- [Queueing](discrete_event/queueing.md) — M/M/1 and M/M/c service systems (arrivals, queues, servers)

## Statistical Simulations

- [Monte Carlo](statistical/monte_carlo.md) — sample random processes to estimate numerical results
- [Markov Chain](statistical/markov_chain.md) — stochastic processes with the Markov property
- [Gillespie SSA](statistical/gillespie.md) — exact stochastic simulation of chemical kinetics

## Cellular Automata

- [Cellular Automaton](cellular/cellular_automaton.md) — grid models with local update rules (incl. Game of Life)
- [Game of Life](cellular/game_of_life.md) — Conway's Life seeded with classic patterns (glider, Gosper gun, ...)
- [Forest Fire](cellular/forest_fire.md) — Drossel-Schwabl forest fire and self-organised criticality

## Agent-Based Simulations

- [Agent-Based](agent_based/agent_based.md) — emergent behaviour from autonomous interacting agents
- [Boids](agent_based/boids.md) — Reynolds flocking (separation, alignment, cohesion)

## System Dynamics

- [System Dynamics](system_dynamics/system_dynamics.md) — stocks, flows, and feedback loops

## Network Simulations

- [Network](network/network.md) — processes (e.g. epidemic spread) on complex network topologies

## Ecological Simulations

- [Predator-Prey](ecological/predator_prey.md) — Lotka-Volterra population dynamics

## Domain-Specific Simulations

- [Epidemiological](domain_specific/epidemiological.md) — SIR/SEIR disease-spread models
- [Supply Chain](domain_specific/supply_chain.md) — multi-tier supply chains with inventory management

## Common features

All SimLab simulators share:

- **Consistent interface** — every simulator inherits from `BaseSimulation` and exposes `run_simulation()`, `reset()`, and `get_parameters_info()`.
- **Registry system** — dynamic discovery and instantiation via `SimulatorRegistry`.
- **Parameter validation** — comprehensive input checking with clear errors.
- **Reproducibility** — stochastic runs are controlled by `random_seed`.
- **Visualization support** — results are plain lists/arrays ready for matplotlib/plotly.

## Getting started

```python
from sim_lab.core import SimulatorRegistry

# Create using the registry
sim = SimulatorRegistry.create("GameOfLife", pattern="glider", grid_size=(30, 30), days=60)

# Run and inspect
live_cells = sim.run_simulation()
print(f"Live cells over time: {live_cells[:5]} ...")

# Or instantiate a class directly
from sim_lab.core import BoidsSimulation
boids = BoidsSimulation(num_boids=50, days=50, random_seed=42)
metrics = boids.run_simulation()
```

See each simulator's page for its parameters, examples, and suggested experiments.
