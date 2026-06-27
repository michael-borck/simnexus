# Schelling Segregation

**Difficulty**: Advanced
**Time**: ~75 minutes
**Learning Focus**: emergent segregation, building custom agents and an environment
**Simulator**: AgentBasedSimulation (registry `"AgentBased"`)

## Overview

Why do cities divide into homogeneous neighbourhoods even when no one wants
extreme segregation? Thomas Schelling's famous model (1971) places agents of two
types on a grid; each agent is happy as long as the *fraction of unlike
neighbours* stays below a personal tolerance, and an unhappy agent moves to a
random vacancy. The question this project answers: **how segregated does the city
become, and how does that compare to what the agents individually asked for?**

## Setup

Install sim_lab and use the agent-based interface:

```bash
pip install sim_lab
```

```python
from sim_lab.core import AgentBasedSimulation, Agent, Environment
```

Read the [Agent-Based Simulation docs](../../simulations/agent_based/agent_based.md)
first — `AgentBasedSimulation` builds agents from an `agent_factory` and gives each
agent, each step, the list of `neighbors` inside `neighborhood_radius`.

## Instructions

### 1. Define the board (an `Environment`) that tracks empty cells

The environment owns the list of vacant cells so unhappy agents have somewhere to
go. It recomputes vacancies from the agents' current positions every step.

```python
import numpy as np
from sim_lab.core import AgentBasedSimulation, Agent, Environment

GRID = 20          # 20x20 grid = 400 cells
N = 320            # 80% occupied, 80 vacancies
RADIUS = 1.5       # > sqrt(2) so each agent sees its 8 Moore neighbours

class SchellingBoard(Environment):
    def __init__(self, grid_size):
        super().__init__({"vacancies": []})
        self.grid_size = grid_size

    def update(self, agents):
        occupied = {(round(a.position[0]), round(a.position[1])) for a in agents}
        cells = [(r, c) for r in range(self.grid_size)
                        for c in range(self.grid_size)]
        self.state["vacancies"] = [cell for cell in cells if cell not in occupied]
```

### 2. Define a `SchellingAgent` that follows Schelling's rule

An agent is **unhappy** when more than a `tolerance` fraction of its neighbours
are of the other type. An unhappy agent claims a random vacancy (freeing its old
cell back into the shared vacancy list so later agents can use it).

```python
class SchellingAgent(Agent):
    def __init__(self, agent_id, position, agent_type, tolerance):
        super().__init__(agent_id, {"type": agent_type, "happy": True}, position)
        self.tolerance = tolerance

    def update(self, environment, neighbors):
        if not neighbors:                       # isolated agents are content
            self.state["happy"] = True
            return
        unlike = sum(1 for n in neighbors
                     if n.state["type"] != self.state["type"])
        self.state["happy"] = (unlike / len(neighbors)) <= self.tolerance
        if not self.state["happy"]:
            vacancies = environment.state["vacancies"]
            if vacancies:
                old = (round(self.position[0]), round(self.position[1]))
                new = vacancies.pop(int(np.random.randint(len(vacancies))))
                vacancies.append(old)           # free the old cell
                self.move(new)
```

### 3. Build the factory, run the simulation, measure segregation

Place agents on distinct random cells and split them into two equal types. The
factory uses its own seeded generator for the initial layout, and we pass
`random_seed=42` so the in-step moves are reproducible too.

```python
def run_schelling(tolerance, seed=42):
    rng = np.random.RandomState(seed)
    cells = [(r, c) for r in range(GRID) for c in range(GRID)]
    chosen = rng.choice(len(cells), size=N, replace=False)

    def agent_factory(i):
        r, c = cells[chosen[i]]
        return SchellingAgent(i, (r, c), i % 2, tolerance)

    board = SchellingBoard(GRID)
    sim = AgentBasedSimulation(
        agent_factory=agent_factory,
        num_agents=N,
        environment=board,
        days=60,
        neighborhood_radius=RADIUS,
        random_seed=seed,
    )
    board.update(sim.agents)            # seed the vacancy list before running
    sim.run_simulation()
    return sim

def segregation_index(sim):
    # fraction of all neighbour links that join same-type agents
    like, total = 0, 0
    for a in sim.agents:
        nb = sim.get_agent_neighbors(a)
        if nb:
            like += sum(1 for n in nb if n.state["type"] == a.state["type"])
            total += len(nb)
    return like / total if total else 0.0

sim = run_schelling(tolerance=0.3)
print("segregation index:", round(segregation_index(sim), 3))
```

### 4. Sweep the tolerance and plot the paradox

A random two-colour mix gives a baseline index of **≈ 0.5**. Sweep the tolerance
and watch how far above that baseline the city lands.

```python
import matplotlib.pyplot as plt

tolerances = [0.125, 0.2, 0.3, 0.4, 0.5, 0.625]
indices = [segregation_index(run_schelling(t)) for t in tolerances]

plt.plot(tolerances, indices, "o-", label="equilibrium segregation")
plt.axhline(0.5, ls="--", color="grey", label="random-mix baseline (0.5)")
plt.xlabel("tolerance (max fraction of unlike neighbours accepted)")
plt.ylabel("segregation index (same-type neighbour fraction)")
plt.legend()
plt.show()
```

## Validation target

With `random_seed=42`, `GRID=20`, `N=320`:

- At **tolerance 0.3** (agents are happy once no more than 30% of their neighbours
  are unlike) the equilibrium segregation index is **≈ 0.99** — almost perfectly
  segregated.
- At **tolerance 0.5** (agents would accept a perfectly mixed 50/50 block) it is
  still **≈ 0.88**.

Both sit far above the **0.5 random-mix baseline**, and far above the share of
same-type neighbours any single agent demanded. This is **Schelling's paradox**:
mild, local preferences amplify into near-total global segregation.

## Things to explore

- What happens at *very* low tolerance (0.125)? Why does the index drop and the
  fraction of happy agents collapse? (Hint: agents become impossible to satisfy.)
- Replace "move to a random vacancy" with "move to the nearest vacancy where I
  would be happy". Does segregation rise or fall?
- Add a third type and rebalance the counts. Does the paradox strengthen or weaken?
- Vary the occupancy (N = 280 vs 360). How does the number of vacancies change the
  speed of segregation?
- Plot the **fraction of happy agents** over time — does it monotonically rise?

## Extension ideas

- Add a small fraction of "stubborn" agents that never move. How robust is the
  segregation to a non-conforming minority?
- Make tolerance heterogeneous (each agent draws its own). Measure the inequality
  of the resulting pattern.
- Replace the `segregation_index` (a global average) with a local measure such as
  the mean over agents of each agent's own same-type-neighbour fraction, and
  compare the two.

## Assessment criteria

- **Reproducibility** — `random_seed=42` is set and a second run reproduces the
  segregation index to the printed precision.
- **Validation** — the report states the **0.5 random-mix baseline** and shows the
  equilibrium index is well above it (e.g. ≈ 0.88 at tolerance 0.5), correctly
  identifying this as **Schelling's paradox**.
- **Analysis** — the sweep plot is interpreted: students explain *why* the outcome
  is more segregated than the individual tolerance requires, and discuss the
  churning regime at extreme intolerance.
- **Code quality** — the agent, environment, factory, and index are cleanly
  separated; tolerance and grid size are parameters, not magic numbers; no
  abandoned vacancies (moved agents free their old cell).
