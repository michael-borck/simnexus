# Stochastic Predator-Prey

**Difficulty**: Advanced
**Time**: ~75 minutes
**Learning Focus**: demographic/environmental noise; ensembles; extinction risk at low population counts
**Simulator**: PredatorPreySimulation (registry `"PredatorPrey"`)

## Overview
The deterministic Lotka–Volterra model predicts perfectly repeatable cycles. Real ecosystems are noisy, and once you add randomness the orbits blur, drift, and — when populations are small — can hit zero and never recover. You will run an **ensemble** of stochastic trajectories around a deterministic baseline, show that the ensemble fluctuates around the deterministic trajectory, and demonstrate that the spread of outcomes *grows with the noise level* and can produce extinction at low counts.

## Setup
Install sim-lab (`pip install sim_lab`) and use a Jupyter notebook. The simulator has a built-in `stochastic=True` switch (Gaussian noise scaled to each population); for the noise-sweep you will reuse its `get_derivatives()` with a tunable noise term. See the [Predator-Prey doc page](../../simulations/ecological/predator_prey.md).

## Instructions

1. **Run the deterministic reference.** This is the noise-free trajectory the ensemble will hug.

```python
import numpy as np
import matplotlib.pyplot as plt
from sim_lab.core import PredatorPreySimulation

ALPHA, BETA, GAMMA, DELTA = 0.1, 0.002, 0.1, 0.001
X0, Y0 = 120, 40
DAYS, DT = 300, 0.01

det = PredatorPreySimulation(
    X0, Y0, ALPHA, BETA, GAMMA, DELTA, days=DAYS, dt=DT, random_seed=42,
)
det_res = det.run_simulation()
det_prey, det_pred = det_res["prey"], det_res["predators"]
```

2. **Build an ensemble with the built-in stochastic switch.** Each member gets a different `random_seed` so the Gaussian noise differs; together they form a cloud around the deterministic curve.

```python
N_ENS = 25
ens_prey, ens_pred = [], []
for s in range(N_ENS):
    stoch = PredatorPreySimulation(
        X0, Y0, ALPHA, BETA, GAMMA, DELTA,
        days=DAYS, dt=DT, stochastic=True, random_seed=s,
    )
    r = stoch.run_simulation()
    ens_prey.append(r["prey"]); ens_pred.append(r["predators"])

ens_prey = np.array(ens_prey); ens_pred = np.array(ens_pred)

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(det_prey, color="black", lw=2, label="Deterministic")
ax.plot(ens_prey.T, color="tab:blue", alpha=0.25)
ax.set_xlabel("Day"); ax.set_ylabel("Prey population")
ax.set_title("Stochastic ensemble around the deterministic trajectory"); ax.legend()
plt.show()
```

3. **Quantify the fluctuations.** Plot the ensemble mean ± 1 standard-deviation band and confirm it tracks the deterministic curve.

```python
days_axis = np.arange(len(det_prey))
mean_prey, std_prey = ens_prey.mean(axis=0), ens_prey.std(axis=0)

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(days_axis, det_prey, color="black", lw=2, label="Deterministic")
ax.plot(days_axis, mean_prey, color="tab:blue", label="Ensemble mean")
ax.fill_between(days_axis, mean_prey - std_prey, mean_prey + std_prey,
                color="tab:blue", alpha=0.25, label="±1 std dev")
ax.set_xlabel("Day"); ax.set_ylabel("Prey population"); ax.legend()
ax.set_title("Ensemble spread around the deterministic prey curve"); plt.show()
```

4. **Sweep the noise level to show variance grows with noise.** The built-in switch uses *environmental* noise (proportional to population). Small populations are instead threatened by **demographic** noise — the birth/death events whose variance scales as √population, so the *relative* fluctuation blows up as counts fall (and, crucially for step 6, can drive a population to zero). Reuse the simulator's ODEs through `get_derivatives()` with a tunable demographic `noise_scale`, and down-sample exactly like `run_simulation()` (one value per simulated day) so the curves align.

