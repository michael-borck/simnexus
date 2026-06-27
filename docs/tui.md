# Terminal User Interface (TUI)

SimLab provides a Terminal User Interface (TUI) for running simulations interactively within your terminal.

## Installation

Make sure you have installed SimLab with the TUI dependencies:

```bash
pip install sim-lab[dev]
```

## Running the TUI

Launch the TUI with:

```bash
simlab ui tui
```

## Interface Overview

The TUI is organized into several screens:

1. **Welcome Screen**: Choose a simulation type
2. **Parameter Forms**: Configure simulation parameters
3. **Results Screen**: View simulation results and save data

### Navigation

- Use **Tab** to navigate between fields
- Use **Enter** to activate buttons
- Use **Arrow Keys** to move between options and navigate widgets

## Features

### Simulation Selection

The welcome screen allows you to select from the available simulation types:

- Stock Market Simulation
- Resource Fluctuations Simulation
- Product Popularity Simulation

### Parameter Configuration

Each simulation type has its own form for setting parameters:

- **Stock Market Simulation**:
  - Starting Price
  - Days
  - Volatility
  - Drift
  - Event Day (optional)
  - Event Impact

- **Resource Fluctuations Simulation**:
  - Starting Price
  - Days
  - Volatility
  - Drift
  - Supply Disruption Day (optional)
  - Disruption Severity

- **Product Popularity Simulation**:
  - Days
  - Initial Popularity
  - Virality Factor
  - Marketing Effectiveness

### Results Visualization

The results screen displays:

- Simulation parameters used
- A textual chart of the results
- Options to save the results or start a new simulation

### Saving Results

Results can be saved to CSV files for further analysis. The files are saved to your home directory in a `sim_lab_results` folder.