# Tutorial Notebooks

Self-contained notebooks that introduce each paradigm by running real simulations
and interpreting the results. Open them in Jupyter / JupyterLab / VS Code.

| Notebook | Covers | Paradigm |
|---|---|---|
| [01 — Basic Financial Models](../notebooks/01_basic_financial.ipynb) | Stock Market, Resource Fluctuations, Product Popularity | Basic (discrete-time stochastic) |
| [02 — Discrete Event & Queueing](../notebooks/02_discrete_event.ipynb) | Discrete Event engine, M/M/1 and M/M/c queueing | Discrete-event |
| [03 — Statistical Methods](../notebooks/03_statistical.ipynb) | Monte Carlo (π, convergence), Markov chains, Gillespie SSA | Statistical / stochastic |
| [04 — Cellular & Agent-Based](../notebooks/04_cellular_agent_based.ipynb) | Game of Life, Forest Fire, Boids flocking | Cellular automata + agent-based |
| [05 — Continuous, Network & Domain Models](../notebooks/05_system_network_domain.ipynb) | System Dynamics, Network epidemics, Predator-Prey, SIR, Supply Chain | Continuous / network / domain-specific |

## How to use them

Each notebook mirrors the structure of a good student submission: set a
`random_seed`, run the simulation, plot the result, **validate against a known
analytic or qualitative result**, and interpret it. Use them as:

- **Lecture live-coding** — run cells top to bottom while explaining each paradigm.
- **A template** — students copy a notebook's structure for their own project.
- **A reproducibility reference** — every notebook sets its seed and reproduces
  identically on re-run.

See the [Project Gallery](projects/index.md) for assessable projects built on the
same simulators, and the [Instructor Guide](instructor-guide.md) for course design.
