# Markov Chain Simulation

## Purpose

This simulation models discrete-time Markov chains — stochastic processes where the next state depends only on the current state and not on the history that led to it. It is a cornerstone example for teaching the Markov property, transition matrices, and the concept of a stationary (long-run) distribution. Because the same engine drives weather forecasting, random walks, and inventory policies, it also shows how a single mathematical idea describes systems across very different domains.

## Parameters

- `transition_matrix`: `np.ndarray` — Square matrix of transition probabilities between states. Each row must sum to 1 (a stochastic matrix); entry $p_{ij}$ is the probability of moving from state $i$ to state $j$ in one step.
- `states`: `List[Any]` (optional) — Human-readable names or values for each state, in row/column order. If `None`, the states are numbered `[0, 1, 2, ...]`. The length must match the dimension of the transition matrix.
- `initial_state`: `int` or state name (optional) — Index or name of the state to start from. If `None`, a state is chosen uniformly at random.
- `days`: `int` (default `100`) — Number of time steps to simulate (the length of the returned state history).
- `random_seed`: `int` (optional) — Seed for reproducible random number generation.

## Example Code

```python
from sim_lab.core import create_weather_model
import matplotlib.pyplot as plt

# Build a 3-state weather chain (Sunny / Cloudy / Rainy) using the weather factory.
sim = create_weather_model(
    sunny_to_sunny=0.7, sunny_to_cloudy=0.2, sunny_to_rainy=0.1,
    cloudy_to_sunny=0.3, cloudy_to_cloudy=0.4, cloudy_to_rainy=0.3,
    rainy_to_sunny=0.2, rainy_to_cloudy=0.3, rainy_to_rainy=0.5,
    initial_state="Sunny",
    days=30,
)

history = sim.run_simulation()                  # list of state indices, length == days
names = sim.get_state_names()                   # ["Sunny", "Cloudy", ...] aligned to history
stationary = sim.compute_stationary_distribution()  # long-run probability of each state

# Map string states to vertical positions so the sequence is easy to read.
code = {"Rainy": 0, "Cloudy": 1, "Sunny": 2}

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

ax1.step(range(len(names)), [code[n] for n in names], where="mid")
ax1.set_yticks([0, 1, 2])
ax1.set_yticklabels(["Rainy", "Cloudy", "Sunny"])
ax1.set_xlabel("Day")
ax1.set_title("Simulated 30-Day Weather Sequence")

ax2.bar(sim.states, stationary)
ax2.set_ylabel("Stationary probability")
ax2.set_title("Stationary Distribution of the Weather Chain")

plt.tight_layout()
plt.show()
```

## Use Case Ideas

### Investigate How Transition Probabilities Shape the Long-Run Distribution

Use `compute_stationary_distribution()` to predict the long-run fraction of days spent in each state, then check the prediction against the empirical frequencies returned by `get_state_distribution()` over a very long run. Questions to Consider:

  - If Sunny $\to$ Sunny persistence rises, does the stationary probability of Sunny increase, and by how much?
  - How many steps are needed before the observed frequencies stay close to the stationary distribution?
  - Can you design a transition matrix whose stationary distribution is uniform across all states?

### Investigate the Inventory Model's Restocking Policy

Run `create_inventory_model` and watch how the demand distribution and reorder point drive the inventory level over time. Questions to Consider:

  - What happens to the stationary distribution of stock levels when `order_amount` increases?
  - Which inventory level is occupied most often in the long run, and why?
  - How does a spikier `demand_probs` distribution change the chance of hitting zero stock?

### Investigate a Biased Random Walk Between Reflecting Boundaries

Use `create_random_walk` with `p_up != p_down` and observe the effect of the reflecting barriers at `min_position` and `max_position`. Questions to Consider:

  - With `p_up = 0.7`, does the chain spend most of its time near the top boundary?
  - Where does the walk's stationary distribution place its peak, and how does the boundary force explain it?
  - How does widening the range `[min_position, max_position]` change the spread of the distribution?

## Model Description

A discrete-time Markov chain is a sequence of random states $X_0, X_1, X_2, \dots$ satisfying the **Markov property**: the future depends only on the present, not on the past:

$$P(X_{n+1} = j \mid X_n = i,\; X_{n-1}, \dots, X_0) \;=\; P(X_{n+1} = j \mid X_n = i) \;=\; p_{ij}.$$

The behaviour of the whole chain is encoded in the **transition matrix** $P = [p_{ij}]$, where row $i$ lists the probabilities of moving from state $i$ to every other state. Each row is a probability distribution, so it must sum to 1 (the simulation validates this in `__init__`).

### Stepping and running

Each call to `step()` draws the next state from the current state's row of $P$ using `np.random.choice`, appends it to `state_history`, and returns its index. `run_simulation()` resets the chain to `initial_state` and then advances `days - 1` steps, returning the full list of state indices (length `days`). `get_state_names()` maps those indices back to the `states` labels, and `get_state_distribution()` returns the empirical frequency of each state over the history.

### Stationary distribution

The **stationary distribution** $\pi$ is the long-run proportion of time the chain spends in each state. It is the probability vector that no longer changes under the transition matrix:

$$\pi \, P \;=\; \pi, \qquad \sum_i \pi_i = 1, \quad \pi_i \ge 0.$$

Geometrically, $\pi$ is the (normalized) left eigenvector of $P$ with eigenvalue 1. `compute_stationary_distribution()` finds it exactly this way: it computes the eigenvectors of $P^{\top}$, selects the one whose eigenvalue is 1, discards any imaginary residue, and normalizes it to sum to 1. For any chain with a unique such eigenvector this gives the exact limiting distribution. As a check, `predict_state_probabilities(steps)` starts from a point mass on the current state and multiplies by $P$ `steps` times ($\pi^{(0)} P^{\,k}$), showing how the state distribution converges toward $\pi$ as $k$ grows.

### Pre-built model factories

Three factory functions assemble commonly taught chains so you can skip writing the matrix by hand:

- `create_weather_model(...)` — A 3-state chain over `["Sunny", "Cloudy", "Rainy"]`. Each of the nine keyword arguments (`sunny_to_sunny`, `sunny_to_cloudy`, … `rainy_to_rainy`) is one row entry of the $3\times3$ matrix; `initial_state` is a state name and `days` sets the run length.
- `create_random_walk(p_up, p_down, initial_position, min_position, max_position, days)` — A chain over the integer positions from `min_position` to `max_position`. `p_up`/`p_down` are renormalized to sum to 1. Interior positions move up with probability $p_{\text{up}}$ and down with $p_{\text{down}}$; the boundaries are **reflecting** — at `min_position` the walk always moves up, and at `max_position` it always moves down.
- `create_inventory_model(demand_probs, max_inventory, order_amount, days)` — A chain over inventory levels $0, 1, \dots, \text{max\_inventory}$, starting fully stocked. Each step subtracts a random demand drawn from `demand_probs` (index = units demanded), clamped at 0; whenever inventory hits 0 it is immediately restocked to $\min(\text{max\_inventory}, \text{order\_amount})$. The resulting transition probabilities accumulate demand outcomes that lead to the same level.

See the source at `src/sim_lab/core/markov_chain_simulation.py` for the exact row-by-row construction of each matrix.
