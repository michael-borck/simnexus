# Flocking vs Milling

**Difficulty**: Intermediate
**Time**: ~50 minutes
**Learning Focus**: emergent collective motion, how steering weights shape macroscopic state
**Simulator**: BoidsSimulation (registry `"Boids"`)

## Overview

Craig Reynolds' *boids* follow only three local rules — **separation** (don't
crowd), **alignment** (match neighbours' heading), and **cohesion** (steer toward
the neighbours' centre) — yet flocks, streams, and swirling mills emerge with no
leader. The question this project answers: **which combination of the three rule
weights produces an ordered flock, parallel streams, a clumping mill, or a
disordered swarm — and how do you tell them apart from the simulation's own
metrics?**

## Setup

Install sim_lab and use the Boids simulator directly:

```bash
pip install sim_lab
```

```python
from sim_lab.core import BoidsSimulation
```

Read the [Boids docs](../../simulations/agent_based/boids.md) first. Each step
`run_simulation()` reports `mean_speed`, `max_speed_observed`, the flock
`centroid_x` / `centroid_y`, and `flock_spread` (the mean positional standard
deviation of the boids — low when they are gathered, high when scattered).

## Instructions

### 1. Run a baseline and read off the metrics

```python
import numpy as np
import matplotlib.pyplot as plt
from sim_lab.core import BoidsSimulation

def run(w_sep, w_ali, w_coh, num_boids=90, days=110, perception_radius=15.0, seed=42):
    sim = BoidsSimulation(
        num_boids=num_boids,
        width=100.0,
        height=100.0,
        max_speed=3.0,
        max_force=0.05,
        perception_radius=perception_radius,
        weight_separation=w_sep,
        weight_alignment=w_ali,
        weight_cohesion=w_coh,
        days=days,
        random_seed=seed,
    )
    return sim.run_simulation()

def steady(metrics, key, window=30):
    # average over the last `window` steps to describe the settled state
    return np.mean([m[key] for m in metrics[-window:]])

def tightest(metrics, key, window=30):
    # minimum over the steady-state window: the tightest the flock gathers,
    # ignoring brief spikes when a moving flock wraps the toroidal boundary.
    return np.min([m[key] for m in metrics[-window:]])

m = run(w_sep=0.6, w_ali=1.5, w_coh=1.0)
print("spread =", round(steady(m, "flock_spread"), 2),
      " mean_speed =", round(steady(m, "mean_speed"), 3))
```

### 2. Map the four canonical regimes

Run the four corners of the (alignment, cohesion) plane at modest separation and
record each state's `(flock_spread, mean_speed)` signature.

```python
regimes = {
    "disordered":       (0.3, 0.3),
    "parallel streams": (3.0, 0.3),
    "clump / mill":     (0.3, 3.0),
    "ordered flock":    (3.0, 3.0),
}
print(f"{'state':<18}{'spread':>9}{'mean_speed':>12}")
for name, (w_ali, w_coh) in regimes.items():
    m = run(w_sep=0.6, w_ali=w_ali, w_coh=w_coh)
    print(f"{name:<18}{steady(m,'flock_spread'):9.2f}{steady(m,'mean_speed'):12.3f}")
```

Use these signatures to build a classifier: high `mean_speed` ⇒ ordered motion
(alignment at work); low `mean_speed` with low `flock_spread` ⇒ a static clump or
mill; high `flock_spread` ⇒ a scattered swarm or parallel streams.

### 3. Validate: higher cohesion → lower spread

Use a larger `perception_radius` (so each boid is pulled toward a wide cluster of
neighbours, not just the few beside it) and hold alignment low so the gathered
flock does not stream around the torus. Raise the cohesion weight and watch
`flock_spread` fall. Record the **minimum** spread over the steady-state window:
it captures how tightly the flock gathers while ignoring brief spikes from a
moving flock wrapping the toroidal boundary.

```python
cohs = [0.2, 0.6, 1.0, 1.5, 2.0]
spreads = [tightest(run(w_sep=0.4, w_ali=0.3, w_coh=wc, perception_radius=30.0),
                    "flock_spread") for wc in cohs]
plt.plot(cohs, spreads, "o-")
plt.xlabel("weight_cohesion")
plt.ylabel("tightest flock_spread (steady state)")
plt.title("Higher cohesion gathers the flock (lower spread)")
plt.show()
```

### 4. Validate: higher alignment → higher, more stable mean speed

Holding cohesion moderate, raise the alignment weight. As headings synchronise the
flock moves as a coherent unit, so `mean_speed` rises **and** its step-to-step
variability (the standard deviation over the window) falls.

```python
alis = [0.2, 0.8, 1.5, 2.0, 3.0]
speeds, stds = [], []
for wa in alis:
    m = run(w_sep=0.6, w_ali=wa, w_coh=1.5)
    speeds.append(np.mean([x["mean_speed"] for x in m[-30:]]))
    stds.append(np.std([x["mean_speed"] for x in m[-30:]]))

fig, ax = plt.subplots()
ax.plot(alis, speeds, "o-", label="mean_speed")
ax.plot(alis, stds, "s-", label="speed std (instability)")
ax.set_xlabel("weight_alignment"); ax.legend()
plt.title("Higher alignment -> faster, more stable collective motion")
plt.show()
```

## Validation targets

With `random_seed=42`:

- **Alignment sweep** (`w_sep=0.6, w_coh=1.5`): `mean_speed` rises (≈ **0.9 →
  1.7**) and its standard deviation falls (≈ **0.11 → 0.06**) as
  `weight_alignment` goes from 0.2 to 3.0. Higher alignment ⇒ faster, more stable
  ordered motion.
- **Cohesion sweep** (`w_sep=0.4, w_ali=0.3, perception_radius=30`): the
  tightest `flock_spread` drops from the ~27.5 scattered baseline at low cohesion
  to about **20** at moderate cohesion (the gathered flock), then edges back up at
  the highest weight as the tight flock begins to orbit and wrap. The clean
  contrast is low vs. moderate cohesion — higher cohesion gathers the flock.

## Things to explore

- Sweep `weight_separation` at fixed alignment and cohesion. How does separation
  change `flock_spread`, and why?
- Push cohesion very high (4–6) with normal alignment. Why does `flock_spread`
  stop falling and even rise? (Think about the flock orbiting and wrapping the
  toroidal field.)
- Find a weight combination where the flock splits into **two sub-flocks** that
  never merge. What metric signature gives that away?
- Change `perception_radius` while holding density fixed. Below what radius does
  the flock dissolve into independent individuals?
- Re-run one configuration with three different seeds. Do the qualitative states
  persist even though the exact trajectories differ?

## Extension ideas

- Replace the single-number steady-state summary with a **phase diagram**: a grid
  over `(weight_alignment, weight_cohesion)` coloured by your classified state.
- Add a gentle "wind" force in a fixed direction and measure how much it deflects
  the flock's mean heading.
- Define an **order parameter** `|mean velocity| / max_speed` (Vicsek order) and
  confirm it tracks `mean_speed`, then locate the order–disorder transition as you
  vary `perception_radius`.

## Assessment criteria

- **Reproducibility** — `random_seed=42` is set; the four-regime table and both
  sweeps reproduce to the quoted precision.
- **Validation** — the report demonstrates the two laws: **higher alignment →
  higher, more stable `mean_speed`**, and **higher (moderate) cohesion → lower
  `flock_spread`**, and correctly explains the toroidal-wrap caveat on the spread
  metric.
- **Analysis** — each of the four regimes is labelled using its
  `(flock_spread, mean_speed)` signature, with the physical interpretation stated,
  not just the numbers.
- **Code quality** — sweeps are parameterised loops, the steady-state average is a
  reusable helper, and the three rule weights are the only things that change
  between runs.
