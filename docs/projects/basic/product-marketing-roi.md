# Marketing Campaign ROI
**Difficulty**: Intermediate
**Time**: ~45 minutes
**Learning Focus**: intervention comparison, return-on-investment accounting
**Simulator**: ProductPopularitySimulation (registry `ProductPopularity`)

## Overview
A marketing campaign costs money up front; the question is whether the extra demand it generates is worth more than the campaign cost. Using `ProductPopularitySimulation` you run the product twice — once with a one-day campaign (`promotion_day`, `promotion_effectiveness`) and once without — and turn the extra cumulative demand into a return on investment (ROI) given a stated value per unit of demand and a stated campaign cost. Both checks are exact: the campaign always lifts cumulative demand, and ROI is positive precisely when that lift, valued, exceeds the cost.

## Setup
Install the toolkit (`pip install sim_lab`) and use the class interface: `from sim_lab.core import ProductPopularitySimulation`. Read the [Product Popularity doc](../../simulations/basic/product_popularity.md) for the demand rule.

## Instructions
1. **Run the baseline (no campaign).** 60 days, modest natural growth plus steady marketing, `random_seed=42`:
   ```python
   from sim_lab.core import ProductPopularitySimulation

   base = ProductPopularitySimulation(
       start_demand=1000, days=60, growth_rate=0.01, marketing_impact=0.02,
       random_seed=42,
   ).run_simulation()
   ```

2. **Run the same product with a campaign.** Same parameters, but add a promotion on day 20 with effectiveness 0.30 (a 30% one-day boost that then keeps compounding):
   ```python
   promo = ProductPopularitySimulation(
       start_demand=1000, days=60, growth_rate=0.01, marketing_impact=0.02,
       promotion_day=20, promotion_effectiveness=0.3, random_seed=42,
   ).run_simulation()
   ```

3. **Validate that the campaign lifted demand.** Because the promotion multiplies that single day's demand (and everything after) by `(1 + promotion_effectiveness)`, cumulative demand must be higher with the campaign:
   ```python
   cum_base, cum_promo = sum(base), sum(promo)
   uplift = cum_promo - cum_base
   print(cum_base, cum_promo, uplift)      # uplift must be > 0
   ```

4. **Compute ROI.** Assume each unit of demand is worth `value_per_unit` in margin and the campaign costs `cost`. ROI = (benefit − cost) / cost:
   ```python
   value_per_unit = 0.50
   cost = 8000
   benefit = value_per_unit * uplift
   roi = (benefit - cost) / cost
   print("ROI: %.1f%%" % (roi * 100))     # positive under these assumptions
   ```

5. **Find the break-even.** The break-even campaign cost is exactly `value_per_unit × uplift`. Report it, and recompute ROI for a range of costs (or `value_per_unit`) to show where ROI crosses zero.

## Things to explore
- Move `promotion_day` earlier or later (10, 20, 40). How does the timing of the boost change the total uplift, given that the boost compounds forward? Explain.
- Increase `promotion_effectiveness` from 0.1 to 0.5. Does ROI scale linearly with effectiveness? Why or why not?
- Sensitivity: at what `value_per_unit` does ROI turn negative for the stated `cost`? What is the most you could justify paying for this campaign?
- The model has no randomness, so both runs are deterministic. What extra step would you add to estimate ROI under *uncertain* market conditions?

## Extension ideas
- Compare several candidate campaigns (different `promotion_day`/`promotion_effectiveness` pairs and assumed costs) and rank them by ROI to pick the best spend.
- Add a second promotion day (run a hand-modified path) and test whether two smaller boosts beat one large one of the same total effectiveness.
- Introduce a per-unit *production cost* so that not all extra demand is margin; recompute ROI and discuss how cost structure changes the campaign decision.

## Assessment criteria
- **Reproducibility** — `random_seed=42` set and stated; the two runs are otherwise identical so the result is exactly reproducible.
- **Validation** — cumulative demand is shown to be higher *with* the campaign (`uplift > 0`), and ROI is reported as a number that is positive under the stated `value_per_unit`/`cost` assumptions (and the break-even cost `value_per_unit × uplift` is identified).
- **Analysis** — the student explains why the one-day boost compounds into a large cumulative uplift, and discusses the sensitivity of the ROI verdict to the assumed value and cost.
- **Code quality** — ROI is a clean formula with named `value_per_unit` and `cost` constants; the with/without runs share all parameters except the promotion.
