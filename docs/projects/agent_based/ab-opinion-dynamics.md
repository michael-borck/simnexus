# Opinion Dynamics

**Difficulty**: Intermediate
**Time**: ~50 minutes
**Learning Focus**: opinion clustering, bounded-confidence (Hegselmann–Krause) dynamics
**Simulator**: AgentBasedSimulation (registry `"AgentBased"`)

## Overview

How does a population reach consensus — or split into echo chambers? In a
**bounded-confidence** model each agent holds a continuous opinion in `[0, 1]`
and, every step, moves its opinion toward the **average of the neighbours it
trusts**, where trust means "your opinion is within `epsilon` of mine". The
central question: **how does the number of surviving opinion clusters depend on
the confidence bound `epsilon`?**

## Setup

Install sim_lab and use the agent-based interface:

```bash
pip install sim_lab
```

```python
from sim_lab.core import AgentBasedSimulation, Agent
```

Skim the [Agent-Based Simulation docs](../../simulations/agent_based/agent_based.md)
first. The key trick here: set `neighborhood_radius` larger than the field's
diagonal so **every agent is everyone's neighbour** (a fully mixed / mean-field
population); the "trust" filtering then happens inside the agent, based on
*opinion* distance rather than physical distance.

## Instructions

### 1. Define an `OpinionAgent` that averages over trusted neighbours

An agent trusts neighbours whose opinion is within `epsilon` of its own, and
moves its opinion to the mean of that trusted set (including itself).

```python
import numpy as np
from sim_lab.core import AgentBasedSimulation, Agent

EPSILON = 0.15          # confidence bound: agents only listen within +/- EPSILON
N = 200                 # population size
DAYS = 60

class OpinionAgent(Agent):
    def __init__(self, agent_id, position, opinion, epsilon):
        super().__init__(agent_id, {"opinion": opinion}, position)
        self.epsilon = epsilon

    def update(self, environment, neighbors):
        trusted = [self.state["opinion"]]
        for n in neighbors:
            if abs(n.state["opinion"] - self.state["opinion"]) <= self.epsilon:
                trusted.append(n.state["opinion"])
        self.state["opinion"] = sum(trusted) / len(trusted)
```

### 2. Build the factory and run the simulation

Give every agent a position (so the neighbour search works) and a uniform random
opinion. Set `neighborhood_radius=2.0` — bigger than the unit square's diagonal
(√2 ≈ 1.41) — so the population is fully mixed.

```python
def run_opinions(epsilon, seed=42):
    rng = np.random.RandomState(seed)

    def agent_factory(i):
        pos = (float(rng.random()), float(rng.random()))
        opinion = float(rng.random())
        return OpinionAgent(i, pos, opinion, epsilon)

    sim = AgentBasedSimulation(
        agent_factory=agent_factory,
        num_agents=N,
        days=DAYS,
        neighborhood_radius=2.0,        # fully mixed population
        random_seed=seed,
    )
    sim.run_simulation()
    return sim

sim = run_opinions(EPSILON)
opinions = [a.state["opinion"] for a in sim.agents]
```

### 3. Count the surviving opinion clusters

After convergence, sort the opinions and count groups separated by a gap larger
than a small threshold.

```python
def count_clusters(opinions, gap=0.02):
    ordered = sorted(opinions)
    clusters = 1
    for i in range(1, len(ordered)):
        if ordered[i] - ordered[i - 1] > gap:
            clusters += 1
    return clusters

print("clusters at epsilon =", EPSILON, "->", count_clusters(opinions))
```

### 4. Sweep `epsilon` and watch the clusters collapse

A tiny confidence bound fragments the population into many clusters; a wide one
drives everyone to consensus.

```python
import matplotlib.pyplot as plt

epsilons = [0.05, 0.10, 0.15, 0.20, 0.30, 0.50]
clusters = [count_clusters([a.state["opinion"] for a in run_opinions(e).agents])
            for e in epsilons]

plt.plot(epsilons, clusters, "o-")
plt.xlabel("confidence bound epsilon")
plt.ylabel("number of opinion clusters")
plt.title("Wider confidence bound -> fewer clusters")
plt.show()
```

## Validation target

With `random_seed=42`, `N=200`, `DAYS=60` and a cluster gap of `0.02`, the number
of clusters **decreases monotonically as `epsilon` widens** — roughly
**7 → 4 → 3 → 2 → 1 → 1** across `epsilon` = 0.05, 0.10, 0.15, 0.20, 0.30, 0.50.
At `epsilon ≥ 0.3` the whole population converges to a **single consensus
cluster**. This is the defining law of bounded-confidence dynamics: the wider the
confidence bound, the fewer the surviving opinions.

## Things to explore

- Plot a histogram of opinions at the start and at the end for one `epsilon`.
  How sharp are the cluster peaks?
- Lower `N` to 30. Why does the cluster count become jumpier as `epsilon` changes?
- Replace the "average of trusted neighbours" rule with a weighted average that
  trusts nearer opinions more. Does consensus become easier or harder?
- Add a tiny fraction of agents with fixed (extremist) opinions. Where do the
  mainstream clusters end up relative to them?
- What is the smallest `epsilon` that still produces a single cluster? Does it
  match the classic Hegselmann–Krause critical bound?

## Extension ideas

- Move from a fully mixed population to a **spatial** one: shrink
  `neighborhood_radius` so agents only see nearby agents, and watch opinion
  clusters become geographic patches.
- Add **asymmetric** confidence (agents trust those they agree with more than
  those they disagree with) and look for polarisation rather than consensus.
- Track the **mean absolute opinion change per step** and use its decay to detect
  when the system has converged.

## Assessment criteria

- **Reproducibility** — `random_seed=42` is set; reruns give identical cluster
  counts.
- **Validation** — the report shows the cluster count **decreasing as `epsilon`
  widens**, identifies the consensus threshold (`epsilon ≈ 0.3`), and explains the
  bounded-confidence mechanism that produces it.
- **Analysis** — the sweep plot is interpreted, not just produced; students
  connect the number of clusters to the structure of who-trusts-whom.
- **Code quality** — the trust rule is inside the agent, the cluster counter is a
  separate reusable function, and `epsilon`, `N`, and the gap are parameters
  rather than magic numbers.
