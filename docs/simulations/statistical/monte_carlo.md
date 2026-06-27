# Monte Carlo Simulation

## Purpose

This simulation is a general-purpose Monte Carlo engine: it repeatedly draws random samples from a user-supplied `sample_function`, scores each one with an `evaluation_function`, and reports the per-step mean together with 95% confidence intervals. Because the sampling and scoring logic are pluggable, the same class handles numerical integration, risk analysis, option pricing, or any problem where an expectation is easier to estimate by random sampling than to compute analytically. It is an excellent teaching tool for the Law of Large Numbers, the $\mathcal{O}(1/\sqrt{N})$ convergence rate of Monte Carlo methods, and the meaning of a confidence interval.

## Parameters

- `sample_function`: `Callable[[], Any]` — A zero-argument function that generates and returns one random sample (e.g. a point, a path, or a scenario).
- `evaluation_function`: `Callable[[Any], float]` — A function that takes a single sample (the return value of `sample_function`) and reduces it to a numeric value (the quantity whose expectation we are estimating).
- `num_samples`: `int` (default `1000`) — Number of samples to generate per step. Larger values give tighter estimates at the standard Monte Carlo rate.
- `days`: `int` (default `100`) — Number of steps to simulate; each step independently draws `num_samples` fresh samples and records their mean.
- `confidence_interval`: `bool` (default `True`) — Whether to compute a 95% confidence interval for each step's mean. When `False`, `get_confidence_intervals()` raises.
- `random_seed`: `Optional[int]` (default `None`) — Seed for the underlying random number generator, making runs reproducible.

## Example Code

This classic example estimates $\pi$ by sampling points uniformly in the unit square $[0,1]^2$ and counting the fraction that fall inside the quarter unit circle. That fraction is an unbiased estimate of $\pi/4$, so multiplying the mean by $4$ recovers $\pi$.

```python
import numpy as np
import matplotlib.pyplot as plt
from sim_lab.core import MonteCarloSimulation

# Sample: a uniform random point in the unit square [0, 1]^2.
def sample_point():
    return (np.random.random(), np.random.random())

# Evaluate: 1.0 if the point lies inside the quarter unit circle, else 0.0.
def in_unit_circle(point):
    x, y = point
    return 1.0 if x**2 + y**2 <= 1.0 else 0.0

# Estimate pi/4 each day from 2000 fresh samples, over 30 days.
sim = MonteCarloSimulation(
    sample_function=sample_point,
    evaluation_function=in_unit_circle,
    num_samples=2000,
    days=30,
    random_seed=42,
)

daily_means = sim.run_simulation()          # list of per-step means (~ pi/4)
pi_estimates = [4.0 * m for m in daily_means]

ci = sim.get_confidence_intervals()          # (lower, upper) per day, in pi/4 units
ci_lower = [4.0 * lo for lo, _ in ci]
ci_upper = [4.0 * hi for _, hi in ci]

# Plot the daily pi estimates with their 95% confidence bands.
days = range(1, sim.days + 1)
plt.figure(figsize=(10, 6))
plt.plot(days, pi_estimates, label=r'$\hat{\pi}$ (daily estimate)')
plt.fill_between(days, ci_lower, ci_upper, alpha=0.25, label='95% CI')
plt.axhline(y=np.pi, color='red', linestyle='--', label=r'True $\pi$')
plt.xlabel('Day')
plt.ylabel(r'Estimate of $\pi$')
plt.title('Monte Carlo Estimation of π')
plt.legend()
plt.show()

# Inspect convergence of the final day's batch as the sample size grows.
convergence = sim.get_convergence_analysis()
print("Sample sizes:", convergence["sample_sizes"])
print("Running means (×4 → pi estimates):",
      [4.0 * m for m in convergence["means"]])

# Summary statistics over ALL evaluations from every day.
stats = sim.get_statistics()
print("Overall mean (×4 → pi):", 4.0 * stats["mean"])
print("Std dev:", stats["std_dev"])
print("95th percentile:", stats["percentiles"]["95th"])
```

