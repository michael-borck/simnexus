# Lightning vs Growth Balance

**Difficulty**: Intermediate
**Time**: ~60 minutes
**Learning Focus**: parameter sweeps, steady state of a stochastic CA
**Simulator**: `ForestFireSimulation` (registry `"ForestFire"`)

## Overview

A forest's long-term cover is set by a tug-of-war: trees grow back into empty
cells (rate `g`) while lightning strikes trees down (rate `p`). The Drossel–Schwabl
rules let you dial these two knobs independently and watch the steady state
respond. The central question: *how do the growth and ignition rates control the
forest's tree fraction, its fire frequency, and the size of its fires?* You will
sweep each parameter and confirm the two qualitative laws that govern the system.

## Setup

`pip install sim-lab matplotlib scipy`, then import the simulator. Cell states
are `EMPTY = 0`, `TREE = 1`, `BURNING = 2`. Every run anchors on
`random_seed=42`; because the steady state is noisy you will average each
parameter point over a few seeds (always including `42`). To count fires and
their sizes robustly (fires overlap in time at high rates) you measure each fire
from the connected tree cluster its lightning strike consumes:

```python
import numpy as np
from scipy.ndimage import label
from sim_lab.core import ForestFireSimulation

TREE, BURNING = 1, 2
EIGHT = np.ones((3, 3), dtype=int)
```

## Instructions

1. **Write a robust measurement helper.** For each generation a *lightning
   ignition* is a tree that catches fire with no burning neighbour — it starts a
   fresh fire whose size is its connected tree cluster. Counting these gives the
   fire frequency; their cluster sizes give the fire sizes. Tree fraction is just
   the mean tree count over the settled window:

   ```python
   def measure(grid_size, p, g, days=1000, warmup=300, seed=42):
       sim = ForestFireSimulation(
           grid_size=grid_size, initial_density=0.5,
           p=p, g=g, days=days, boundary="periodic", random_seed=seed,
       )
       trees = sim.run_simulation()
       states = sim.get_all_states()
       total = grid_size[0] * grid_size[1]
       tree_frac = np.mean(trees[warmup:]) / total

       sizes = []
       ignitions = 0
       for t in range(warmup, len(states) - 1):
           cur, nxt = states[t], states[t + 1]
           burning = cur == BURNING
           ignited = (cur == TREE) & (nxt == BURNING)
           if not ignited.any():
               continue
           pb = np.pad(burning, 1, mode="wrap")
           bn = np.zeros_like(burning, dtype=int)
           for i in range(3):
               for j in range(3):
                   bn += pb[i:i + bn.shape[0], j:j + bn.shape[1]]
           bn -= burning
           struck = ignited & (bn == 0)
           if not struck.any():
               continue
           labels, n = label(cur == TREE, structure=EIGHT)
           cluster_sizes = np.bincount(labels.ravel())
           sizes.extend(cluster_sizes[labels[struck]].tolist())
           ignitions += int(struck.sum())

       freq = ignitions / (days - warmup)
       mean_size = np.mean(sizes) if sizes else 0.0
       return tree_frac, freq, mean_size
   ```

2. **Average over seeds for a clean steady state.** The forest fire is stochastic,
   so a single run is noisy. Wrap `measure` in a small seed loop and return the
   means:

   ```python
   def mean_over_seeds(grid_size, p, g, seeds=(42, 7, 99)):
       rows = [measure(grid_size, p, g, seed=s) for s in seeds]
       tf = np.mean([r[0] for r in rows])
       fq = np.mean([r[1] for r in rows])
       ms = np.mean([r[2] for r in rows])
       return tf, fq, ms
   ```

3. **Growth sweep — fix `p`, vary `g`.** The prediction: *more regrowth → more
   trees*. Sweep `g` over a moderate range (very fast regrowth can flip into
   catastrophic fill-burn cycling, so stay below that):

   ```python
   p_fixed = 1e-4
   g_values = [1e-3, 2e-3, 4e-3, 7e-3, 1e-2, 1.5e-2, 2e-2]
   growth = []
   for g in g_values:
       tf, fq, ms = mean_over_seeds((40, 40), p_fixed, g)
       growth.append((g, tf, fq, ms))
       print(f"g={g:.0e}  tree_frac={tf:.3f}  freq={fq:.4f}  mean_fire={ms:.1f}")
   ```

4. **Lightning sweep — fix `g`, vary `p`.** The prediction: *more lightning →
   more frequent but smaller fires*. Sweep `p` while holding `g`:

   ```python
   g_fixed = 1e-2
   p_values = [1e-5, 5e-5, 1e-4, 5e-4, 1e-3, 3e-3]
   light = []
   for p in p_values:
       tf, fq, ms = mean_over_seeds((40, 40), p, g_fixed)
       light.append((p, tf, fq, ms))
       print(f"p={p:.0e}  tree_frac={tf:.3f}  freq={fq:.4f}  mean_fire={ms:.1f}")
   ```

5. **Validate the two laws.** Turn the qualitative predictions into robust
   endpoint asserts (the trends hold cleanly with seed averaging):

   ```python
   # Law 1: higher g -> more trees (compare the sweep endpoints)
   assert growth[-1][1] > growth[0][1], "tree fraction should rise with g"

   # Law 2a: higher p -> more frequent fires
   assert light[-1][2] > light[0][2], "fire frequency should rise with p"

   # Law 2b: higher p -> smaller fires
   assert light[-1][3] < light[0][3], "mean fire size should fall with p"
   print("Both balance laws hold.")
   ```

6. **Visualise the balances.** Make a 1×3 figure: tree fraction vs `g`, fire
   frequency vs `p`, and mean fire size vs `p` (log-x axes for the sweeps).
   Annotate which law each panel demonstrates.

## Things to explore

- **The fill-burn flip.** Push `g` past `2e-2` (try `4e-2`, `6e-2`). Why does the
  tree fraction eventually *drop* even though regrowth is faster? (Think about
  how connectivity feeds the fires.)
- **Frequency–size trade-off.** Plot fire frequency against mean fire size across
  *both* sweeps. Do they trace out a single inverse relationship?
- **Critical ratio.** Around what `p/g` does the forest tip from mostly-trees to
  mostly-empty?
- **Grid size.** Repeat the growth sweep on `(30,30)` vs `(50,50)`. Does the
  steady-state tree fraction depend on system size?

## Extension ideas

- **Heatmap.** Run a full `p × g` grid and produce a 2-D heatmap of steady-state
  tree fraction — locate the contour separating "living" from "dead" forests.
- **Recovery time.** After a large fire, how many generations until the local
  tree fraction recovers to its steady value? Does recovery time depend on `g`?
- **Mean-field tie-in.** In a mean-field picture the tree fraction obeys a
  balance between the `g`-driven gain and the fire-driven loss; fit your
  `tree_frac(g)` curve and discuss where mean-field succeeds and fails.

## Assessment criteria

- **Reproducibility** — a fixed seed list is used; re-running reproduces the
  sweeps point-for-point.
- **Validation** — both balance laws pass: tree fraction rises with `g`; fire
  frequency rises with `p` while mean fire size falls.
- **Analysis** — interprets *why* faster regrowth fills the forest and why
  frequent lightning keeps clusters small; explains the warm-up choice and why
  results are averaged over seeds.
- **Code quality** — the sweep is a single parameterised helper (no copy-pasted
  runs); `warmup`, `grid_size`, the seed list, and the sweep ranges are named,
  not hard-coded.