```python
def stochastic_pp(noise_scale, seed, x0=X0, y0=Y0):
    rng = np.random.default_rng(seed)
    engine = PredatorPreySimulation(x0, y0, ALPHA, BETA, GAMMA, DELTA, days=DAYS, dt=DT)
    n_steps = int(DAYS / DT)
    xs, ys = [x0], [y0]
    x, y = x0, y0
    for _ in range(1, n_steps):
        dx, dy = engine.get_derivatives(x, y)
        if x > 0:
            dx += rng.normal(0, noise_scale * np.sqrt(x))
        if y > 0:
            dy += rng.normal(0, noise_scale * np.sqrt(y))
        x = max(0.0, x + dx * DT)
        y = max(0.0, y + dy * DT)
        xs.append(x); ys.append(y)
    idx = np.linspace(0, len(xs) - 1, DAYS, dtype=int)
    return np.array(xs)[idx], np.array(ys)[idx]
```

5. **Measure how the final-state variance scales with noise.** For each noise level run a small ensemble and record the standard deviation of the final predator count.

```python
NOISE_LEVELS = [0.0, 0.3, 0.6, 1.0, 1.5]
M = 20
std_final_pred = []
for ns in NOISE_LEVELS:
    finals = [stochastic_pp(ns, seed)[1][-1] for seed in range(M)]
    std_final_pred.append(np.std(finals))

fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(NOISE_LEVELS, std_final_pred, "o-")
ax.set_xlabel("Noise scale"); ax.set_ylabel("Std dev of final predator count")
ax.set_title("Outcome variance grows with noise"); plt.show()
```

6. **Probe extinction risk at low counts.** With small starting populations and strong noise, individual runs can hit zero (the `max(0, …)` floor). Count how often each species goes extinct across the ensemble.

```python
M_EXT = 40
extinct_prey = extinct_pred = 0
for seed in range(M_EXT):
    xs, ys = stochastic_pp(3.0, seed, x0=15, y0=8)
    if (xs <= 0).any():
        extinct_prey += 1
    if (ys <= 0).any():
        extinct_pred += 1

print(f"prey extinct in {extinct_prey}/{M_EXT} runs, predators in {extinct_pred}/{M_EXT} runs")
```

## Things to explore
- Reduce the ensemble size `N_ENS` to 5. How rough does the mean ± std band look, and how many members are needed for it to settle?
- At the high-noise / low-count setting, plot the fraction of runs with an extinction *over time* (first day the population hits zero). Which species tends to vanish first, and why?
- Compare **demographic** noise (`noise_scale·√population`, used above) against **environmental** noise (`noise_scale·population`, as in the built-in `stochastic=True`). Which produces the larger *relative* swing when populations are small, and which drives more extinctions?
- Lower `DAYS/dt` resolution (larger `DT`). Does coarser integration inflate or damp the apparent variance?

## Extension ideas
- Replace Gaussian noise with a proper Gillespie-style **demographic stochasticity** (integer births/deaths drawn as Poisson events) and compare the extinction probability to the Gaussian approximation.
- Add logistic prey growth (`carrying_capacity`). Does a stable equilibrium reduce extinction risk compared with the neutrally-stable cycles?
- Compute the **mean exit time** from a band around the equilibrium as a function of noise scale — the classic stochastic-resonance / noise-induced-transition picture.

## Assessment criteria
- **Reproducibility** — the deterministic run uses `random_seed=42`; every ensemble member and sweep point uses a fixed seed, so all figures are repeatable.
- **Validation (fluctuations around deterministic)** — the ensemble mean ± std band is shown to track the deterministic trajectory rather than drifting away from it.
- **Validation (variance grows with noise)** — the final-state standard deviation increases monotonically with `noise_scale` across the sweep.
- **Validation (extinction at low counts)** — at low starting populations and high noise, a non-trivial fraction of ensemble runs are shown to hit zero.
- **Analysis** — the student distinguishes *demographic* noise (scales with √population) from a fixed-amplitude perturbation, and explains why low counts are extinction-prone.
- **Code quality** — the tunable-noise integrator reuses `get_derivatives()` rather than re-implementing the ODEs; ensembles are loops over seeds, not copy-pasted runs.
