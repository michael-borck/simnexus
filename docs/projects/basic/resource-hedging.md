# Hedging Resource Price Risk
**Difficulty**: Advanced
**Time**: ~75 minutes
**Learning Focus**: Monte Carlo over many paths, variance reduction via hedging
**Simulator**: ResourceFluctuationsSimulation (registry `ResourceFluctuations`)

## Overview
A firm that must buy a fixed quantity of a volatile resource every day faces an unpredictable total bill. A fixed-price hedge (a forward contract) locks in a price on part of that consumption, trading a potentially higher *expected* cost for a much smaller *spread* of outcomes. Using `ResourceFluctuationsSimulation` you run hundreds of seeded price paths, compute total procurement cost with and without a hedge covering a fraction of consumption, and validate the central hedging theorem: locking in a fraction `f` of exposure cuts the standard deviation of total cost by exactly `(1 − f)`.

## Setup
Install the toolkit (`pip install sim_lab`) and use the class interface: `from sim_lab.core import ResourceFluctuationsSimulation`. Read the [Resource Fluctuations doc](../../simulations/basic/resource_fluctuations.md) for the price rule.

## Instructions
1. **Define the firm.** The firm consumes a fixed `consumption` units each day and can lock in `hedge_frac` of that volume at a `fixed_price`; the rest is bought at the spot price. With `fixed_price` equal to the starting spot price and zero drift, the hedge is roughly fair (cost-neutral in expectation), so any difference is pure variance:
   ```python
   from sim_lab.core import ResourceFluctuationsSimulation
   import numpy as np

   consumption = 1000      # units bought every day
   hedge_frac = 0.5        # half locked at the fixed price
   fixed_price = 60        # = start_price, so the hedge is ~fair
   days = 120
   n_runs = 300
   ```

2. **Monte Carlo the costs.** For each seed, build a price path and record the total cost with and without the hedge:
   ```python
   unhedged, hedged = [], []
   for seed in range(n_runs):
       prices = ResourceFluctuationsSimulation(
           start_price=60, days=days, volatility=0.02, drift=0.0,
           random_seed=seed,
       ).run_simulation()
       cost_unhedged = sum(consumption * p for p in prices)
       cost_hedged = sum(
           consumption * hedge_frac * fixed_price
           + consumption * (1 - hedge_frac) * p
           for p in prices
       )
       unhedged.append(cost_unhedged)
       hedged.append(cost_hedged)
   ```

3. **Validate the variance reduction.** Hedging a fraction `f` of exposure removes exactly `f` of the price risk, so the standard deviation should fall by a factor of `(1 − f)`:
   ```python
   std_u, std_h = np.std(unhedged), np.std(hedged)
   print("std unhedged:", round(std_u))
   print("std hedged:  ", round(std_h))
   print("ratio:        %.3f   (expected %.3f)" % (std_h / std_u, 1 - hedge_frac))
   ```

4. **Compare the distributions.** Plot overlaid histograms of `unhedged` and `hedged` total cost, and report both means and both standard deviations.

5. **Sweep the hedge fraction.** Repeat for `hedge_frac` in `{0.0, 0.25, 0.5, 0.75, 1.0}` and plot cost standard deviation against `hedge_frac`. Confirm it traces the line `std_h = (1 − hedge_frac) · std_u`.

## Things to explore
- What happens to the *mean* cost when `fixed_price` is set above or below the starting spot price? Interpret the hedge as insurance: you pay a premium (higher mean) to lower the variance.
- Recompute everything with a positive `drift` (a rising-price market). Does the variance-reduction factor `(1 − f)` still hold? Does the *desirability* of the hedge change?
- How many runs (`n_runs`) do you need before the measured ratio `std_h / std_u` settles within 1% of `1 − f`? This is Monte Carlo error in action.
- Add a supply disruption (`supply_disruption_day`, `disruption_severity`) to every path. How well does the hedge protect against a tail event?

## Extension ideas
- Make the hedge *cost* money up front (a fixed option premium) and find the hedge fraction that minimises CVaR (conditional value at risk) of total cost rather than just standard deviation.
- Introduce *basis risk*: the hedge locks a price that tracks the spot only imperfectly (e.g. `0.9 × spot + noise`). How much variance reduction survives imperfect correlation?
- Compare this forward hedge against an alternative (e.g. buying a fixed fraction *one day in advance* each day) on the same set of seeded paths.

## Assessment criteria
- **Reproducibility** — every path uses an explicit `random_seed` (one per run); re-running reproduces identical cost distributions.
- **Validation** — the standard-deviation ratio `std_hedged / std_unhedged ≈ 1 − hedge_frac` is stated as the target and shown to hold (≈ 0.50 for `hedge_frac = 0.5`); means are reported too.
- **Analysis** — the student explains the variance–mean trade-off (why the hedge cuts spread, and when it raises expected cost), and discusses convergence as `n_runs` grows.
- **Code quality** — the Monte Carlo is a clean parameterised loop; `consumption`, `hedge_frac`, `fixed_price`, and `n_runs` are named constants, not magic numbers.
