# Supply Disruption Scenarios
**Difficulty**: Beginner
**Time**: ~25 minutes
**Learning Focus**: exogenous price shocks, reading a price path
**Simulator**: ResourceFluctuationsSimulation (registry `ResourceFluctuations`)

## Overview
A factory that depends on a single commodity is exposed to supply shocks — a strike, a pipeline failure, a poor harvest — that briefly spike the input price before normal trading resumes. Using `ResourceFluctuationsSimulation` you fire a supply disruption on a chosen day, verify the exact size of the spike, and study how the price behaves afterwards. Because the disruption-day price is exact, you can isolate the *shock* from the random *aftermath*.

## Setup
Install the toolkit (`pip install sim_lab`) and use the class interface: `from sim_lab.core import ResourceFluctuationsSimulation`. Read the [Resource Fluctuations doc](../../simulations/basic/resource_fluctuations.md) for the price rule.

## Instructions
1. **Run a disrupted scenario.** A $50 resource, 200 days, with a +25% supply shock on day 80, `random_seed=42`:
   ```python
   from sim_lab.core import ResourceFluctuationsSimulation

   sim = ResourceFluctuationsSimulation(
       start_price=50, days=200, volatility=0.01, drift=0.0002,
       supply_disruption_day=80, disruption_severity=0.25, random_seed=42,
   )
   prices = sim.run_simulation()
   ```

2. **Validate the spike.** On the disruption day the random step is *replaced* by the shock, so the price must rise by exactly `(1 + disruption_severity)`:
   ```python
   ratio = prices[80] / prices[79]
   print(ratio, 1 + sim.disruption_severity)   # 1.25  1.25
   ```

3. **Check that the shock is permanent (no mean reversion).** Drop the noise to see the shift cleanly: run a disrupted and a baseline path with `volatility=0` (same seed, same drift). The post-shock ratio is then a flat constant, `(1 + disruption_severity) / (1 + drift)` — the price level is lifted for good, never pulled back down:
   ```python
   base = ResourceFluctuationsSimulation(
       start_price=50, days=200, volatility=0.0, drift=0.0002, random_seed=42,
   ).run_simulation()
   disr = ResourceFluctuationsSimulation(
       start_price=50, days=200, volatility=0.0, drift=0.0002,
       supply_disruption_day=80, disruption_severity=0.25, random_seed=42,
   ).run_simulation()
   print([round(disr[d] / base[d], 5) for d in (80, 120, 199)])  # 1.24975 ... flat
   ```

4. **Quantify the shock on the noisy path.** Back in the realistic `prices` from step 1, report the pre-shock price (`prices[79]`), the spike price (`prices[80]`), and the end-of-horizon price. Overlay a same-seed noisy baseline to see that the disrupted path stays *above* it (the shift persists; only the noise varies). Mark the disruption day with a vertical line.

5. **Vary the shock.** Re-run with `disruption_severity` in `{0.10, 0.25, 0.50}` and `supply_disruption_day` in `{40, 80, 120}`, and note how the spike size and its persistence change.

## Things to explore
- In the `volatility=0` run from step 3, the post-shock ratio is the flat constant `(1 + disruption_severity) / (1 + drift)`. Re-add noise and the ratio wobbles around that constant but never decays back to 1 — why?
- This model is a geometric random walk with **no mean reversion**, so a supply shock is a permanent level shift, not a spike that fades. Where would you *expect* a real commodity market to mean-revert, and what would that path look like instead?
- What if the disruption is *negative* (`disruption_severity = -0.25`, a supply glut)? Does the mirror-image level shift hold?
- Move the disruption earlier vs later in the horizon. How does the *cumulative* price paid (the sum over all days) change with timing?

## Extension ideas
- Model an inventory buffer: the firm draws from stock for the first `k` days after the shock and only buys at the spiked price once stock is empty. How much does a `k`-day buffer save?
- Chain two disruptions on different days and check that the second shock multiplies the already-shifted level (compound shocks).
- Add a hand-written mean-reverting price model (Ornstein–Uhlenbeck style) and compare how a shock *decays* there versus the permanent shift in this simulator.

## Assessment criteria
- **Reproducibility** — `random_seed=42` set and stated; re-running reproduces identical prices and spike.
- **Validation** — the disruption-day check `prices[80] == prices[79] * (1 + disruption_severity)` is shown and passes (≈ 1.25); the permanent-shift check (`disr[d] / base[d]` is a flat `(1 + severity) / (1 + drift)` in the `volatility=0` run) is demonstrated, and the student correctly notes this model does **not** mean-revert.
- **Analysis** — spike size and persistence are reported across severities and timings, with a correct explanation of why the shift is permanent in this simulator.
- **Code quality** — the baseline comparison is looped/parameterised; the spike and ratio checks are clean and labelled.
