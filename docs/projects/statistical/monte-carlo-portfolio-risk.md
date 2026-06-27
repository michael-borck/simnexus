# Portfolio Risk (Value at Risk)
**Difficulty**: Advanced
**Time**: ~60 minutes
**Learning Focus**: Monte Carlo risk modelling; tail-risk percentiles (Value at Risk)
**Simulator**: MonteCarloSimulation (registry `MonteCarlo`)
## Overview
Value at Risk (VaR) answers a question every portfolio manager faces: *"How much could I lose on a bad day?"* The 95% VaR is the loss that is exceeded only 5% of the time — equivalently, the negative of the 5th percentile of the return distribution. Because the Monte Carlo engine lets you plug in *any* random scenario, you can simulate thousands of correlated asset-return scenarios, build the portfolio return distribution, and read its tail directly. The central question: how does the correlation between two assets change the portfolio's tail risk?
## Setup
Install `sim-lab` and use `MonteCarloSimulation` directly: `pip install sim-lab`.
## Instructions
1. Define a 2-asset world: each asset has a daily mean return, a volatility, and a correlation `rho`. The `sample_function` draws one correlated return scenario using `np.random.multivariate_normal`; the `evaluation_function` weights the two returns into a single portfolio return.

```python
import numpy as np
from sim_lab.core import MonteCarloSimulation

mu = np.array([0.0005, 0.0008])      # mean daily return of each asset
vol = np.array([0.012, 0.018])       # daily volatility of each asset
rho = 0.3                            # correlation between the two assets
weights = np.array([0.5, 0.5])       # equal-weighted portfolio

cov = np.array([
    [vol[0]**2,            rho * vol[0] * vol[1]],
    [rho * vol[0] * vol[1], vol[1]**2           ],
])

def sample_scenario():
    return np.random.multivariate_normal(mu, cov)

def portfolio_return(scenario):
    return float(np.dot(weights, scenario))
```

2. Run a large batch (one "day" with many samples) with a fixed seed. Setting `confidence_interval=False` is fine here — we want the raw return pool, not the mean's CI.

```python
sim = MonteCarloSimulation(
    sample_function=sample_scenario,
    evaluation_function=portfolio_return,
    num_samples=20000,
    days=1,
    confidence_interval=False,
    random_seed=42,
)
sim.run_simulation()
returns = np.array([v for batch in sim.results_history for v in batch])
```

3. Compute the 95% VaR. The 5th percentile of returns is the return threshold breached only 5% of the time, so VaR is its negative (a positive loss magnitude).

```python
var_95 = -np.percentile(returns, 5)
print("95% VaR (loss):", round(var_95, 5))
```

4. **Validate** the diversification effect: rebuild the model with a high correlation (`rho = 0.9`) and a low correlation (`rho = 0.1`), keeping everything else fixed, and compare the VaR magnitudes. With a fixed seed the only thing changing is the correlation.

```python
def var_for_correlation(rho):
    cov = np.array([[vol[0]**2, rho*vol[0]*vol[1]],
                    [rho*vol[0]*vol[1], vol[1]**2]])
    s = MonteCarloSimulation(
        sample_function=lambda: np.random.multivariate_normal(mu, cov),
        evaluation_function=portfolio_return,
        num_samples=20000, days=1, confidence_interval=False, random_seed=42,
    )
    s.run_simulation()
    r = np.array([v for batch in s.results_history for v in batch])
    return -np.percentile(r, 5)

for rho in [0.1, 0.3, 0.5, 0.9]:
    print(f"rho={rho}:  95% VaR = {var_for_correlation(rho):.5f}")
```
## Things to explore
- Confirm the analytic portfolio volatility formula $\sigma_p = \sqrt{w_1^2\sigma_1^2 + w_2^2\sigma_2^2 + 2 w_1 w_2 \rho \sigma_1 \sigma_2}$ against the sample standard deviation of your simulated returns. They should match closely.
- Convert the 95% VaR into the parametric (variance–covariance) estimate $1.645\,\sigma_p$ and compare it to the simulated percentile VaR. When do they disagree, and why?
- Move to the 99% VaR (the 1st percentile). Is the gap between the parametric and simulated estimates larger or smaller in the tail?
- Add a third asset and explore how the VaR changes as you vary the weights while keeping correlations fixed.
## Extension ideas
- Make one asset heavy-tailed by sampling its return from a Student-t distribution instead of a normal, and measure how much the VaR jumps relative to the Gaussian case.
- Compute Expected Shortfall (CVaR) — the average loss *conditional on* exceeding the VaR threshold — and argue why it is a stricter risk measure than VaR.
- Build a back-test: generate 252 trading days of scenarios and count how often the daily loss actually exceeds your 95% VaR. It should be roughly 5% of days.
## Assessment criteria
- [ ] **Reproducibility**: every run sets `random_seed=42` so VaR comparisons across correlations differ *only* because of `rho`, not RNG noise.
- [ ] **Validation — VaR definition**: the reported 95% VaR is exactly the negative of the 5th percentile of the simulated returns (verified numerically, not assumed).
- [ ] **Validation — diversification**: the write-up demonstrates that VaR magnitude *decreases* as correlation drops, matching $\sigma_p$'s dependence on $\rho$.
- [ ] **Analysis**: the interpretation distinguishes the percentile-based VaR from the parametric $1.645\sigma_p$ estimate and explains any discrepancy.
- [ ] **Code quality**: the correlated-sampling `sample_function` is built from a correct covariance matrix, and the return-flattening step pools all scenarios correctly.
