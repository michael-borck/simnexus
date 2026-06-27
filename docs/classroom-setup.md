# Classroom Setup

This guide gets a classroom of students running SimLab quickly. It assumes basic
familiarity with Python and the command line, and works offline once installed.

## System requirements

- **OS:** Linux, macOS, or Windows (WSL recommended on Windows).
- **Python:** 3.10 or newer (`python --version`).
- **Disk:** ~200 MB for the package and its dependencies.
- **Network:** needed only for installation; simulations run locally with no
  API keys, no accounts, and no internet.

## Installation

### Option A — `uv` (recommended for classrooms)

`uv` is fast and creates an isolated environment per project, which avoids
"works on my machine" issues:

```bash
# one-time install of uv
curl -LsSf https://astral.sh/uv/install.sh | sh

git clone https://github.com/teaching-repositories/sim-lab.git
cd sim-lab
uv venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

### Option B — plain pip

```bash
git clone https://github.com/teaching-repositories/sim-lab.git
cd sim-lab
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

For students who only need to *use* (not develop) SimLab:

```bash
pip install sim-lab
```

## Verify the install

```bash
python -c "import sim_lab; from sim_lab.core import SimulatorRegistry; print(SimulatorRegistry.list_simulators())"
```

You should see 18 registered simulators. Then run one from the CLI:

```bash
simlab sim stock run --days 100 --viz
```

## Choosing an interface

| Interface | Best for | Launch |
|---|---|---|
| **Python API** | Projects, notebooks, grading scripts | `from sim_lab.core import ...` |
| **CLI (`simlab`)** | Quick demos, parameter sweeps, CSV output | `simlab sim <name> run --help` |
| **Web** | Interactive exploration in a browser | `simlab ui web` → http://localhost:8000 |
| **TUI** | Live terminal dashboards | `simlab ui tui` |

For project work, the **Python API in a notebook** is the default — it makes
plotting and interpretation easy.

## Reproducibility (important for grading)

Every stochastic simulator accepts `random_seed`. **Require students to set and
report it** so you can reproduce their exact numbers:

```python
sim = SimulatorRegistry.create("StockMarket", start_price=100, days=252,
                               volatility=0.02, drift=0.0005, random_seed=42)
```

## Common classroom issues

- **`ModuleNotFoundError: sim_lab`** — the virtual environment isn't activated, or
  the editable install (`-e .`) wasn't run. Re-run `pip install -e ".[dev]"`.
- **No plot appears** — in a headless/server environment set
  `export MPLBACKEND=Agg` and save figures to files instead of calling `plt.show()`.
- **Different numbers each run** — `random_seed` was not set, or a fresh random
  source (e.g. `numpy.random` called directly) bypasses the seeded generator.
- **Slow notebooks** — reduce `days`, grid size, or `num_samples`; the defaults
  are sized for interactive exploration, not performance.
