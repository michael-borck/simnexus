# Viral Product Launch
**Difficulty**: Beginner
**Time**: ~25 minutes
**Learning Focus**: compounding growth, critical thresholds
**Simulator**: ProductPopularitySimulation (registry `ProductPopularity`)

## Overview
Will a new product take off or fizzle? In `ProductPopularitySimulation` demand compounds daily at an effective rate set by `growth_rate` (word-of-mouth virality) plus `marketing_impact` (paid marketing). The product "goes viral" only when that combined rate is positive; at or below zero, demand stalls or decays. Your job is to scan the two knobs, pin down the exact takeoff threshold, and explain why the curve looks the way it does above and below it.

## Setup
Install the toolkit (`pip install sim_lab`) and use the class interface: `from sim_lab.core import ProductPopularitySimulation`. Read the [Product Popularity doc](../../simulations/basic/product_popularity.md) for the demand rule.

## Instructions
1. **Run one launch.** Start at 500 units of demand and give the product a modest combined boost, `random_seed=42`:
   ```python
   from sim_lab.core import ProductPopularitySimulation

   sim = ProductPopularitySimulation(
       start_demand=500, days=120, growth_rate=0.02, marketing_impact=0.01,
       random_seed=42,
   )
   demand = sim.run_simulation()
   ```

2. **Find the growth factor.** Each day demand is multiplied by `1 + growth_rate + marketing_impact`. Verify the effective daily factor and the resulting end demand:
   ```python
   factor = 1 + sim.growth_rate + sim.marketing_impact
   print(factor, demand[-1], 500 * factor ** 119)   # last two should match
   ```

3. **Scan across the threshold.** Vary the combined rate `growth_rate + marketing_impact` from −0.05 to +0.05 and record the end-of-horizon demand. Watch for the sharp kink at zero:
   ```python
   for s in [-0.05, -0.03, -0.01, 0.0, 0.01, 0.03, 0.05]:
       d = ProductPopularitySimulation(
           start_demand=500, days=120, growth_rate=s, marketing_impact=0.0,
           random_seed=42,
       ).run_simulation()
       print("combined %+.2f -> end %.0f" % (s, d[-1]))
   ```

4. **Locate the threshold.** Confirm the takeoff threshold is exactly `growth_rate + marketing_impact = 0`: demand grows (end > start) above it and shrinks (end < start) below it.

5. **Plot above vs below.** On one set of axes, plot demand for a clearly above-threshold case (e.g. combined +0.03) and a clearly below-threshold case (combined −0.03). Use a logarithmic y-axis and explain the shape.

## Things to explore
- On a log-y plot the above-threshold curve is a straight line — the signature of exponential growth. Confirm its slope equals `log(1 + growth_rate + marketing_impact)`.
- The model has **no carrying capacity**, so above-threshold demand grows without bound — this is exponential, not a true logistic S-curve with an upper plateau. Where would a saturating S-curve come from, and what parameter would you add?
- Swap the mix: reach the same combined rate once with all virality (`growth_rate=0.03, marketing_impact=0`) and once with all marketing (`growth_rate=0, marketing_impact=0.03`). Is the demand path identical? Why?
- Push `days` to 365 for a just-above-threshold case (combined +0.005). How dramatic is the long-run difference between +0.005 and −0.005?

## Extension ideas
- Add a carrying capacity by capping demand at a market size `M` (a logistic update) and show how the curve bends into a genuine S-shape above the threshold.
- Introduce a one-time `promotion_day`/`promotion_effectiveness` launch event and find whether a strong launch can push an otherwise below-threshold product *past* the threshold permanently.
- Compare two products with the same combined rate but one with noise added to the daily factor — does the threshold still sit exactly at zero?

## Assessment criteria
- **Reproducibility** — `random_seed=42` set and stated; re-running reproduces identical demand curves.
- **Validation** — the takeoff threshold `growth_rate + marketing_impact = 0` is stated as the target and confirmed by the scan (end-demand kinks at zero); the daily factor `1 + growth_rate + marketing_impact` is verified against the simulated path.
- **Analysis** — the student correctly describes the above-threshold path as exponential growth (straight line on a log plot), and honestly notes the model has no carrying capacity (so it is not a true saturating S-curve).
- **Code quality** — the threshold scan is a clean loop with no magic numbers; the log-plot and factor check are clearly labelled.
