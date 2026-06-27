# Design a Custom CA Rule

**Difficulty**: Intermediate
**Time**: ~45 minutes
**Learning Focus**: local update rules, emergence and consensus dynamics
**Simulator**: `CellularAutomatonSimulation` (registry `"CellularAutomaton"`)

## Overview

Conway's Game of Life is just one of thousands of rules a grid of cells can
follow. In this project you write your *own* update rule — the classic
**majority (vote) rule** — and hand it to the engine as a plain Python function.
The real-world analogue is opinion dynamics or grain growth: each cell copies
the majority state of its neighbourhood, and the grid coarsens into large
uniform regions. The central question is *what global behaviour emerges from a
rule that only looks at immediate neighbours?*

## Setup

`pip install sim-lab matplotlib`, then import the engine. The key idea is that
`rule` accepts any callable with signature `(grid) -> grid`:

```python
import numpy as np
from sim_lab.core import CellularAutomatonSimulation
```

## Instructions

1. **Write a synchronous majority rule.** A cell becomes 1 if a majority of its
   own value plus its eight neighbours (9 cells total) are 1, otherwise 0. Build
   the neighbourhood sum by padding the grid so you can reuse the engine's
   neighbour-counting trick.

   ```python
   def majority_rule(grid):
       rows, cols = grid.shape
       padded = np.pad(grid, 1, mode="wrap")          # periodic boundary
       neigh = np.zeros((rows, cols), dtype=int)
       for i in range(3):
           for j in range(3):
               neigh += padded[i:i + rows, j:j + cols]
       return (neigh >= 5).astype(int)                # majority of 9 => alive
   ```

2. **Run it from random noise** and watch the grid coarsen into patches:

   ```python
   sim = CellularAutomatonSimulation(
       grid_size=(40, 40),
       initial_density=0.5,
       rule=majority_rule,
       days=25,
       boundary="periodic",
       random_seed=42,
   )
   live = sim.run_simulation()
   states = sim.get_all_states()
   ```

3. **Confirm the rule is applied synchronously.** Every cell must update from the
   *old* grid, never from a half-updated one. Validate this by hand: build a tiny
   grid with a single vertical stripe of 1s in a sea of 0s. Under synchronous
   majority each stripe cell has only 3 of 9 neighbours alive (`< 5`), so the
   whole stripe must vanish in exactly one generation. Check it:

   ```python
   stripe = np.zeros((5, 5), dtype=int)
   stripe[:, 2] = 1
   check = CellularAutomatonSimulation(
       grid_size=(5, 5), initial_state=stripe,
       rule=majority_rule, days=2, boundary="periodic", random_seed=42,
   )
   check.run_simulation()
   print("Gen 1 all zero?", not check.get_state_at_day(1).any())
   ```

   If anything other than `True`, your rule is reading cells it already
   overwrote — fix the synchrony bug.

4. **Verify the consensus law.** Majority rule is a *monotone* (Lyapunov)
   automaton: the number of "interfaces" (adjacent unlike-cell pairs) can only
   stay the same or decrease each generation, so the grid always reaches a fixed
   point. Count interfaces over the run and confirm `detect_stable_pattern()`
   returns `0`:

   ```python
   def interfaces(grid):
       v = np.sum(grid[:, :-1] != grid[:, 1:])     # horizontal pairs
       h = np.sum(grid[:-1, :] != grid[1:, :])     # vertical pairs
       return v + h

   iface = [interfaces(s) for s in states]
   monotone = all(iface[t + 1] <= iface[t] for t in range(len(iface) - 1))
   print("Interfaces non-increasing?", monotone)
   print("Fixed point reached?", sim.detect_stable_pattern() == 0)
   ```

   Both should print `True` — the named qualitative law is **monotone interface
   reduction ⇒ stable consensus**.

5. **Explain the boundary behaviour.** The rule uses `np.pad(..., mode="wrap")`
   (a torus). Re-run with `boundary="fixed"` and pad with `mode="constant"` so
   off-grid cells count as 0; describe in your write-up how edges now *bias* the
   border cells toward 0 and why `"periodic"` is preferred for clean studies.

## Things to explore

- **Density sweep.** Vary `initial_density` from 0.1 to 0.9. Where is the tipping
  point where the final grid ends up mostly 1s versus mostly 0s?
- **Threshold.** Change `>= 5` to `>= 4` (a "cautious" rule) or `> 5` (strict).
  How does the consensus speed and final patch count change?
- **Boundary swap.** Plot the final grid for `periodic` vs `fixed` from the same
  `random_seed=42` — quantify how many border cells flip.
- **Mixed rule.** What happens if a cell follows majority only *among its 4
  orthogonal* neighbours (von Neumann neighbourhood of 5)?

## Extension ideas

- **HighLife / Seeds.** Implement another totalistic rule (e.g. B36/S23 "HighLife"
  birth on 3 or 6, survive on 2 or 3) and compare the structures that emerge to
  Conway's.
- **Noisy majority.** Add a small probability of flipping against the majority
  (a stochastic CA) and measure whether the interface count still trends down.
- **Energy landscape.** Treat interfaces as an "energy" and plot it as a
  Lyapunov function alongside the grid snapshots.

## Assessment criteria

- **Reproducibility** — `random_seed=42` is set; re-running the notebook gives
  identical grids and interface counts.
- **Validation** — confirms the synchronous update (stripe vanishes in one step),
  the monotone-interface consensus law, and a fixed point (`detect_stable_pattern() == 0`).
- **Analysis** — interprets *why* patches coarsen and explicitly explains the
  `periodic` vs `fixed` boundary effect with evidence, not just a plot.
- **Code quality** — the rule is a clean, parameterised function; the threshold
  and boundary mode are named, not magic numbers buried inline.
