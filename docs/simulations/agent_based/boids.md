# Boids Flocking Simulation

## Purpose

This simulation models the flocking behaviour of birds (or fish, or sheep) using Craig Reynolds' classic *boids* model from 1987. Each "boid" is an autonomous agent that follows only three local steering rules — separation, alignment, and cohesion — with no leader and no global plan. It is a cornerstone teaching example of **emergence**: complex, lifelike group motion arises from a handful of simple rules operating on local information, making it ideal for introducing agent-based modelling, decentralised control, and self-organisation.

## Parameters

- `num_boids`: Number of boids (agents) in the flock.
- `width`: Width of the 2-D field the flock lives on.
- `height`: Height of the 2-D field the flock lives on.
- `max_speed`: Speed cap; a boid's velocity magnitude can never exceed this value.
- `max_force`: Per-step cap on the steering acceleration a boid can apply, which limits how sharply it can turn.
- `perception_radius`: Radius within which a boid can sense and react to its neighbours.
- `weight_separation`: Relative weight of the separation rule (avoid crowding).
- `weight_alignment`: Relative weight of the alignment rule (match neighbour heading).
- `weight_cohesion`: Relative weight of the cohesion rule (steer toward neighbour centre).
- `days`: Number of simulation steps to run.
- `save_history`: Whether to record per-agent state history each step (useful for animation/tracing, costs memory).
- `random_seed`: Optional seed for reproducible initial positions and headings.

## Example Code

```python
from sim_lab.core import BoidsSimulation
import matplotlib.pyplot as plt

# Example scenario: a medium flock on a 100x100 toroidal field,
# tuned so cohesion dominates and a tight flock emerges.
sim = BoidsSimulation(
    num_boids=80,
    width=100.0,
    height=100.0,
    max_speed=3.0,
    max_force=0.05,
    perception_radius=10.0,
    weight_separation=1.5,
    weight_alignment=1.0,
    weight_cohesion=1.0,
    days=150,
    random_seed=42,
)

metrics = sim.run_simulation()

# Mean speed over time -- watch it settle as the flock synchronises.
steps = range(len(metrics))
mean_speeds = [m["mean_speed"] for m in metrics]
spread = [m["flock_spread"] for m in metrics]

fig, axes = plt.subplots(1, 3, figsize=(15, 4))

axes[0].plot(steps, mean_speeds, label="Mean speed")
axes[0].set_xlabel("Step")
axes[0].set_ylabel("Speed")
axes[0].set_title("Flock Mean Speed")
axes[0].legend()

axes[1].plot(steps, spread, color="tab:orange", label="Flock spread")
axes[1].set_xlabel("Step")
axes[1].set_ylabel("Spread (mean positional std)")
axes[1].set_title("Flock Spread")
axes[1].legend()

# Final positions of every boid.
xs = [a.position[0] for a in sim.agents]
ys = [a.position[1] for a in sim.agents]
axes[2].scatter(xs, ys, s=10)
axes[2].set_xlim(0, sim.width)
axes[2].set_ylim(0, sim.height)
axes[2].set_aspect("equal")
axes[2].set_title("Final Boid Positions")

plt.tight_layout()
plt.show()
```

## Use Case Ideas

### Investigate How the Rule Weights Shape Flock Structure

Tune `weight_separation`, `weight_alignment`, and `weight_cohesion` against one another and observe the group's macroscopic behaviour. Questions to Consider:

- What happens to the flock when separation dominates the other two rules?
- Can you find a weight combination where the flock splits into several independent sub-flocks?
- Which single rule is most responsible for the flock moving in a common direction?

### Investigate the Effect of Perception Radius

Change `perception_radius` while holding the population density fixed and watch the coupling between agents grow or shrink. Questions to Consider:

- How small can the radius get before the flock effectively dissolves into independent individuals?
- Does a very large radius produce "globally coupled" behaviour that looks unnatural?
- How does the radius interact with field size at constant `num_boids` (i.e. with density)?

### Investigate Emergence and Self-Organisation

Start from a random, disordered configuration and let the simulation run, tracking `flock_spread` and `mean_speed` over time. Questions to Consider:

- How many steps does it take for the mean speed to settle to a steady value?
- Is there a clear phase transition between "disordered" and "ordered" flocking as you vary `max_force`?
- If you re-run with a different `random_seed`, do the qualitative dynamics stay the same even though the exact trajectories differ?

## Model Description

`BoidsSimulation` is a subclass of `AgentBasedSimulation`. The field is **toroidal**: when a boid's position is updated it is wrapped with the modulo operator, so a boid flying off the right edge re-enters from the left:

$$x_{t+1} = (x_t + v_x) \bmod \text{width}, \qquad y_{t+1} = (y_t + v_y) \bmod \text{height}.$$

Each boid carries a position $\mathbf{p}=(x,y)$ and a velocity $\mathbf{v}=(v_x,v_y)$ whose magnitude is capped by `max_speed`. At every step the boid considers only the neighbours inside its `perception_radius` and computes three steering forces (the Reynolds rules):

1. **Separation** — steer away from close neighbours, weighted by inverse square distance so nearer neighbours push harder:
$$\mathbf{s}_{\text{sep}} = \frac{1}{n}\sum_{i} \frac{\mathbf{p}-\mathbf{p}_i}{\lVert \mathbf{p}-\mathbf{p}_i\rVert^{2}}.$$

2. **Alignment** — steer toward the neighbours' average heading:
$$\mathbf{s}_{\text{ali}} = \frac{1}{n}\sum_{i} \mathbf{v}_i.$$

3. **Cohesion** — steer toward the neighbours' average position:
$$\mathbf{s}_{\text{coh}} = \frac{1}{n}\sum_{i} \mathbf{p}_i - \mathbf{p}.$$

Each raw rule direction is converted into a bounded steering force by the shared `_steer_to` helper: the direction is scaled up to `max_speed` to form a *desired* velocity, and the difference from the current velocity is clamped to `max_force`:

$$\mathbf{f}_{\text{rule}} = \mathrm{clamp}_{\text{max\_force}}\!\left( \hat{\mathbf{d}} \cdot \text{max\_speed} - \mathbf{v} \right).$$

The three forces are linearly combined with the rule weights and clamped once more to `max_force`, then integrated:

$$\mathbf{v}_{t+1} = \mathrm{clamp}_{\text{max\_speed}}\!\left( \mathbf{v}_t + \mathrm{clamp}_{\text{max\_force}}\!\left( w_{\text{sep}}\mathbf{f}_{\text{sep}} + w_{\text{ali}}\mathbf{f}_{\text{ali}} + w_{\text{coh}}\mathbf{f}_{\text{coh}} \right) \right).$$

The two clamps are what give boids their characteristic smooth, lazy turns: `max_force` limits turning rate, while `max_speed` limits how fast they travel.

**Emergence.** Nothing in the rules refers to "a flock". Each boid reacts only to its immediate neighbours using local arithmetic, and no agent has a global view or a leadership role. Nevertheless, after a transient period the population self-organises into coherent, parallel-moving groups that turn and regroup as a unit — exactly the behaviour Reynolds observed in real bird flocks. This gap between the simplicity of the rules and the richness of the group behaviour is the central lesson of the model: global order can be an *emergent property* of local interactions, with no central coordinator required.

`run_simulation()` returns one metrics dictionary per step (including the initial state). Each dictionary reports `num_boids`, `mean_speed`, `max_speed_observed`, the flock centroid (`centroid_x`, `centroid_y`), and `flock_spread` (the mean positional standard deviation across boids, which falls as the flock gathers and rises as it scatters).
