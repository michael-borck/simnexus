# Epidemic Spread on Networks

**Difficulty**: Intermediate
**Time**: ~55 minutes
**Learning Focus**: how network topology shapes diffusion; SI epidemics on random, scale-free, and small-world graphs
**Simulator**: NetworkSimulation (registry `"Network"`)

## Overview
The same contagion rule produces wildly different outbreaks depending on *who is connected to whom*. On a **scale-free** network a few high-degree hubs ignite explosive, threshold-free spread; **small-world** shortcuts let the infection jump across the graph far faster than a pure lattice. You will run an SI epidemic on three topologies built with sim-lab's network generators, plot the infected fraction over time, and compare the speed and final reach of each.

## Setup
Install sim-lab (`pip install sim_lab`) and use a Jupyter notebook. sim-lab's network generators and the per-step spread both draw from Python's `random` module, so a single `random.seed(42)` makes the whole pipeline reproducible. See the [Network doc page](../../simulations/network/network.md).

## Instructions

1. **Pick the epidemic rule and network size.** SI = "once infected, always infected"; each day a susceptible node with an infected neighbour catches the disease with probability `BETA` per infected contact.

```python
import random
import matplotlib.pyplot as plt
from sim_lab.core import (
    create_random_network, create_scale_free_network, create_small_world_network,
)

N = 500
BETA = 0.10          # per-contact infection probability per day
DAYS = 40
```

2. **Build a topology matcher.** To make the comparison fair, give every topology roughly the same *mean degree* (~4): `edge_probability = 4/(N−1)` for Erdős–Rényi, `m = 2` for Barabási–Albert (mean degree `2m`), and `k = 4` for Watts–Strogatz. A "lattice" is just Watts–Strogatz with `beta = 0` (no shortcut rewiring).

```python
def build_network(kind):
    if kind == "random":
        return create_random_network(N, edge_probability=4 / (N - 1))
    if kind == "scale_free":
        return create_scale_free_network(N, m=2)
    if kind == "small_world":
        return create_small_world_network(N, k=4, beta=0.15)
    if kind == "lattice":
        return create_small_world_network(N, k=4, beta=0.0)
```

3. **Write the SI spread as the network's update function.** Each node carries a `state` attribute (`"S"` or `"I"`). The update is **synchronous** — collect the newly infected first, then flip them — so the order of iteration within a day does not matter. Record the infected count each day on the network object.

```python
def si_update(network, day):
    new_infected = []
    for nid, node in network.nodes.items():
        if node.attributes.get("state") == "S":
            for nb in node.neighbors:
                if network.nodes[nb].attributes.get("state") == "I":
                    if random.random() < BETA:
                        new_infected.append(nid)
                        break
    for nid in new_infected:
        network.nodes[nid].update_attribute("state", "I")
    infected = sum(1 for n in network.nodes.values() if n.attributes.get("state") == "I")
    network.infected_counts.append(infected)
```

4. **Run all four topologies from a single patient zero.** Seed the RNG *inside* the loop so each topology is independently reproducible from `seed = 42` (otherwise earlier builds would eat the random stream of later ones).

```python
def run_si(kind):
    random.seed(42)                       # reproducible topology + spread
    net = build_network(kind)
    for nid in net.nodes:                 # everyone starts susceptible...
        net.nodes[nid].update_attribute("state", "S")
    net.nodes[0].update_attribute("state", "I")   # ...except patient zero
    net.infected_counts = [1]             # day-0 count
    net.update_function = si_update
    net.days = DAYS                       # run_simulation loops day = 1 .. DAYS-1
    net.run_simulation()
    return [c / N for c in net.infected_counts]

curves = {kind: run_si(kind) for kind in ["random", "scale_free", "small_world", "lattice"]}
```

5. **Plot the infected fraction over time and read off the comparison.**

```python
fig, ax = plt.subplots(figsize=(10, 6))
for kind, frac in curves.items():
    ax.plot(frac, label=kind)
ax.set_xlabel("Day"); ax.set_ylabel("Infected fraction"); ax.legend()
ax.set_title("SI epidemic across network topologies (mean degree ~4)"); plt.show()

for kind, frac in curves.items():
    print(f"{kind:12s} final fraction = {frac[-1]:.3f}")
```

6. **Compare the speed of spread.** Report the day each topology first reaches 50% infected (use `None` if it never does). The expected ordering is **scale-free fastest**, and **small-world faster than the pure lattice**.

```python
def day_to_fraction(frac, target=0.5):
    for d, f in enumerate(frac):
        if f >= target:
            return d
    return None

for kind, frac in curves.items():
    print(f"{kind:12s} day to reach 50% infected = {day_to_fraction(frac)}")
```

## Things to explore
- Lower `BETA` until the outbreak stalls on the random graph but still sweeps the scale-free graph. This is the "vanishing epidemic threshold" of scale-free networks in miniature.
- Increase the small-world rewiring `beta` from `0` to `1`. At what rewiring fraction does the lattice's slow spread turn into a fast outbreak?
- Vary `m` on the scale-free graph (more edges per new node). Does the *final* fraction change, or only the *speed*?
- Seed patient zero at a high-degree hub instead of node 0. Does it change the scale-free curve much? Does it change the lattice curve?

## Extension ideas
- Upgrade the model to **SIR** by adding a recovery attribute: each infected node recovers (state `"R"`, no longer infectious) with daily probability `gamma`. Now the *final* infected fraction differs sharply by topology — plot it for `gamma` in `{0.02, 0.05, 0.1}`.
- Add `save_history=True` to the network and use `get_node_attribute_history(node_id, "state")` to draw the infection's wavefront across the graph over time.
- Compare the degree distributions with `get_degree_distribution()` and correlate each topology's hub count with its outbreak speed.

## Assessment criteria
- **Reproducibility** — `random.seed(42)` is set before each topology build, so re-running yields identical curves and final fractions.
- **Validation (scale-free speed)** — the scale-free network reaches 50% infected no later than the random and small-world networks (hubs drive fast, threshold-free spread).
- **Validation (small-world vs lattice)** — the small-world network (rewired, `beta > 0`) reaches 50% infected strictly earlier than the pure lattice (`beta = 0`).
- **Validation (fair comparison)** — the four topologies are built with comparable mean degree (~4), so differences are attributed to topology, not edge count.
- **Analysis** — the student connects the degree distribution (presence/absence of hubs and shortcuts) to each curve's slope, not just reporting which is fastest.
- **Code quality** — the SI rule lives in one reusable update function; the topology builder is parameterised; no copy-pasted spread loops.
