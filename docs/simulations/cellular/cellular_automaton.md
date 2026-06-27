# Cellular Automaton Simulation

## Purpose

This simulation models grid-based cellular automata, in which each cell evolves from one generation to the next according to a local rule that depends only on the cell and its eight neighbors. By default it implements Conway's Game of Life, but it also accepts any user-supplied update function, making it a flexible teaching tool for exploring emergence, self-organization, and how very simple local rules can produce strikingly complex global behavior.

## Parameters

- `grid_size`: `Tuple[int, int]` — The dimensions of the grid as `(rows, columns)`. Used to validate a provided `initial_state` and to size a randomly generated grid. Default `(50, 50)`.
- `initial_state`: `Optional[np.ndarray]` — Initial configuration of the grid. If `None`, a random grid is generated. When provided, its shape must match `grid_size` or a `ValueError` is raised. Default `None`.
- `initial_density`: `float` — Probability that a randomly generated cell starts alive. Only used when `initial_state` is `None`. Default `0.3`.
- `rule`: `Union[str, Callable]` — Either the string `"game_of_life"` for the built-in Conway ruleset, or a custom callable with signature `(grid: np.ndarray) -> np.ndarray` that returns the next generation. Default `GAME_OF_LIFE` (`"game_of_life"`).
- `days`: `int` — Number of generations to simulate. Default `100`.
- `boundary`: `str` — Boundary condition, either `'periodic'` (edges wrap around, a torus) or `'fixed'` (cells outside the grid are treated as dead). Used by the built-in rule. Default `'periodic'`.
- `random_seed`: `Optional[int]` — Seed for the random number generator used when building a random initial state. Default `None`.

## Example Code

```python
import numpy as np
import matplotlib.pyplot as plt
from sim_lab.core import CellularAutomatonSimulation

# Start from a single glider on a small toroidal (periodic) grid.
glider = np.zeros((15, 15), dtype=int)
glider[1, 2] = 1
glider[2, 3] = 1
glider[3, 1:4] = 1

sim = CellularAutomatonSimulation(
    grid_size=(15, 15),
    initial_state=glider,
    rule="game_of_life",
    days=30,
    boundary="periodic",
)

live_cells = sim.run_simulation()
states = sim.get_all_states()

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Live-cell population over time.
axes[0].plot(live_cells, marker="o")
axes[0].set_xlabel("Generation")
axes[0].set_ylabel("Live Cells")
axes[0].set_title("Population Over Time")
axes[0].grid(True)

# Final grid configuration.
axes[1].imshow(states[-1], cmap="binary")
axes[1].set_title(f"Generation {len(states) - 1}")

plt.tight_layout()
plt.show()

# Has the grid settled into a static or cycling pattern?
print("Cycle length:", sim.detect_stable_pattern())
```

## Use Case Ideas

### Investigate How Initial Density Affects Long-Term Survival

Seed a random grid and vary `initial_density` to see how the starting crowd of live cells shapes the final outcome.

- At what density does the grid tend to die out versus sustain ongoing activity?
- How does the population curve over time differ between very sparse and very dense starts?
- Does the final live-cell count depend more on density or on `random_seed`?

### Investigate Classic Game of Life Patterns

Provide `initial_state` with a known pattern — a glider, a blinker, a block, or a pulsar — and watch how each evolves.

- Which patterns reach a stable fixed point (cycle length `0`) and which fall into a repeating cycle?
- How does switching `boundary` from `'periodic'` to `'fixed'` change the trajectory of a glider near the edge?
- Can you confirm the theoretical period of an oscillator using `detect_stable_pattern()`?

### Investigate Custom Update Rules

Pass your own callable as `rule` to explore alternative automata such as *HighLife*, *Seeds*, or majority-rule dynamics.

- How does changing the survival/birth thresholds alter the kinds of structures that emerge?
- What happens with a rule that ignores neighbors and depends only on the cell itself?
- Which custom rules produce chaotic, expanding behavior versus quickly stabilizing grids?

## Model Description

Each generation, every cell is updated in parallel based on its current value and the number of live cells among its eight Moore neighbors. Let $c_{i,j}^{(t)} \in \{0, 1\}$ denote the state of the cell at row $i$, column $j$ at generation $t$, and let $n_{i,j}^{(t)}$ be its live-neighbor count.

Neighbor counting is implemented in `_game_of_life_rule`. The grid is first padded by one cell on every side; with `boundary='periodic'` the padding wraps the edges (`np.pad(..., mode='wrap')`, forming a torus), while `boundary='fixed'` pads with zeros. A $3 \times 3$ sliding sum is then accumulated and the cell's own value subtracted so that only the eight neighbors are counted:

$$n_{i,j}^{(t)} = \sum_{\Delta i, \Delta j \in \{-1,0,1\}} c_{i+\Delta i,\, j+\Delta j}^{(t)} \;-\; c_{i,j}^{(t)}.$$

Conway's Game of Life then applies simultaneously to all cells:

1. A live cell with fewer than two live neighbors dies — **underpopulation**: $c^{(t)}_{i,j}=1 \land n^{(t)}_{i,j}<2 \Rightarrow c^{(t+1)}_{i,j}=0$.
2. A live cell with exactly two or three live neighbors survives.
3. A live cell with more than three live neighbors dies — **overpopulation**: $c^{(t)}_{i,j}=1 \land n^{(t)}_{i,j}>3 \Rightarrow c^{(t+1)}_{i,j}=0$.
4. A dead cell with exactly three live neighbors becomes alive — **reproduction**: $c^{(t)}_{i,j}=0 \land n^{(t)}_{i,j}=3 \Rightarrow c^{(t+1)}_{i,j}=1$.

`run_simulation()` applies this rule for `days` generations (returning a list of live-cell counts, one per generation), storing every intermediate grid in `state_history`. `get_all_states()` exposes that full history as a list of `np.ndarray` grids, indexed by generation; `get_state_at_day(day)` returns a single generation. After running, `detect_stable_pattern(max_cycle_length=10)` inspects the tail of the history: it returns `0` when the final two generations are identical (a fixed point), the cycle length $L$ (up to `max_cycle_length`) when the last $L$ generations repeat periodically, or `None` if no such pattern is found.
