# Glider Gun Factory

**Difficulty**: Intermediate
**Time**: ~45 minutes
**Learning Focus**: unbounded growth from a finite seed, glider counting
**Simulator**: `GameOfLifeSimulation` (registry `"GameOfLife"`)

## Overview

Bill Gosper's glider gun is a landmark in computer science: the first pattern
proved to grow *without limit* from a fixed starting shape. It works like a
factory, emitting a fresh glider (a 5-cell spaceship) roughly every 30
generations — forever. In this project you run the `gosper_glider_gun` pattern on
a large grid, count the gliders it produces, and verify its signature property:
**linear population growth** of about +5 cells every 30 generations.

## Setup

`pip install sim-lab matplotlib`, then import the simulator. A glider is exactly
5 live cells, which makes counting clean:

```python
import numpy as np
from sim_lab.core import GameOfLifeSimulation
```

## Instructions

1. **Place the gun on a large grid and run.** The gun is 36 wide × 9 tall, so
   give it room and use a toroidal (`periodic`) boundary so emitted gliders can
   fly clear without dying at an edge. Offset it into the top-left corner so the
   gliders stream into open space:

   ```python
   sim = GameOfLifeSimulation(
       grid_size=(60, 90),
       pattern="gosper_glider_gun",
       offset=(8, 8),
       days=300,
       boundary="periodic",
       random_seed=42,
   )
   live = sim.run_simulation()
   states = sim.get_all_states()
   print(f"start={int(live[0])} cells, end={int(live[-1])} cells")
   ```

2. **Validate linear growth.** The gun body keeps a bounded, fluctuating
   population while each new glider adds a constant 5 cells. So the live-cell
   curve should climb in a straight line. Fit a line to the curve *after* the
   first glider detaches (≈ generation 30) and check the slope:

   ```python
   t0 = 30
   t = np.arange(t0, len(live))
   slope = np.polyfit(t, live[t0:], 1)[0]            # cells per generation
   per_30 = slope * 30
   print(f"slope = {slope:.3f} cells/gen  ->  +{per_30:.1f} cells / 30 gens")
   print("linear growth?", abs(per_30 - 5.0) < 1.0)
   ```

   The named result is **≈ +5 cells per 30 generations** (one glider per cycle).
   A good run lands `per_30` between about 4 and 6.

3. **Count the gliders directly.** The gun is pinned near the top-left; anything
   live outside its bounding box is escaped glider material. Each glider is 5
   cells, so divide the escaped live count by 5:

   ```python
   def escaped_gliders(grid, gun_rows=25, gun_cols=45):
       mask = np.ones(grid.shape, dtype=bool)
       mask[:gun_rows, :gun_cols] = False            # mask out the gun body
       return int(round(grid[mask].sum() / 5))

   n_gliders = escaped_gliders(states[-1])
   print(f"gliders emitted by gen {len(states)-1}: {n_gliders}")
   ```

4. **Cross-check the two measures.** Plot `live` versus generation, overlay the
   fitted line, and add `(5 * escaped_gliders(s)) + gun_baseline` as a second
   series to confirm the count and the slope agree on how many gliders exist at
   each generation. The two should track each other closely.

5. **Watch the first launch.** From `states`, find the generation at which the
   first detached glider first sits fully outside the gun's bounding box — this
   is the gun's "firing" time. Confirm subsequent gliders follow roughly every
   30 generations thereafter.

## Things to explore

- **Fixed vs periodic.** Re-run with `boundary="fixed"`. Gliders now crash into
  the edge and die — does the population plateau instead of growing linearly?
  Why?
- **Collision.** On a small grid the circling gliders eventually hit the gun.
  At roughly what generation does linear growth break down for `grid_size=(40, 40)`?
- **Rate vs grid.** Does doubling the grid change the *slope*, or just how long
  the linear regime lasts?
- **Net growth.** The gun is a finite seed with unbounded growth — how does its
  long-term behaviour differ from a `block` or a `blinker`?

## Extension ideas

- **Spaceship stream.** Use `place_pattern` to launch two guns aimed at each
  other and study the annihilation/reaction when glider streams collide.
- **Memoryless counter.** Build a detector that scans for the 5-cell glider shape
  (in any of its four rotations) each generation, rather than relying on the
  bounding-box estimate.
- **Growth-rate law.** Theoretically the population is `N(t) ≈ N0 + 5 * t/30`;
  fit `N0` and the period jointly and report the implied cycle length.

## Assessment criteria

- **Reproducibility** — `random_seed=42` set; re-running reproduces the same
  live-cell curve and glider count.
- **Validation** — the fitted slope yields ≈ +5 cells per 30 generations (the
  gun's defining linear-growth law), and the direct glider count agrees with the
  slope-based estimate.
- **Analysis** — explains *why* growth is linear (a bounded gun emits a constant
  5-cell glider per cycle), and interprets the boundary-condition effect.
- **Code quality** — the bounding box and offset are named parameters; the
  glider counter is a reusable function, not copy-pasted.
