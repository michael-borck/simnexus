# Forest Fire & Self-Organised Criticality

**Difficulty**: Advanced
**Time**: ~90 minutes
**Learning Focus**: self-organised criticality, power-law distributions
**Simulator**: `ForestFireSimulation` (registry `"ForestFire"`)

## Overview

The Drossel–Schwabl forest fire is the textbook model of **self-organised
criticality (SOC)**: with no parameter tuning, the interplay of slow regrowth,
fast fire spread, and rare lightning drives the forest to a critical state whose
fire sizes follow a **power law** — exactly the heavy-tailed statistics seen in
real wildfires. The central question: *can you recover a heavy-tailed fire-size
distribution when lightning is far rarer than regrowth (`p << g`), and does it
disappear when the two timescales are not separated?*

## Setup

`pip install sim-lab matplotlib scipy`, then import the simulator. Cell states
are `EMPTY = 0`, `TREE = 1`, `BURNING = 2`. You will also use
`scipy.ndimage.label` to measure connected tree clusters:

```python
import numpy as np
from scipy.ndimage import label
from sim_lab.core import ForestFireSimulation

TREE, BURNING = 1, 2
EIGHT = np.ones((3, 3), dtype=int)        # 8-connectivity (Moore neighbourhood)
```

## Instructions

1. **Run a long simulation in the critical regime.** Use `p` much smaller than
   `g` (a ratio near 1/50) and run for several thousand generations so the system
   reaches its critical state. `run_simulation()` returns tree counts per
   generation and fills `fire_history`; `get_all_states()` gives the full grid
   history you need to measure fire sizes:

   ```python
   sim = ForestFireSimulation(
       grid_size=(80, 80),
       initial_density=0.5,
       p=2e-4,       # lightning: rare
       g=1e-2,       # regrowth: ~50x faster  (p/g = 1/50 << 1)
       days=3000,
       boundary="periodic",
       random_seed=42,
   )
   trees = sim.run_simulation()
   states = sim.get_all_states()
   ```

2. **Measure fire sizes the robust way.** A *lightning ignition* is a tree cell
   that catches fire with **no** burning neighbour — it starts a brand-new fire.
   That fire then consumes the whole connected tree cluster containing it, so the
   **fire size = the size of that cluster** at the moment of ignition. This
   definition works even when several fires overlap in time (which they do here),
   unlike simply summing the burning count:

   ```python
   def fire_sizes(states, warmup=600):
       sizes = []
       for t in range(warmup, len(states) - 1):
           cur, nxt = states[t], states[t + 1]
           burning = cur == BURNING
           ignited = (cur == TREE) & (nxt == BURNING)        # caught fire
           if not ignited.any():
               continue
           # burning-neighbour count (8-neighbourhood, periodic)
           pb = np.pad(burning, 1, mode="wrap")
           bn = np.zeros_like(burning, dtype=int)
           for i in range(3):
               for j in range(3):
                   bn += pb[i:i + bn.shape[0], j:j + bn.shape[1]]
           bn -= burning
           struck = ignited & (bn == 0)                      # lightning ignition
           if not struck.any():
               continue
           labels, n = label(cur == TREE, structure=EIGHT)  # tree clusters
           cluster_sizes = np.bincount(labels.ravel())
           sizes.extend(cluster_sizes[labels[struck]].tolist())
       return np.array(sizes, dtype=float)

   sizes = fire_sizes(states)
   print(f"{len(sizes)} fires; mean={sizes.mean():.0f}, max={int(sizes.max())} cells")
   ```

3. **Test for a power law with the complementary CDF.** Plot
   `P(size >= s)` (the fraction of fires at least as large as `s`) against `s` on
   log–log axes. In the critical regime the bulk of the curve is roughly a
   straight line — the signature of a heavy-tailed, scale-free distribution
   $P(s) \propto s^{-\tau}$. Fit a slope over the linear region, avoiding the
   smallest bins and the finite-size cutoff at the top:

   ```python
   def ccdf_slope(sizes):
       xs = np.unique(sizes.astype(int))
       ccdf = np.array([np.mean(sizes >= x) for x in xs])
       mask = (xs >= 2) & (xs <= sizes.max() * 0.3) & (ccdf > 0)
       slope = -np.polyfit(np.log(xs[mask]), np.log(ccdf[mask]), 1)[0]
       return slope

   crit_slope = ccdf_slope(sizes)
   print(f"critical CCDF slope ~= {crit_slope:.2f}  (heavy-tailed if small)")
   ```

   On the log–log plot the critical curve falls off slowly, reaching fire sizes
   that are a large fraction of the 6400-cell grid.

