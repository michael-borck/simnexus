# Traffic Flow (Nagel-Schreckenberg)

**Difficulty**: Intermediate
**Time**: ~60 minutes
**Learning Focus**: one-dimensional cellular automata, traffic flow and jams
**Simulator**: `CellularAutomatonSimulation` (registry `"CellularAutomaton"`)

## Overview

The Nagel–Schreckenberg (NaSch) model is the standard cellular-automaton model
of single-lane highway traffic: cars accelerate, brake to avoid the car ahead,
sometimes dawdle, and move forward — all on a circular road. Despite its
simplicity it reproduces the **stop-and-go jams** seen on real motorways, which
appear *spontaneously* with no obstacle. The central question: *how does
free-flowing traffic turn into a jam just because of density?*

You will implement the four NaSch steps as a custom 1-D rule and hand it to the
2-D engine as a single-row grid, then build the **fundamental diagram** (flow vs
density) that every traffic engineer knows.

## Setup

`pip install sim-lab matplotlib`, then import the engine. Treat a one-lane road
as a grid with one row. Encode each car's *velocity* in the cell value: `0`
means empty, and a car moving at speed `v` (which may be 0, i.e. stopped) is
stored as `v + 1`. The `+1` offset is essential — a stopped car has velocity 0,
and storing it as `0` would make it vanish (indistinguishable from an empty
cell). So occupied cells hold values `1 .. v_max+1`:

```python
import numpy as np
from sim_lab.core import CellularAutomatonSimulation
```

## Instructions

1. **Build the NaSch rule as a closure.** It captures `v_max`, the dawdle
   probability `p_brake`, and a seeded RNG so the run is reproducible. Each step
   applies the four NaSch rules: (1) accelerate, (2) slow to the gap ahead,
   (3) random brake, (4) move. Velocities are stored as `v + 1`:

   ```python
   def make_nasch_rule(v_max, p_brake, seed):
       rng = np.random.RandomState(seed)
       def rule(grid):
           road = grid[0].copy()
           L = road.shape[0]
           new_road = np.zeros(L, dtype=int)
           pos = np.where(road > 0)[0]              # all car positions
           for i in pos:
               v = road[i] - 1                      # stored v+1 -> real velocity
               v = min(v + 1, v_max)                # 1. accelerate
               ahead = (pos - i) % L                # distance to every car ahead
               ahead = ahead[ahead > 0]
               gap = (ahead.min() - 1) if ahead.size else (L - 1)  # empty cells
               v = min(v, gap)                      # 2. slow down to the gap
               if rng.random() < p_brake:           # 3. random dawdle
                   v = max(v - 1, 0)
               new_road[(i + v) % L] = v + 1        # 4. move; store v+1
           out = np.zeros_like(grid)
           out[0] = new_road
           return out
       return rule
   ```

2. **Seed a road at an exact density.** Place `N` cars at `v_max` around the ring
   so the density is exactly `rho = N / L`:

   ```python
   def make_road(L, n_cars, v_max, seed):
       rng = np.random.RandomState(seed)
       road = np.zeros(L, dtype=int)
       idx = np.sort(rng.choice(L, n_cars, replace=False))
       road[idx] = v_max + 1                        # cars start at top speed
       return road.reshape(1, L)
   ```

3. **Run one density and measure the mean speed.** Free-flowing traffic lets
   every car cruise at `v_max`; a jammed road does not. Note the engine's
   `run_simulation()` returns `np.sum(grid)` per generation — with the `v+1`
   encoding that is `N_cars + total_velocity`, **not** the car count. Read the
   states directly and recover velocity by subtracting 1:

   ```python
   L, v_max, p_brake = 200, 5, 0.3
   rho = 0.05
   road0 = make_road(L, int(rho * L), v_max, seed=42)
   sim = CellularAutomatonSimulation(
       grid_size=(1, L), initial_state=road0,
       rule=make_nasch_rule(v_max, p_brake, seed=42),
       days=600, boundary="periodic", random_seed=42,
   )
   sim.run_simulation()
   states = sim.get_all_states()[200:]              # discard warm-up
   mean_speed = np.mean([s[s > 0].mean() - 1 for s in states])
   print(f"rho={rho:.2f}  mean speed={mean_speed:.2f} (v_max={v_max})")
   ```

   At `rho=0.05` you should see mean speed ≈ `v_max - p_brake` ≈ 4.7 — **free
   flow**: dawdling knocks it just below the limit.

