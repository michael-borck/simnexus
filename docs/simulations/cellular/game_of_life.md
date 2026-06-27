# Game of Life Simulation

## Purpose

This simulation models Conway's Game of Life, the most famous example of a two-dimensional cellular automaton, in which a grid of cells evolves generation by generation according to a few simple local rules. Despite those rules being entirely deterministic, the system gives rise to a remarkably rich zoo of behaviours — stable shapes, oscillators, and gliding spaceships — making it a classic vehicle for teaching emergence, computation theory, and pattern dynamics. The simulator ships a catalogue of named starting patterns (still lifes, oscillators, spaceships, and the Gosper glider gun) so students can begin exploring immediately rather than hand-drawing initial states.

## Parameters

- `grid_size`: A tuple `(rows, cols)` giving the dimensions of the grid (default `(50, 50)`).
- `pattern`: Name of a starting pattern from the `PATTERNS` dictionary — `"block"`, `"beehive"`, `"blinker"`, `"toad"`, `"beacon"`, `"glider"`, `"lwss"`, `"pulsar"`, or `"gosper_glider_gun"`. Set to `None` to start from a random grid instead (default `None`).
- `offset`: Top-left `(row, col)` placement of the named pattern on the grid. `None` centres the pattern (default `None`).
- `initial_density`: When `pattern` is `None`, the probability that each cell starts alive (default `0.3`).
- `days`: Number of generations to evolve (default `100`).
- `boundary`: Boundary condition for cells on the edge — `"periodic"` wraps around (torus), `"fixed"` treats off-grid neighbours as dead (default `"periodic"`).
- `random_seed`: Seed for reproducible random grids (default `None`).

## Example Code

```python
from sim_lab.core import GameOfLifeSimulation
import matplotlib.pyplot as plt

# --- A glider: a 5-cell spaceship that travels diagonally forever. ---
glider = GameOfLifeSimulation(
    grid_size=(15, 15),
    pattern="glider",
    days=30,
    boundary="periodic",
)
glider_live = glider.run_simulation()

# --- The Gosper glider gun: emits a new glider every 30 generations. ---
gun = GameOfLifeSimulation(
    grid_size=(40, 70),
    pattern="gosper_glider_gun",
    offset=(5, 5),
    days=80,
    boundary="periodic",
)
gun_live = gun.run_simulation()
final_grid = gun.get_state_at_day(gun.days - 1)

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# Left: live-cell counts. The glider holds steady at 5 cells (a true spaceship),
# while the gun's population climbs as it launches gliders across the grid.
axes[0].plot(glider_live, label="Glider (5 cells)")
axes[0].plot(gun_live, label="Gosper glider gun")
axes[0].set_xlabel("Generation")
axes[0].set_ylabel("Live cells")
axes[0].set_title("Population over time")
axes[0].legend()

# Right: final grid of the gun, showing emitted gliders streaming to the right.
axes[1].imshow(final_grid, cmap="binary")
axes[1].set_title(f"Gosper gun at generation {gun.days - 1}")
axes[1].set_xlabel("Column")
axes[1].set_ylabel("Row")

plt.tight_layout()
plt.show()
```

## Use Case Ideas

### Investigate Still Lifes, Oscillators, and Spaceships

Seed the grid with each named pattern in turn (`block`, `beehive`, `blinker`, `toad`, `beacon`, `glider`, `lwss`, `pulsar`) and watch how its live-cell count and visual shape evolve over a few dozen generations.

Questions to Consider:

  - Which patterns never change shape, which return to their original form after a fixed number of generations, and which translate across the grid?

  - How does the periodic boundary condition change the long-term behaviour of a glider or lightweight spaceship compared with a fixed boundary?

  - For each oscillator, what is its period — the number of generations before it repeats?

### Investigate the Gosper Glider Gun

Place the `gosper_glider_gun` on a wide grid with a few generations of headroom and run it for 80–100 steps. A new glider is launched roughly every 30 generations.

Questions to Consider:

  - Why does the live-cell count grow roughly linearly even though the underlying rules are local and reversible in shape?

  - What happens if the boundary is `fixed` so the emitted gliders collide with the edge instead of wrapping around?

  - At what generation count does the first glider fully separate from the gun body?

### Investigate Random "Soup" Dynamics

Set `pattern=None` and sweep `initial_density` (for example, `0.1`, `0.3`, `0.5`, `0.7`) on a large grid, recording the final population and whether `detect_stable_pattern()` reports a cycle.

Questions to Consider:

  - At which density does the simulation leave behind the most surviving material, and why might that be near the critical value of roughly `0.3`?

  - Do random soups reliably settle into stable debris plus a few oscillators, regardless of the starting density?

  - How does changing the `boundary` condition affect the steady-state population on a finite grid?

## Model Description

`GameOfLifeSimulation` is a thin convenience wrapper around `CellularAutomatonSimulation`. It fixes the update rule to Conway's Game of Life and optionally seeds the grid with a named pattern via the module-level `place_pattern()` helper before delegating to the base class for evolution. When no pattern is supplied, the base class fills the grid with a random `initial_density` of live cells.

**Seeding with `place_pattern()` and the `PATTERNS` catalogue.** `place_pattern(pattern, grid_size, offset)` zeros a `grid_size` array and stamps the given `pattern` (a 0/1 NumPy array) at the top-left `offset`, centring it when `offset` is `None`. It raises `ValueError` if the pattern is larger than the grid or would fall outside it. The `PATTERNS` dictionary bundles the canonical starting shapes:

- **Still lifes** (unchanging): `block`, `beehive`.
- **Oscillators** (periodic): `blinker` (period 2), `toad` (period 2), `beacon` (period 2), `pulsar` (period 3).
- **Spaceships** (translate): `glider` (moves diagonally), `lwss` (lightweight spaceship, moves orthogonally).
- **Guns**: `gosper_glider_gun` — a 36×9 pattern that emits a new glider every ~30 generations, the first known object with unbounded growth from a finite seed.

**The Game of Life update rule.** Each generation, every cell counts its eight neighbours (with `"periodic"` boundaries wrapping around the grid and `"fixed"` boundaries treating off-grid neighbours as dead). The next state follows Conway's four rules:

1. A live cell with fewer than two live neighbours dies (underpopulation).
2. A live cell with two or three live neighbours survives.
3. A live cell with more than three live neighbours dies (overpopulation).
4. A dead cell with exactly three live neighbours becomes alive (reproduction).

Compactly, with $n$ the neighbour count and $s_t \in \{0,1\}$ the current state:

$$s_{t+1} = \begin{cases} 1 & \text{if } n = 3 \\ s_t & \text{if } n = 2 \\ 0 & \text{otherwise} \end{cases}$$

**Running and inspecting.** `run_simulation()` (inherited from `CellularAutomatonSimulation`) evolves the grid for `days` generations and returns a `List[float]` of live-cell counts per generation, one entry per step. The full grid history is retained, so `get_state_at_day(day)` returns the grid at any generation and `get_all_states()` returns the entire sequence as a list of arrays. `detect_stable_pattern()` scans for cycles up to a configurable length, which is useful for confirming that an oscillator or still life has settled.

See the cellular automaton documentation for the general engine, update-rule machinery, and boundary handling that this simulator builds on.
