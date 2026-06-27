# SimLab: Comprehensive Simulation Toolkit

<!-- BADGES:START -->
[![agent-based-simulation](https://img.shields.io/badge/-agent--based--simulation-blue?style=flat-square)](https://github.com/topics/agent-based-simulation) [![business-simulation](https://img.shields.io/badge/-business--simulation-blue?style=flat-square)](https://github.com/topics/business-simulation) [![data-visualization](https://img.shields.io/badge/-data--visualization-blue?style=flat-square)](https://github.com/topics/data-visualization) [![discrete-event-simulation](https://img.shields.io/badge/-discrete--event--simulation-blue?style=flat-square)](https://github.com/topics/discrete-event-simulation) [![educational-tools](https://img.shields.io/badge/-educational--tools-blue?style=flat-square)](https://github.com/topics/educational-tools) [![modeling](https://img.shields.io/badge/-modeling-blue?style=flat-square)](https://github.com/topics/modeling) [![python](https://img.shields.io/badge/-python-3776ab?style=flat-square)](https://github.com/topics/python) [![simulation](https://img.shields.io/badge/-simulation-blue?style=flat-square)](https://github.com/topics/simulation) [![stochastic-processes](https://img.shields.io/badge/-stochastic--processes-blue?style=flat-square)](https://github.com/topics/stochastic-processes) [![system-dynamics](https://img.shields.io/badge/-system--dynamics-blue?style=flat-square)](https://github.com/topics/system-dynamics)
<!-- BADGES:END -->

SimLab is a Python package providing a versatile set of simulation tools for modeling complex systems across various domains. It offers a unified interface for different simulation paradigms, making it ideal for educational, research, and business applications.

## Installation

To install SimLab with all features:

```bash
pip install sim-lab
```

For specific interfaces only:

```bash
# CLI only
pip install sim-lab[cli]

# Web interface
pip install sim-lab[web]

# TUI (terminal interface)
pip install sim-lab[tui]
```

## Key Features

- **Unified Interface**: All simulators share a consistent API
- **Registry System**: Dynamic discovery and instantiation of simulation models
- **Multiple Interfaces**: CLI, TUI, Web, and Python API
- **Visualization Tools**: Built-in plotting and visualization capabilities
- **Data Import/Export**: Support for common data formats
- **Parameter Validation**: Comprehensive input validation
- **Stochastic Processes**: Support for random processes with seed control

## Simulation Categories

SimLab ships **18 simulators** organised by modelling paradigm — how state and time advance:

### Basic (discrete-time stochastic)
- **Stock Market** — price fluctuations with volatility, drift, and market events
- **Resource Fluctuations** — resource price dynamics with supply disruptions
- **Product Popularity** — product demand with growth, marketing, and promotions

### Discrete-Event
- **Discrete Event** — general-purpose event-driven engine
- **Queueing** — M/M/1 and M/M/c service systems (arrivals, queues, servers)

### Statistical / Stochastic
- **Monte Carlo** — sample random processes to estimate numerical results
- **Markov Chain** — stochastic processes with the Markov property
- **Gillespie SSA** — exact stochastic simulation of chemical kinetics

### Cellular Automata
- **Cellular Automaton** — grid models with local update rules (incl. Game of Life)
- **Game of Life** — Conway's Life seeded with classic patterns (glider, Gosper gun, ...)
- **Forest Fire** — Drossel-Schwabl forest fire and self-organised criticality

### Agent-Based
- **Agent-Based** — emergent behaviour from autonomous interacting agents
- **Boids** — Reynolds flocking (separation, alignment, cohesion)

### Continuous / System Dynamics
- **System Dynamics** — stocks, flows, and feedback loops (Euler + RK45)

### Network
- **Network** — processes (e.g. epidemic spread) on complex network topologies

### Ecological
- **Predator-Prey** — Lotka-Volterra population dynamics

### Domain-Specific
- **Epidemiological** — SIR disease-spread models
- **Supply Chain** — multi-tier supply chains with inventory management

## Basic Usage

```python
from sim_lab.core import SimulatorRegistry

# Create a simulation using the registry
sim = SimulatorRegistry.create(
    "StockMarket",
    start_price=100.0,
    days=252,
    volatility=0.02,
    drift=0.0005,
    random_seed=42
)

# Run the simulation
prices = sim.run_simulation()

# Visualize the results
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 6))
plt.plot(prices)
plt.title('Stock Price Simulation')
plt.xlabel('Trading Days')
plt.ylabel('Price ($)')
plt.grid(True)
plt.show()
```

### Command Line Interface

```bash
# Run a stock market simulation
simlab stock-market run --start-price 100 --days 365 --volatility 0.02 --drift 0.001 --output prices.csv

# Get help for all commands
simlab --help
```

### Terminal UI

```bash
# Launch the interactive terminal UI
simlab-tui
```

### Web Interface

```bash
# Start the web server
simlab-web

# Then visit http://localhost:8000 in your browser
```

## Educational Applications

SimLab is designed with education in mind, helping students:

- Understand complex systems through hands-on simulation
- Explore the impact of parameters on system dynamics
- Develop data analysis and visualization skills
- Apply theoretical concepts to practical scenarios
- Create and test hypotheses in a simulated environment

## Documentation

For comprehensive documentation, visit:
- [Getting Started Guide](https://teaching-repositories.github.io/sim-lab/getting_started/)
- [API Reference](https://teaching-repositories.github.io/sim-lab/api/)
- [Simulation Catalog](https://teaching-repositories.github.io/sim-lab/simulations/)
- [Developer Guide](https://teaching-repositories.github.io/sim-lab/developers/architecture/)
- [Teaching Guide](https://teaching-repositories.github.io/sim-lab/teaching_guide/)

## Development

SimLab uses modern Python development tools:

- [uv](https://github.com/astral-sh/uv) for dependency management
- [Ruff](https://github.com/astral-sh/ruff) for linting and formatting
- [pytest](https://docs.pytest.org/) for testing
- [MkDocs](https://www.mkdocs.org/) for documentation

To set up a development environment:

```bash
# Clone the repository
git clone https://github.com/teaching-repositories/sim-lab.git
cd sim-lab

# Run the setup script
./scripts/setup_dev.sh

# Or manually
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .[dev]
```

See [DEVELOPMENT.md](DEVELOPMENT.md) for more details.

## Registry System

SimLab features a powerful registry system for dynamically discovering and instantiating simulators:

```python
from sim_lab.core import SimulatorRegistry, BaseSimulation

# Register a custom simulator
@SimulatorRegistry.register("MySimulator")
class MyCustomSimulation(BaseSimulation):
    # Your implementation here
    pass

# List available simulators
simulators = SimulatorRegistry.list_simulators()
print(f"Available simulators: {simulators}")

# Create an instance
sim = SimulatorRegistry.create("MySimulator", days=100, random_seed=42)
```

For more information, see the [Registry System documentation](https://teaching-repositories.github.io/sim-lab/developers/registry_system/).

## Contributing

We welcome contributions to the SimLab project! See the [Contributing Guide](CONTRIBUTING.md) for more details.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.