## Use Case Ideas

### Investigate the Law of Large Numbers and Convergence Rate

Explore how the estimate tightens as more samples are drawn. Use `get_convergence_analysis()` to watch the running mean of a single day's batch settle toward the true value.

- How quickly does the error shrink as `num_samples` grows from 10 to 5000? Does the halving pattern match the $\mathcal{O}(1/\sqrt{N})$ rate?
- Compare the convergence curves for a low-variance estimator versus a high-variance one — which reaches a stable answer first?
- At what sample size does the 95% confidence interval consistently cover the true value across all `days`?

### Investigate Numerical Integration by Sampling

Monte Carlo integration turns area/volume estimation into expectation estimation. Replace the circle indicator with the integrand of any other definite integral.

- Estimate the area under $f(x) = e^{-x^2}$ on $[0,1]$ by sampling $x$ uniformly and evaluating $f(x)$; how does the result compare to the analytic value?
- How does raising the dimension of the sample (e.g. integrating over a hypercube) affect the convergence rate compared with grid-based quadrature?
- What happens to the confidence interval width if the evaluation function returns a more spread-out (higher-variance) set of values?

### Investigate Risk Analysis and Tail Behavior

Monte Carlo is the workhorse of quantitative risk modelling. Use a `sample_function` that draws a loss scenario and an `evaluation_function` that returns the loss magnitude, then study the distribution.

- How do the percentile statistics from `get_statistics()` (e.g. the 95th and 99th) reveal tail risk that the mean alone hides?
- Compare a stable, low-volatility scenario distribution with a heavy-tailed one — which has the wider confidence interval, and why?
- How does `random_seed` improve reproducibility when comparing two risk strategies side by side?

## Model Description

Each of the `days` steps is an independent Monte Carlo trial. On step $t$ the simulator draws $N = \texttt{num\_samples}$ i.i.d. samples $x_i = \texttt{sample\_function()}$, evaluates each to $y_i = \texttt{evaluation\_function}(x_i)$, and stores the full batch in `results_history`. The step's point estimate of the target expectation $\mu = \mathbb{E}[Y]$ is the sample mean

$$\bar{y}_t = \frac{1}{N}\sum_{i=1}^{N} y_i.$$

When `confidence_interval` is `True`, the step also reports a 95% confidence interval built from the **sample** standard deviation ($\text{ddof}=1$) and the normal approximation:

$$s_t = \sqrt{\frac{1}{N-1}\sum_{i=1}^{N}(y_i - \bar{y}_t)^2}, \qquad \text{CI}_t = \bar{y}_t \pm 1.96 \cdot \frac{s_t}{\sqrt{N}}.$$

Three accessors summarize the run:

- `get_statistics()` flattens every evaluation from every step into one pool and returns its `mean`, `std_dev` (again $\text{ddof}=1$), `min`, `max`, and a `percentiles` sub-dictionary of the 25th, 50th, 75th, 95th, and 99th percentiles.
- `get_confidence_intervals()` returns the per-step $(\text{lower}, \text{upper})$ tuples described above (and raises if `confidence_interval=False`).
- `get_convergence_analysis()` takes the **final** step's batch and reports running means at the sample sizes `[10, 50, 100, 500, 1000, 5000]` (filtered to those $\le \texttt{num\_samples}$, with `num_samples` always appended), illustrating the Law of Large Numbers: $\bar{y} \to \mu$ as $N \to \infty$, with error shrinking at the standard Monte Carlo rate $\mathcal{O}(1/\sqrt{N})$.

In the $\pi$ example, $x = (u, v)$ is uniform on $[0,1]^2$ and $y = \mathbf{1}\{u^2 + v^2 \le 1\}$ is the inside-the-quarter-circle indicator. Its expectation is the ratio of the quarter-disk area to the unit-square area, $\mathbb{E}[Y] = (\pi/4) / 1 = \pi/4$, so $4\bar{y}$ is an unbiased estimator of $\pi$.
