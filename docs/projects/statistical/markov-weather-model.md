# Weather Prediction with a Markov Chain
**Difficulty**: Beginner
**Time**: ~25 minutes
**Learning Focus**: The Markov property; stationary (long-run) distributions
**Simulator**: MarkovChainSimulation (registry `MarkovChain`)
## Overview
Tomorrow's weather depends (roughly) only on today's weather — not on last week. That "memoryless" structure is exactly a Markov chain: each day the weather transitions from its current state (Sunny / Cloudy / Rainy) to the next according to fixed probabilities. The central question is twofold: given it is Sunny today, what is the probability of each weather state tomorrow, and over a long run, what fraction of days are Sunny, Cloudy, or Rainy?
## Setup
Install `sim-lab` and use the ready-made `create_weather_model` factory: `pip install sim-lab`.
## Instructions
1. Build the 3-state weather chain. The factory assembles the transition matrix from the nine `from_to` probabilities and starts the chain on a Sunny day.

```python
import numpy as np
from sim_lab.core import create_weather_model

sim = create_weather_model(
    sunny_to_sunny=0.7, sunny_to_cloudy=0.2, sunny_to_rainy=0.1,
    cloudy_to_sunny=0.3, cloudy_to_cloudy=0.4, cloudy_to_rainy=0.3,
    rainy_to_sunny=0.2, rainy_to_cloudy=0.3, rainy_to_rainy=0.5,
    initial_state="Sunny",
    days=10000,
)
# The factory has no seed argument; set it on the object so the run is reproducible.
sim.random_seed = 42
```

2. Predict tomorrow's distribution from today's state. `predict_state_probabilities(steps)` starts from a point mass on the current state and multiplies by the transition matrix `steps` times.

```python
print("Next-day forecast from Sunny:", sim.predict_state_probabilities(1))
print("Forecast 3 days ahead:      ", sim.predict_state_probabilities(3))
```

3. Run a long simulation (10 000 days) and record the realized weather, then compute the *empirical* fraction of days spent in each state.

```python
sim.run_simulation()
empirical = sim.get_state_distribution()
for state, freq in empirical.items():
    print(f"{state}: {freq:.3f}")
```

4. Compute the chain's *stationary* distribution — the theoretical long-run frequency — and **validate** that the empirical frequencies from step 3 match it.

```python
stationary = sim.compute_stationary_distribution()
for state, p in zip(sim.states, stationary):
    print(f"{state}: stationary={p:.3f}  empirical={empirical[state]:.3f}")
```
## Things to explore
- Shorten the run to `days=50` and re-compare empirical vs stationary. How far off is it? Increase to `days=10000` again — does the gap shrink as the run lengthens?
- Raise `sunny_to_sunny` from 0.7 to 0.85 (and lower the other two Sunny→ probabilities so the row still sums to 1). How much does the stationary probability of Sunny increase?
- Start the chain from `"Rainy"` instead of `"Sunny"`. Does the stationary distribution change? Should it?
- Predict the distribution 1, 5, 10, and 50 steps ahead with `predict_state_probabilities`. Does it converge toward the stationary distribution?
## Extension ideas
- Design a transition matrix whose stationary distribution is exactly uniform (⅓, ⅓, ⅓), and verify it both analytically and empirically.
- Add a fourth state (e.g. "Stormy") and rebuild the matrix by hand using `MarkovChainSimulation` directly.
- Estimate the *expected length* of a Sunny streak from the simulation and check it against $1/(1-p_{\text{sunny}\to\text{sunny}})$.
## Assessment criteria
- [ ] **Reproducibility**: the run is seeded (`sim.random_seed = 42`) so the realized sequence and empirical frequencies are identical on re-run.
- [ ] **Validation against the stationary distribution**: the empirical frequencies from `get_state_distribution()` over a long run converge to `compute_stationary_distribution()`, and the gap is shown to shrink as `days` grows.
- [ ] **Analysis**: the write-up uses the Markov property to interpret the next-day forecast and explains why the stationary distribution does not depend on the starting state.
- [ ] **Code quality**: the `create_weather_model` arguments are used correctly (each row of the implied matrix sums to 1) and the empirical/stationary comparison is printed clearly.
