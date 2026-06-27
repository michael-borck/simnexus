# Getting Started with SimLab

Welcome to the getting started guide for SimLab, a toolkit for simulating various business scenarios including stock market fluctuations, resource price dynamics, and product popularity. This guide will walk you through the installation options and different ways to use SimLab.

## Installation Options

SimLab offers flexible installation options depending on your needs:

### Basic Installation

For core simulation functionality only:

```bash
pip install sim-lab
```

### Full Installation

For all features including CLI, web interface, and development tools:

```bash
pip install sim-lab[dev]
```

### Component-Specific Installation

For specific interfaces:

```bash
# Command-line interface
pip install sim-lab[cli]

# Web interface
pip install sim-lab[web]
```

### Install from GitHub

For the latest development version:

```bash
pip install git+https://github.com/teaching-repositories/sim-lab.git
```

## Verify Installation

To ensure that SimLab was installed correctly:

```python
python -c "import sim_lab; print(sim_lab.__version__)"
```

Or using the CLI:

```bash
simlab --version
```

## Usage Methods

SimLab offers multiple ways to run simulations:

### 1. Python Library

Import SimLab in your Python code:

```python
from sim_lab.core import StockMarketSimulation

# Create a simulation instance
sim = StockMarketSimulation(
    start_price=100,
    days=365,
    volatility=0.03,
    drift=0.001,
    event_day=180,
    event_impact=-0.2,
    random_seed=42
)

# Run the simulation
prices = sim.run_simulation()

# Use the results
print(f"Final price: ${prices[-1]:.2f}")
```

### 2. Command Line Interface

Run simulations directly from the command line:

```bash
# Stock market simulation
simlab sim stock run --days 365 --event-day 180 --event-impact -0.2 --output results.csv

# Resource fluctuations simulation
simlab sim resource run --volatility 0.05 --disruption-day 100 --disruption-severity 0.3
```

### 3. Web Interface

Launch the web interface for interactive simulation:

```bash
simlab ui web
```

Then open your browser at http://localhost:8000.

### 4. Terminal UI

Launch the terminal user interface (TUI):

```bash
simlab ui tui
```

## Example Resources

SimLab includes comprehensive examples to help you get started:

- **Python Examples**: Basic scripts showing simulation usage
- **CLI Examples**: Shell scripts demonstrating command-line capabilities  
- **Jupyter Notebooks**: Interactive examples for data analysis

See the [examples directory](https://github.com/teaching-repositories/sim-lab/tree/main/examples) in the repository.

## Next Steps

- Explore the [API documentation](api.md) for detailed information on simulation classes
- Try different interfaces: [CLI](cli.md), [TUI](tui.md), or [Web](web.md)
- Check out the [example code](https://github.com/teaching-repositories/sim-lab/tree/main/examples) for practical applications

## Getting Help

If you encounter any issues or have questions:

- Check the [documentation](https://teaching-repositories.github.io/sim-lab/)
- Run `simlab --help` for CLI assistance
- Contact information is available on the [Contact](contact.md) page

Happy simulating with SimLab\!
