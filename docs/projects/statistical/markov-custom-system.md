# Build a Custom Markov System
**Difficulty**: Intermediate
**Time**: ~45 minutes
**Learning Focus**: Building transition matrices; the stationary distribution as a left eigenvector
**Simulator**: MarkovChainSimulation (registry `MarkovChain`)
## Overview
Any system whose next state depends only on its current state is a Markov chain. In this project you choose your own 3-state system — for example the market share of three competing brands, where each month a customer either stays loyal or switches — encode it as a transition matrix, then analyze its long-run behavior. The central question: what is the long-run distribution of states, and how can you derive it two independent ways (by simulation and by linear algebra)?
## Setup
Install `sim-lab` and use `MarkovChainSimulation` directly: `pip install sim-lab`.
## Instructions
1. Pick a 3-state system of your own. This example models three brands (`A`, `B`, `C`) and the monthly brand-switching probabilities of a single customer: each row lists the probability of moving *from* that brand *to* each brand. Define the matrix as a NumPy array and verify every row sums to 1.

```python
import numpy as np
from sim_lab.core import MarkovChainSimulation

# Rows = "from" brand, columns = "to" brand. Order: A, B, C.
transition_matrix = np.array([
    [0.80, 0.15, 0.05],   # from A: 80% stay, 15% -> B, 5% -> C
    [0.20, 0.60, 0.20],   # from B
    [0.10, 0.30, 0.60],   # from C
])

# Validation 1: every row must sum to 1 (the engine checks this too).
print("Row sums:", transition_matrix.sum(axis=1))
```

2. Wrap the matrix in a `MarkovChainSimulation`, give the states names, pick a starting brand, and run a long simulation with a fixed seed.

```python
sim = MarkovChainSimulation(
    transition_matrix=transition_matrix,
    states=["Brand A", "Brand B", "Brand C"],
    initial_state="Brand A",
    days=20000,
    random_seed=42,
)
sim.run_simulation()
empirical = sim.get_state_distribution()
```

3. Compute the stationary distribution analytically with the engine's `compute_stationary_distribution()` (it solves for the left eigenvector with eigenvalue 1), and compare it to the empirical frequencies from the long run.

```python
stationary = sim.compute_stationary_distribution()
for state, emp, pi in zip(sim.states, [empirical[s] for s in sim.states], stationary):
    print(f"{state}: empirical={emp:.3f}  stationary={pi:.3f}")
```

4. **Validate independently** that the stationary vector really is the leading left eigenvector of the transition matrix: compute the eigen-decomposition of $P^\top$ and confirm the eigenvector for eigenvalue 1, normalized to sum to 1, matches `stationary`.

```python
eigvals, eigvecs = np.linalg.eig(transition_matrix.T)
i = np.argmin(np.abs(eigvals - 1.0))     # eigenvalue closest to 1
v = np.real(eigvecs[:, i])
v = v / v.sum()                          # normalize to a probability vector
print("Eigenvector method:", np.round(v, 3))
print("Engine method:     ", np.round(stationary, 3))
```
## Things to explore
- Make brand A stickier (raise the `[0,0]` entry and re-balance the row). Does its stationary share rise? By how much per 0.05 of added loyalty?
- Start the chain from `"Brand C"` instead of `"Brand A"`. Does the stationary distribution change? Confirm empirically that it does not.
- Check $\pi P = \pi$ directly by multiplying your stationary vector by the matrix — the result should equal $\pi$ to numerical precision.
- How many steps does `predict_state_probabilities(k)` need before the distribution is within 0.01 of stationary, regardless of the start?
## Extension ideas
- Add a 4th state (e.g. a "No purchase" / churn absorbing state) and analyze how an absorbing state changes the long-run picture (the stationary distribution collapses onto it).
- Build a periodic chain (e.g. strict alternation A→B→A) and show that `compute_stationary_distribution` still returns a fixed point while the *time-averaged* empirical distribution behaves differently — explain why.
- Estimate the mean first-passage time from brand A to brand C from your simulation and compare it to the analytic value.
## Assessment criteria
- [ ] **Reproducibility**: the simulation sets `random_seed=42` so the empirical frequencies are stable across runs.
- [ ] **Validation — rows sum to 1**: the chosen transition matrix is verified to have every row summing to 1 before simulation.
- [ ] **Validation — stationary = leading left eigenvector**: the engine's `compute_stationary_distribution()` is shown to equal the normalized eigenvector of $P^\top$ for eigenvalue 1, and the empirical run frequencies converge to it.
- [ ] **Analysis**: the write-up interprets the stationary distribution in the language of the chosen system (e.g. long-run market share) and explains why it is independent of the initial state.
- [ ] **Code quality**: the matrix construction is correct and clearly commented, and the two solution methods are compared side by side.
