# SimLab Overview

SimLab is a Python simulation toolkit providing **18 simulators** across seven
modelling paradigms. Every simulator shares a consistent `BaseSimulation`
interface and a `SimulatorRegistry` for dynamic discovery, making it ideal for
educational, research, and business applications.

## Simulation paradigms

- **Basic** (discrete-time stochastic) — [Stock Market](./simulations/basic/stock_market.md), [Resource Fluctuations](./simulations/basic/resource_fluctuations.md), [Product Popularity](./simulations/basic/product_popularity.md)
- **Discrete-event** — [Discrete Event](./simulations/discrete_event/discrete_event.md), [Queueing](./simulations/discrete_event/queueing.md)
- **Statistical / stochastic** — [Monte Carlo](./simulations/statistical/monte_carlo.md), [Markov Chain](./simulations/statistical/markov_chain.md), [Gillespie SSA](./simulations/statistical/gillespie.md)
- **Cellular automata** — [Cellular Automaton](./simulations/cellular/cellular_automaton.md), [Game of Life](./simulations/cellular/game_of_life.md), [Forest Fire](./simulations/cellular/forest_fire.md)
- **Agent-based** — [Agent-Based](./simulations/agent_based/agent_based.md), [Boids](./simulations/agent_based/boids.md)
- **Continuous / system dynamics** — [System Dynamics](./simulations/system_dynamics/system_dynamics.md)
- **Network** — [Network](./simulations/network/network.md)
- **Ecological** — [Predator-Prey](./simulations/ecological/predator_prey.md)
- **Domain-specific** — [Epidemiological](./simulations/domain_specific/epidemiological.md), [Supply Chain](./simulations/domain_specific/supply_chain.md)

See the [full simulation catalog](./simulations/index.md) for parameters,
examples, and suggested experiments for each model.

## Key features

- **Unified interface** — every simulator inherits from `BaseSimulation`
- **Registry system** — dynamic discovery and instantiation
- **Reproducible** — stochastic runs controlled by `random_seed`
- **Multiple interfaces** — Python API, CLI (`simlab`), TUI, and web
- **Visualization** — results ready for matplotlib / plotly

## Getting Started

To get started, visit our [Getting Started](./getting_started.md) guide, which
will help you set up and run your first simulations.

## Contribute

Interested in contributing? Check out the [Contribution Guidelines](./contribute.md)
for more information on how to help improve SimLab.

## Contact

If you have any questions or feedback, please don't hesitate to
[Contact Us](./contact.md).