4. **Build the fundamental diagram.** Sweep density and record mean flow
   `q = rho * mean_speed` (cars passing a fixed point per generation). This is
   the canonical validation curve for NaSch: a rising **free-flow branch** at low
   density, a **capacity maximum** at the critical density, then a falling
   **congested branch** as jams appear:

   ```python
   densities = np.arange(0.05, 0.85, 0.05)
   flows, speeds = [], []
   for rho in densities:
       road0 = make_road(L, int(rho * L), v_max, seed=42)
       s = CellularAutomatonSimulation(
           grid_size=(1, L), initial_state=road0,
           rule=make_nasch_rule(v_max, p_brake, seed=42),
           days=600, boundary="periodic", random_seed=42,
       )
       s.run_simulation()
       tail = s.get_all_states()[200:]
       sp = np.mean([st[st > 0].mean() - 1 for st in tail])
       speeds.append(sp)
       flows.append(rho * sp)
   ```

   Plot `flows` vs `densities`: confirm the inverted-U shape and note the density
   at which flow peaks (the critical density, around 0.15 for these parameters).

5. **Validate the two regimes.** Turn the qualitative picture into asserts:

   ```python
   speeds = np.array(speeds); flows = np.array(flows)
   free_idx = 0                                    # rho = 0.05
   jam_idx = int((0.6 - 0.05) / 0.05)             # rho = 0.60
   peak_idx = int(np.argmax(flows))
   assert speeds[free_idx] > 0.8 * v_max, "low density should be free flow"
   assert speeds[jam_idx] < 0.3 * v_max, "high density should be jammed"
   assert flows[peak_idx] > flows[free_idx] and flows[-1] < flows[peak_idx], \
       "fundamental diagram must rise then fall"
   print("Free flow at low density, jams above the critical density.")
   ```

6. **Visualise a jam.** At `rho=0.35` save the road each generation and show it
   as a space–time diagram (`imshow` of the states, rows = generation, columns =
   cell). You should see dark stop-and-go bands moving *backwards* against
   traffic — the hallmark of a phantom jam.

## Things to explore

- **Dawdle probability.** Set `p_brake` to `0.0`, `0.3`, `0.6`. Does the
  critical density shift? Do jams still form with no dawdling?
- **Deterministic limit.** With `p_brake=0` the rule is deterministic — can you
  still find jams, and what does that tell you about their origin?
- **`v_max`.** Double `v_max` to 10 (more "aggressive" drivers). How does the
  free-flow branch slope change?
- **Two lanes.** Sketch how you would add a lane-change step; what collision
  rule would you need?

## Extension ideas

- **Free-flow analytic line.** In free flow every unhindered car travels near
  `v_max`, so the free-flow branch tracks `q = rho * v_max` — overlay this line
  on your diagram and quantify where the data peels away.
- **Stop-and-go wave speed.** Measure the backwards propagation speed of the jam
  fronts from the space–time diagram and compare to the empirical ~15–20 km/h.
- **On-ramp.** Inject cars at one cell and remove them elsewhere; does a
  localised bottleneck lower the global capacity?

## Assessment criteria

- **Reproducibility** — both RNGs seeded (`seed=42`); re-running reproduces the
  same fundamental diagram point-for-point.
- **Validation** — the fundamental diagram shows the three named regimes (free
  flow at low density with `mean_speed ≈ v_max`, a capacity maximum near the
  critical density, jams above it with `mean_speed ≪ v_max`); a space–time plot
  shows a backwards-moving jam.
- **Analysis** — interprets *why* jams form without an obstacle and locates the
  critical density; explains why the `+1` velocity offset is needed and why the
  engine's `run_simulation()` counts can't be used directly.
- **Code quality** — the four NaSch steps are clearly separated and commented;
  `L`, `v_max`, `p_brake`, and `rho` are named parameters, not magic numbers.
