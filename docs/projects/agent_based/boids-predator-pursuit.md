# Predator Pursuit

**Difficulty**: Advanced
**Time**: ~80 minutes
**Learning Focus**: extending an agent-based model with a new agent type, predator–prey evasion
**Simulator**: BoidsSimulation (registry `"Boids"`) — subclassed with custom agents

## Overview

A real flock does not just move — it **reacts**. When a hawk approaches, the flock
compresses, splits, and bolts away from the threat. This project adds a
**predator** agent that homes on the flock's centroid while the prey (ordinary
boids) gain a fourth rule: **flee any predator among your neighbours**. The
question: **does the flock's evasive response keep the predator farther from its
centroid than a flock that ignores the threat?**

## Setup

Install sim_lab. You will subclass `BoidsSimulation` and reuse the real `Boid`
class, so import both plus the base `Agent`:

```bash
pip install sim_lab
```

```python
from sim_lab.core import BoidsSimulation, Boid, Agent
```

Read the [Boids docs](../../simulations/agent_based/boids.md) and the
[Agent-Based docs](../../simulations/agent_based/agent_based.md) first. The plan:
override three pieces of `BoidsSimulation` — `_make_boid` (build fleeing prey
instead of plain boids), `reset` (also spawn one predator), and
`calculate_metrics` (report the centroid-to-predator distance and stash the
centroid where the predator can read it).

## Instructions

### 1. Define a `FleeingBoid` — Reynolds rules plus an escape force

Subclass `Boid` so you can reuse its real steering helpers
(`_separation`, `_alignment`, `_cohesion`, `_steer_to`, `_limit`). Add a flee
force that points away from every predator among the neighbours, weighted more
strongly the closer the predator is. Predators are recognised by their state
`type == "predator"`.

```python
import numpy as np
from sim_lab.core import BoidsSimulation, Boid, Agent

class FleeingBoid(Boid):
    flee_strength = 2.0      # class attribute so the control run can set it to 0

    def update(self, environment, neighbors):
        preds = [n for n in neighbors if n.state.get("type") == "predator"]
        flock = [n for n in neighbors if n.state.get("type") != "predator"]

        # normal Reynolds steering over the (predator-free) flock
        steer = (self.w_sep * self._separation(flock)
                 + self.w_ali * self._alignment(flock)
                 + self.w_coh * self._cohesion(flock))

        if preds:
            flee = np.zeros(2)
            for p in preds:
                dx = self.position[0] - p.position[0]
                dy = self.position[1] - p.position[1]
                dist = max(0.1, (dx * dx + dy * dy) ** 0.5)
                flee += np.array([dx, dy]) / dist      # unit vector, away
            steer = steer + self.flee_strength * flee

        steer = self._limit(steer, self.max_force)
        self.velocity = self._limit(self.velocity + steer, self.max_speed)
        nx = (self.position[0] + self.velocity[0]) % self.width
        ny = (self.position[1] + self.velocity[1]) % self.height
        self.move((nx, ny))
        self.state = {"speed": self.speed, "type": "prey"}
```

### 2. Define the `PredatorBoid` — steer straight at the flock centroid

The predator ignores the Reynolds rules. Each step it reads the flock centroid
(stashed in the environment by `calculate_metrics`) and heads toward it at a
fixed speed. It carries a `velocity` and `position` so that, if a prey ever treats
it as a neighbour, the duck-typing does not break.

```python
class PredatorBoid(Agent):
    def __init__(self, agent_id, position, width, height, speed):
        super().__init__(agent_id, {"type": "predator"}, position)
        self.velocity = np.array([speed, 0.0])
        self.width = width
        self.height = height
        self.pspeed = speed

    def update(self, environment, neighbors):
        centroid = environment.state.get("centroid")
        if centroid is None:
            return
        toward = np.array(centroid) - np.array(self.position)
        dist = np.linalg.norm(toward)
        if dist > 1e-6:
            self.velocity = toward / dist * self.pspeed
        nx = (self.position[0] + self.velocity[0]) % self.width
        ny = (self.position[1] + self.velocity[1]) % self.height
        self.move((nx, ny))
        self.state = {"type": "predator"}
```

### 3. Subclass `BoidsSimulation` to host both agent types

Override `_make_boid` to return fleeing prey, `reset` to append a predator after
the parent rebuilds the flock, and `calculate_metrics` to (a) compute the prey
centroid, (b) stash it into `self.environment.state` for the predator, and
(c) return the centroid-to-predator distance.

