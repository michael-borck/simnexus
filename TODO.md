# SimLab Project Roadmap

This document tracks the state of the SimLab simulation toolkit and the work that
remains. Items already shipped are checked; open work is listed below by area.

## Status snapshot

SimLab currently ships **18 simulators** across seven modelling paradigms, exposed
through a Python API, a CLI, a TUI, and a web interface. All simulators share a
`BaseSimulation` interface and a `SimulatorRegistry` for dynamic discovery.

Paradigms covered: Basic (discrete-time stochastic), Discrete-event, Statistical /
stochastic, Cellular automata, Agent-based, Continuous (system dynamics), Network,
plus ecological and domain-specific collections.

## Completed

### Core architecture
- [x] Core module structure with `BaseSimulation` abstract class
- [x] `SimulatorRegistry` for dynamic discovery and instantiation
- [x] Type hinting, parameter validation, and `get_parameters_info()` metadata
- [x] Reproducible stochastic runs via `random_seed`

### Simulators (18)
- [x] Basic: Stock Market, Resource Fluctuations, Product Popularity
- [x] Discrete-event: Discrete Event engine, Queueing (M/M/1, M/M/c)
- [x] Statistical: Monte Carlo, Markov Chain, Gillespie SSA
- [x] Cellular automata: Cellular Automaton, Game of Life (pattern catalogue), Forest Fire (Drossel-Schwabl)
- [x] Agent-based: Agent-Based engine, Boids (Reynolds flocking)
- [x] Continuous: System Dynamics (Euler + RK45)
- [x] Network: processes on random / scale-free / small-world graphs
- [x] Ecological: Predator-Prey (Lotka-Volterra)
- [x] Domain-specific: Epidemiological (SIR), Supply Chain (multi-tier)

### Interfaces
- [x] Importable Python package
- [x] CLI (`simlab`) with command groups
- [x] Terminal UI (`simlab-tui`)
- [x] Web interface (`simlab-web`)
- [x] Visualization helpers (`sim_lab.viz`)

### Documentation & testing
- [x] MkDocs Material site with per-simulator pages organised by paradigm
- [x] pytest tests for every simulator
- [x] CI workflow (ruff, mypy, pytest)
- [x] PyPI packaging (`sim-lab`)

### Bug fixes applied during the audit
- [x] `SupplyChainSimulation.run_simulation()` no longer crashes — added `reset()` to
      `SupplyChainNode` and its `Factory` / `Distributor` / `Retailer` subclasses.
- [x] `QueueingSimulation.run_simulation()` now processes events — removed the double
      `reset()` that wiped the event queue; the first arrival is scheduled in `reset()`.
- [x] `SystemDynamicsSimulation` RK45 path fixed — wrapped the derivative callable so
      `scipy.solve_ivp` receives `fun(t, y)` in the correct argument order.
- [x] Project-wide rename from the legacy "SimNexus" name to "SimLab" (code, docs,
      scripts, CI, config).

## Open work

### Interfaces
- [ ] Expand CLI coverage: only 7 of 18 simulators have `simlab` commands
      (stock, resource, product, game-of-life, forest-fire, boids, gillespie). Add
      commands for the remaining discrete-event, statistical, network, ecological,
      and domain-specific simulators.
- [ ] Expose the new simulators (Game of Life, Forest Fire, Boids, Gillespie) in the
      TUI and web interface.
- [ ] Sharable simulation configurations (save/load parameter sets).

### Known issues
- [ ] `QueueingSimulation.get_statistics()["server_utilization"]` is computed as
      `total_customers / (max_time * num_servers * service_rate)`, which approaches
      `(1 - rho) * rho` rather than the true utilization `rho`. Re-instrument with
      busy-time tracking so the statistic matches its name.
- [ ] The codebase uses `typing.Dict` / `typing.List` style throughout; under the
      project's enabled Ruff `UP` rules these are deprecated in favour of `dict` /
      `list`. Run a one-off `ruff check --select UP --fix` pass once the formatter is
      wired into CI.
- [ ] `AgentBasedSimulation.reset()` clears metrics but does not restore agent state;
      subclasses that need reproducible re-runs (e.g. Boids) override it. Consider
      pushing a general "snapshot initial agents" mechanism into the base class.

### Documentation & testing
- [ ] Add example notebooks for the new simulators (Boids, Gillespie, Forest Fire).
- [ ] Property-based / fuzz tests for parameter validation edge cases.
- [ ] Performance benchmarks for the larger engines (Network, Supply Chain).

### Deployment
- [ ] Docker image for the web interface.
- [ ] Cloud-deployment guide.
