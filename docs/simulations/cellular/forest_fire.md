# Forest Fire Simulation

## Purpose

This simulation implements the Drossel–Schwabl forest fire cellular automaton, a canonical model of **self-organised criticality**. Each grid cell is empty, a tree, or burning, and the system evolves through the interplay of slow tree growth, fast fire spread, and rare lightning strikes. It is a superb teaching tool because a single, tiny ruleset reproduces the heavy-tailed, power-law fire-size distributions observed in real ecosystems — emergent complexity from almost no rules.

## Parameters

- `grid_size`: Dimensions of the grid as a `(rows, columns)` tuple (default `(50, 50)`).
- `initial_density`: Initial fraction of cells that start as trees, in `[0, 1]` (default `0.5`).
- `p`: Spontaneous-ignition (lightning) probability per tree per step, in `[0, 1]` (default `1e-4`).
- `g`: Tree-regrowth probability per empty cell per step, in `[0, 1]` (default `1e-2`).
- `days`: Number of generations to simulate (default `100`).
- `boundary`: Boundary condition — `"periodic"` (edges wrap around, a torus) or `"fixed"` (edges bordered by empty cells) (default `"periodic"`).
- `initial_state`: Optional NumPy array with values in `{0, 1, 2}`; if given it overrides `initial_density` (default `None`).
- `random_seed`: Seed for the random number generator, for reproducible runs (default `None`).

## Example Code

```python
from sim_lab.core import ForestFireSimulation
import matplotlib.pyplot as plt

# Self-organised critical regime: lightning is rare, regrowth is ~100x faster.
sim = ForestFireSimulation(
    grid_size=(40, 40),
    initial_density=0.5,
    p=2e-4,       # lightning strikes per tree per step
    g=1e-2,       # regrowth per empty cell per step
    days=400,
    boundary="periodic",
    random_seed=7,
)

trees = sim.run_simulation()          # list of tree counts, one per generation
fires = sim.fire_history              # list of burning-cell counts per generation
stats = sim.get_statistics()
print(stats)
# {'mean_trees': ..., 'mean_fires': ..., 'max_fires': ..., 'final_tree_fraction': ...}

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(trees, color="green", label="Trees")
ax.plot(fires, color="red", label="Burning")
ax.set_xlabel("Generation")
ax.set_ylabel("Number of cells")
ax.set_title("Forest Fire: tree cover vs. burning cells over time")
ax.legend()
plt.tight_layout()
plt.show()
```

## Use Case Ideas

### Investigate Self-Organised Criticality and Fire-Size Distributions

Run the model with `p << g` for many generations and examine the distribution of fire sizes (the number of trees consumed in each burn event).

  - How does the fire-size distribution behave — is it roughly a straight line on a log–log plot, the signature of a power law?
  - What happens to the typical fire size if you increase or decrease the ratio `p / g`?
  - Does the system need a "warm-up" period to reach its critical state, and how can you tell it has arrived?

### Investigate the Balance Between Regrowth and Ignition

Fix the grid and sweep `g` while holding `p` constant to probe how the forest's steady-state tree cover is set by the growth/ignition balance.

  - At very low `g` the forest never builds up fuel; at very high `g` it is perpetually saturated. Where does the most interesting dynamics live?
  - Does `max_fires` from `get_statistics()` grow without bound as the grid is enlarged in the critical regime? (Hint: it scales with system size — a hallmark of criticality.)

### Investigate the Effect of Boundary Conditions

Compare `"periodic"` (toroidal) against `"fixed"` boundaries to see how edge effects change fire spread.

  - Do fires behave differently near the edges under `"fixed"` boundaries?
  - On a small grid, which boundary condition reaches a cleaner critical state, and why might `"periodic"` be preferred for finite-size studies?

## Model Description

The grid holds three cell states — **empty (`0`)**, **tree (`1`)**, **burning (`2`)** — and all three update rules are applied **synchronously** against the current generation's grid, so every cell's new state depends only on the previous generation (a classic cellular automaton). For each generation the Drossel–Schwabl rule (`_forest_fire_rule`) does the following:

1. **A burning cell becomes empty.**
2. **A tree ignites** if any of its eight neighbours is burning, *or* if it is struck by lightning with probability $p$:
   $$\text{ignites}(i,j) = \text{tree}(i,j) \land \bigl( \text{neighbours burning} > 0 \;\lor\; U_{ij} < p \bigr)$$
   where $U_{ij}$ is an independent uniform random draw.
3. **An empty cell grows a tree** with probability $g$:
   $$\text{grows}(i,j) = \text{empty}(i,j) \land \, V_{ij} < g$$

Neighbour counts are computed from a padded copy of the grid — `mode="wrap"` for `"periodic"` boundaries, or `constant=0` (empty) for `"fixed"` — excluding the cell itself. Because burning→empty, ignition, and growth each use masks derived from the *old* grid, a cell that burned this step cannot regrow in the same step, and a tree that ignites is not also regrown.

**Self-organised criticality.** When $p \ll g$, trees accumulate slowly into large, connected clusters while fires are ignited rarely; once a lightning strike hits, the cluster burns out almost instantly relative to the regrowth timescale. The competition between these widely separated timescales drives the system to a critical state *without any parameter tuning*. In this regime the fire-size distribution follows a power law, $P(s) \propto s^{-\tau}$, mirroring the scale-free fire statistics seen in real forests. Increasing $p$ toward $g$ destroys the separation of timescales and the system drifts out of criticality.

**Outputs.** `run_simulation()` advances the grid for `days` generations and returns a `List[float]` of the number of trees at each generation (it also populates `tree_history` and `fire_history` with the per-generation tree and burning-cell counts). `get_statistics()` summarises the run with `mean_trees`, `mean_fires`, `max_fires`, and `final_tree_fraction` (final tree count divided by total cells). See [`forest_fire_simulation.py`](../../../src/sim_lab/core/forest_fire_simulation.py) for the source.