```python
class PredatorBoidsSimulation(BoidsSimulation):
    predator_speed = 3.2     # slightly faster than the prey (max_speed = 3.0)

    def _make_boid(self, agent_id):
        position = (self._rng.uniform(0, self.width), self._rng.uniform(0, self.height))
        velocity = self._rng.uniform(-1, 1, size=2)
        norm = np.linalg.norm(velocity)
        velocity = velocity / norm * self.max_speed if norm > 1e-6 else np.array([self.max_speed, 0.0])
        return FleeingBoid(
            agent_id, position, velocity,
            self.width, self.height, self.max_speed, self.max_force,
            self._w_sep, self._w_ali, self._w_coh,
        )

    def reset(self):
        super().reset()      # reseeds the RNG and rebuilds the fleeing prey
        self.agents.append(PredatorBoid(
            self._num_boids, (5.0, 5.0), self.width, self.height, self.predator_speed))

    def calculate_metrics(self):
        prey = [a for a in self.agents if a.state.get("type") != "predator"]
        positions = np.array([a.position for a in prey])
        centroid = positions.mean(axis=0)
        # stash the centroid so the predator can read it next step
        self.environment.state["centroid"] = (float(centroid[0]), float(centroid[1]))
        predator = next(a for a in self.agents if a.state.get("type") == "predator")
        distance = float(np.linalg.norm(np.array(predator.position) - centroid))
        return {
            "num_prey": len(prey),
            "centroid_x": float(centroid[0]),
            "centroid_y": float(centroid[1]),
            "predator_x": predator.position[0],
            "predator_y": predator.position[1],
            "centroid_predator_distance": distance,
        }
```

### 4. Run with fleeing vs. without, and compare

Use a **large `perception_radius`** (≈ global coupling on the 100×100 field) so the
flock behaves as one coherent unit — that is what lets a predator's approach
shove the *whole* flock, and therefore its centroid, away. Run once with
`flee_strength = 2.0` and once with `0.0` (a control flock that ignores the
predator) and compare the steady-state centroid-to-predator distance.

```python
import matplotlib.pyplot as plt

def run(flee_strength, seed=42):
    FleeingBoid.flee_strength = flee_strength
    sim = PredatorBoidsSimulation(
        num_boids=50,
        width=100.0, height=100.0,
        max_speed=3.0, max_force=0.3,
        perception_radius=45.0,          # near-global coupling -> coherent flock
        weight_separation=0.8, weight_alignment=2.0, weight_cohesion=2.5,
        days=140, random_seed=seed,
    )
    return [m["centroid_predator_distance"] for m in sim.run_simulation()]

fleeing = run(2.0)
control = run(0.0)

print("mean distance  WITH flee =", round(np.mean(fleeing[40:]), 2))
print("mean distance  NO  flee =", round(np.mean(control[40:]), 2))

plt.plot(fleeing, label="prey flee")
plt.plot(control, label="prey ignore predator")
plt.xlabel("step"); plt.ylabel("centroid-to-predator distance")
plt.legend(); plt.show()
```

## Validation target

With `random_seed=42`, `num_boids=50`, `perception_radius=45`, and a predator
slightly faster than the prey (`predator_speed = 3.2` vs `max_speed = 3.0`):

- The **mean** centroid-to-predator distance over the steady state is roughly
  **twice as large when the prey flee** (≈ 17) as in the no-flee control (≈ 9).
- On the time series, the distance **rebounds upward after each close approach**:
  the predator closes in, the local prey bolt, and the coherent flock carries its
  centroid away. In the control run the predator tracks the centroid far more
  tightly.

This is the evasive signature: even against a faster, centroid-homing predator,
coordinated fleeing keeps the flock's centre at greater distance.

## Things to explore

- Drop `perception_radius` back to 15. Why does the mean-distance contrast shrink?
  (Hint: with only *local* vision, fleeing spreads the flock symmetrically instead
  of translating it.)
- Make the predator much faster (4.5). At what speed can it overcome the evasion
  and sit on the centroid?
- Replace "steer toward the centroid" with "steer toward the **nearest prey**".
  How does the distance time series change?
- Add a second predator starting from the opposite corner. Does the flock compress
  (lower spread) or split?
- Vary `weight_cohesion`: does a tighter flock evade better, or does it become an
  easier target?

## Extension ideas

- Detect and count **evasive events**: steps where the distance first drops below
  a threshold and then rises by more than a set amount within a window. Plot the
  distribution of rebound sizes for fleeing vs. control.
- Give the predator **limited stamina** (it slows after sustained pursuit) and
  observe chase–escape cycles.
- Log each prey's distance to the predator and build a heatmap of the flock's
  deformation as the predator passes through.

## Assessment criteria

- **Reproducibility** — `random_seed=42` is set; the fleeing and control runs both
  reproduce their mean distances to the quoted precision.
- **Validation** — the report shows the mean centroid-to-predator distance is
  **larger when prey flee than in the no-flee control**, and explains *why* (the
  flee force must act on a coherent, near-globally-coupled flock to translate the
  centroid rather than merely spread it).
- **Analysis** — the distance time series is interpreted: students identify the
  close-approach → rebound pattern as the evasive response, and discuss the
  perception-radius and predator-speed regimes that strengthen or erase it.
- **Code quality** — the prey, predator, and simulator subclass are cleanly
  separated; the predator reads the centroid via the environment (not a global);
  `flee_strength`, `predator_speed`, and the perception radius are parameters, not
  magic numbers; the control is produced by flipping one parameter, not by
  rewriting the model.