4. **Confirm the forest has settled.** A critical forest is *quasi-stationary*:
   after warm-up the tree fraction fluctuates around a stable mean. Split the
   post-warm-up `trees` into halves and compare:

   ```python
   settled = np.array(trees[600:])
   half = len(settled) // 2
   f1 = settled[:half].mean() / 6400
   f2 = settled[half:].mean() / 6400
   print(f"tree fraction: 1st half={f1:.2f}  2nd half={f2:.2f}")
   print("settled?", abs(f1 - f2) < 0.05)
   ```

5. **Run a non-critical control and compare.** With `p` close to `g` the
   timescales are no longer separated and the system falls out of criticality:
   fires become small and frequent, so the distribution is cut off rather than
   heavy-tailed. Repeat with `p=5e-3, g=1e-2` and overlay both CCDF curves:

   ```python
   ctrl = ForestFireSimulation(
       grid_size=(80, 80), initial_density=0.5,
       p=5e-3, g=1e-2, days=3000, boundary="periodic", random_seed=42,
   )
   ctrl.run_simulation()
   ctrl_sizes = fire_sizes(ctrl.get_all_states())
   print(f"control: {len(ctrl_sizes)} fires; max={int(ctrl_sizes.max())} cells; "
         f"slope~={ccdf_slope(ctrl_sizes):.2f}")
   ```

   The named contrast is the **SOC signature**: the critical run (`p ≪ g`) has
   rare fires spanning hundreds-to-thousands of cells (shallow CCDF, large max),
   while the control (`p` closer to `g`) is cut off at small sizes (steep CCDF,
   small max). Both halves of the law should hold:

   ```python
   assert sizes.max() > 5 * ctrl_sizes.max(), "critical fires should be far larger"
   assert crit_slope < ccdf_slope(ctrl_sizes), "critical CCDF should be shallower"
   print("Heavy-tailed fires in the critical regime; cut-off in the control.")
   ```

## Things to explore

- **Separation ratio.** Sweep `p/g` over {1/1000, 1/200, 1/50, 1/10}. How do the
  fitted slope and the maximum fire size respond as the timescales come together?
- **Finite-size scaling.** Run the same `p/g` on `(50,50)`, `(80,80)`,
  `(120,120)`. Does the largest fire grow with grid size — a hallmark of
  criticality?
- **Warm-up.** How many generations does an initially empty forest need to reach
  its critical tree fraction? Plot tree fraction over the first 600 generations.
- **Boundary.** Does `boundary="fixed"` change the slope versus
  `boundary="periodic"`? Why might a torus be cleaner?

## Extension ideas

- **Maximum-likelihood exponent.** Use the Hill estimator on the raw `sizes`
  array (no binning) for an unbiased exponent `τ` and a bootstrap confidence
  interval; compare to your CCDF slope.
- **Cluster-size vs fire-size.** Snapshot the connected-tree cluster
  distribution between fires (reusing `label`) and compare its tail to the
  fire-size tail.
- **Avalanche mapping.** Treat each fire as an "avalanche" and measure its
  duration (generations of burning) as well as its size; test whether duration
  also follows a power law.

## Assessment criteria

- **Reproducibility** — `random_seed=42` set; the same seed reproduces the
  fire-size list, slope, and max.
- **Validation** — the `p ≪ g` run shows a heavy-tailed fire-size distribution
  (shallow, roughly straight CCDF on log–log with fires spanning a large fraction
  of the grid); the `p`-closer-to-`g` control is cut off at small sizes (steeper
  CCDF); and the tree fraction is quasi-stationary after warm-up.
- **Analysis** — interprets the shallow CCDF as the SOC power law, explains why
  separated timescales (`p ≪ g`) produce it and why overlapping fires force the
  cluster-based measurement, and discusses finite-size effects.
- **Code quality** — warm-up, the lightning-ignition detector, and the fit window
  are named parameters; the CCDF slope fit excludes the cutoff bins rather than
  fitting the whole range blindly.
