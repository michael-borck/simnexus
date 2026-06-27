# Estimate π with Monte Carlo
**Difficulty**: Beginner
**Time**: ~30 minutes
**Learning Focus**: Monte Carlo integration; the Law of Large Numbers
**Simulator**: MonteCarloSimulation (registry `MonteCarlo`)
## Overview
The area of a unit circle is π. If you scatter points uniformly across the unit square `[0,1]×[0,1]`, the fraction that land inside the quarter circle is approximately π/4 — so four times that fraction is an estimate of π. The central question is: how many random samples do you need before your estimate is trustworthy, and how do you *quantify* that trust with a confidence interval?
## Setup
Install `sim-lab` and use the `MonteCarloSimulation` class directly: `pip install sim-lab`.
## Instructions
1. The `MonteCarlo` engine takes two functions: a `sample_function` that produces one random sample, and an `evaluation_function` that reduces that sample to a number. Here a "sample" is a random point `(x, y)` in the unit square, and its "evaluation" is `1.0` if it lands inside the quarter unit circle and `0.0` otherwise.
2. Define the two functions below. Note that the mean of the indicator is π/4, so the engine's mean × 4 estimates π.

```python
import numpy as np
from sim_lab.core import MonteCarloSimulation

# Sample: one random point in the unit square [0, 1] x [0, 1].
def sample_point():
    return (np.random.random(), np.random.random())

# Evaluate: 1.0 inside the quarter circle of radius 1, else 0.0.
def in_unit_circle(point):
    x, y = point
    return 1.0 if x**2 + y**2 <= 1.0 else 0.0
```

3. Build the simulator with `num_samples=2000` points per "day", `days=30`, and a fixed seed. Each day is an independent estimate of π/4 from a fresh batch of points.

```python
sim = MonteCarloSimulation(
    sample_function=sample_point,
    evaluation_function=in_unit_circle,
    num_samples=2000,
    days=30,
    random_seed=42,
)

daily_means = sim.run_simulation()          # list of ~pi/4 means
pi_estimates = [4.0 * m for m in daily_means]
print("Mean estimate:", round(np.mean(pi_estimates), 4))
print("True pi:      ", round(np.pi, 4))
```

4. Convert the engine's 95% confidence intervals (returned in π/4 units) into π units, and check the **validation**: the true π should fall inside the interval for (almost) every day.

```python
ci = sim.get_confidence_intervals()         # (lower, upper) per day, in pi/4 units
ci_lo = [4.0 * lo for lo, _ in ci]
ci_hi = [4.0 * hi for _, hi in ci]
covers = np.mean([lo <= np.pi <= hi for lo, hi in zip(ci_lo, ci_hi)])
print("Fraction of days whose 95% CI contains pi:", round(covers, 3))
```

5. Watch the estimate converge as the sample size grows using `get_convergence_analysis()`. It reports the running mean of the final day's batch at sizes `[10, 50, 100, 500, 1000, 2000]`.

```python
conv = sim.get_convergence_analysis()
print("Sample sizes:", conv["sample_sizes"])
print("pi at each size:", [round(4.0 * m, 4) for m in conv["means"]])
```
## Things to explore
- Re-run with `num_samples` of 100, 1000, and 10000 (set `days=1`). How does the width of the 95% CI shrink? Does the error roughly halve each time you quadruple the sample count (the $1/\sqrt{N}$ rate)?
- Fix `num_samples` and increase `days` to 100. What fraction of the daily CIs cover π? It should be close to 95%.
- Replace the circle indicator with a different estimator — for example, sample `x` uniformly on `[0,1]` and evaluate `e**(-x**2)` to estimate $\int_0^1 e^{-x^2}\,dx$. Does the same $1/\sqrt{N}$ convergence apply?
- What happens if you forget to set `random_seed`? Run twice and confirm the answers differ; set it to `42` and confirm they match exactly.
## Extension ideas
- Estimate the 3-D volume of a unit sphere by sampling in the unit cube `[0,1]^3`; the same `4·mean... ` logic generalizes — work out the new multiplier analytically first.
- Plot the convergence error $|\hat\pi - \pi|$ against sample size on a log–log axis and fit the slope to verify it is approximately $-1/2$.
- Implement an antithetic-variance reduction (pair each point `(x,y)` with `(1-x, 1-y)`) and measure how much it tightens the CI for the same `num_samples`.
## Assessment criteria
- [ ] **Reproducibility**: code sets `random_seed=42` and produces identical estimates on re-run.
- [ ] **Validation against π**: the mean estimate converges toward π as `num_samples` grows (clearly demonstrated via `get_convergence_analysis`), and the 95% CI (×4) contains π on roughly 95% of days.
- [ ] **Analysis**: the write-up explains *why* the mean × 4 equals π, and discusses the observed convergence rate and CI coverage.
- [ ] **Code quality**: the `sample_function` / `evaluation_function` split is clean and correct, and the indicator math matches the quarter-circle definition.
