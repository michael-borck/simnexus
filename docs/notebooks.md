# Tutorial Notebooks

Self-contained notebooks that introduce each paradigm by running real simulations
and interpreting the results. Open them in Jupyter / JupyterLab / VS Code, or view
them on GitHub:

| Notebook | Covers | Paradigm |
|---|---|---|
| [01 — Basic Financial Models](https://github.com/michael-borck/sim-lab/blob/main/notebooks/01_basic_financial.ipynb) | Stock Market, Resource Fluctuations, Product Popularity | Basic (discrete-time stochastic) |
| [02 — Discrete Event & Queueing](https://github.com/michael-borck/sim-lab/blob/main/notebooks/02_discrete_event.ipynb) | Discrete Event engine, M/M/1 and M/M/c queueing | Discrete-event |
| [03 — Statistical Methods](https://github.com/michael-borck/sim-lab/blob/main/notebooks/03_statistical.ipynb) | Monte Carlo (π, convergence), Markov chains, Gillespie SSA | Statistical / stochastic |
| [04 — Cellular & Agent-Based](https://github.com/michael-borck/sim-lab/blob/main/notebooks/04_cellular_agent_based.ipynb) | Game of Life, Forest Fire, Boids flocking | Cellular automata + agent-based |
| [05 — Continuous, Network & Domain Models](https://github.com/michael-borck/sim-lab/blob/main/notebooks/05_system_network_domain.ipynb) | System Dynamics, Network epidemics, Predator-Prey, SIR, Supply Chain | Continuous / network / domain-specific |

> The notebooks live in the [`notebooks/`](https://github.com/michael-borck/sim-lab/tree/main/notebooks) directory of the repository. The links above open the rendered notebook on GitHub; download or clone to run them locally.

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
