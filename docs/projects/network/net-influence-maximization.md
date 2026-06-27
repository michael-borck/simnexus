# Influence Maximisation

**Difficulty**: Advanced
**Time**: ~75 minutes
**Learning Focus**: seed-set selection for cascade spread; greedy vs degree-based vs random heuristics
**Simulator**: NetworkSimulation (registry `"Network"`)

## Overview
Given a fixed budget of `k` "seed" nodes, which should you activate to maximise how far a contagion spreads through a social network? This is the **influence-maximisation** problem. You will build a scale-free network, define a stochastic SI cascade, and compare three seed-selection strategies — **random**, **high-degree**, and the classic **greedy** marginal-gain algorithm — measuring final spread by Monte-Carlo averaging. The expected pecking order is random ≪ high-degree ≲ greedy.

## Setup
Install sim-lab (`pip install sim_lab`) and use a Jupyter notebook. Network generation and the cascade both use Python's `random` module, so seed it with `random.seed(42)` before building the graph. See the [Network doc page](../../simulations/network/network.md).

## Instructions

1. **Build the network and set the cascade parameters.** Scale-free graphs are the canonical test bed because their hubs carry most of the influence.

```python
import random
import matplotlib.pyplot as plt
from sim_lab.core import create_scale_free_network

random.seed(42)
N = 200
network = create_scale_free_network(N, m=2)

BETA = 0.06        # per-contact infection probability per step (low enough that coverage/overlap matters)
HORIZON = 20       # cascade length
K = 5              # seed-set budget
R = 50             # Monte-Carlo realisations for spread estimation (enough that greedy is not noise-dominated)
```

2. **Define the cascade primitive.** Given a seed set, run a synchronous SI process for `HORIZON` steps and return how many nodes are infected at the end. Pass in a dedicated `random.Random` instance so every estimate is reproducible and independent.

```python
def spread_size(net, seeds, rng):
    state = {n: ("I" if n in seeds else "S") for n in net.nodes}
    for _ in range(HORIZON):
        newly = []
        for nid in net.nodes:
            if state[nid] == "S":
                for nb in net.nodes[nid].neighbors:
                    if state[nb] == "I" and rng.random() < BETA:
                        newly.append(nid)
                        break
        if not newly:
            break
        for nid in newly:
            state[nid] = "I"
    return sum(1 for v in state.values() if v == "I")

def estimate_spread(net, seeds, realizations, seed):
    rng = random.Random(seed)
    return sum(spread_size(net, seeds, rng) for _ in range(realizations)) / realizations
```

3. **Strategy 1 — random seeds.** Pick `k` nodes uniformly at random.

```python
nodes = list(network.nodes)
degrees = {n: len(network.nodes[n].neighbors) for n in nodes}

random_seeds = random.Random(7).sample(nodes, K)
```

4. **Strategy 2 — high-degree (targeted) seeds.** Pick the `k` highest-degree nodes — the hubs.

```python
degree_seeds = sorted(degrees, key=degrees.get, reverse=True)[:K]
```

5. **Strategy 3 — greedy marginal gain.** Start with an empty seed set. Each round, add the node whose *marginal* increase in estimated spread is largest. To keep it tractable, search only the top candidates by degree (influence-maximising seeds are almost always near the hubs).

```python
CANDIDATES = 50
candidate_pool = sorted(degrees, key=degrees.get, reverse=True)[:CANDIDATES]

greedy_seeds = []
for _ in range(K):
    best_node, best_gain = None, -1.0
    base = estimate_spread(network, greedy_seeds, R, seed=123)
    for n in candidate_pool:
        if n in greedy_seeds:
            continue
        gain = estimate_spread(network, greedy_seeds + [n], R, seed=123) - base
        if gain > best_gain:
            best_gain, best_node = gain, n
    greedy_seeds.append(best_node)

print("random seeds:    ", random_seeds)
print("high-degree seeds:", degree_seeds)
print("greedy seeds:     ", greedy_seeds)
```

6. **Evaluate all three with a large, stable Monte-Carlo sample and compare.** Average over many realisations so the comparison is not noise.

```python
EVAL = 200
results = {
    "random":     estimate_spread(network, random_seeds, EVAL, seed=999),
    "high-degree": estimate_spread(network, degree_seeds, EVAL, seed=999),
    "greedy":     estimate_spread(network, greedy_seeds, EVAL, seed=999),
}

fig, ax = plt.subplots(figsize=(8, 5))
ax.bar(results.keys(), results.values(), color=["tab:grey", "tab:orange", "tab:green"])
ax.set_ylabel("Average final spread (infected nodes)")
ax.set_title(f"Influence maximisation on a scale-free network (k={K})")
for i, v in enumerate(results.values()):
    ax.text(i, v, f"{v:.1f}", ha="center", va="bottom")
plt.show()
```

## Things to explore
- Plot `estimate_spread` as a function of `k` (1 to ~15) for each strategy. Where does greedy's advantage over high-degree shrink?
- Vary `BETA`. At very low transmission probability the cascade dies out — which strategy survives longest, and why?
- Try the same three strategies on a *random* (Erdős–Rényi) network instead of scale-free. Does greedy still beat high-degree, or do they tie?
- Reduce `R` (the estimation sample) to 3. How unstable does greedy's choice become, and how does that hurt its *evaluated* spread?

## Extension ideas
- Replace the SI cascade with **independent cascade**: each infected node gets exactly one chance (per neighbour, at the moment of infection) to transmit, drawn from a fixed probability. Re-run greedy — do the chosen seeds change?
- Implement the **CELF** lazy-forwarding optimisation: cache each candidate's marginal gain and re-evaluate only the top of a priority queue each round. How many spread simulations does it save versus plain greedy?
- Weight edges (e.g. by a similarity score) and make `BETA` edge-dependent. Does targeting high-strength nodes beat targeting high-degree nodes?

## Assessment criteria
- **Reproducibility** — `random.seed(42)` fixes the network; each Monte-Carlo estimate uses a fixed `seed`, so every reported spread is repeatable.
- **Validation (heuristic ordering)** — the high-degree spread is shown to exceed the random spread; greedy is shown to be at least as good as high-degree (within Monte-Carlo noise).
- **Validation (Monte-Carlo rigour)** — final comparison uses a large sample (`EVAL ≫ R`); the student reports averages, not single noisy realisations.
- **Analysis** — the student explains *why* high-degree beats random (hub reach) and why greedy can still edge it out (coverage / overlap between hubs' neighbourhoods).
- **Code quality** — the cascade is a single reusable `spread_size` primitive; the greedy loop is parameterised by `K`, `R`, and the candidate pool; no duplicated spread code.
