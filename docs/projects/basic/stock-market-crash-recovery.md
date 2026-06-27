# Market Crash and Recovery
**Difficulty**: Intermediate
**Time**: ~50 minutes
**Learning Focus**: stochastic price paths, event shocks vs trend recovery
**Simulator**: StockMarketSimulation (registry `StockMarket`)

## Overview
A sudden market crash — an earnings miss, a macro shock — slices a chunk off a stock's price in a single day, after which the price drifts and jitters back (or doesn't). Using `StockMarketSimulation` you inject a large negative `event_impact` on a chosen `event_day`, then quantify how many days the price needs to claw back to its pre-crash level, and how that recovery time depends on the underlying `drift` and `volatility`. The crash itself is deterministic, which lets you cleanly separate the *event* from the random *aftermath*.

## Setup
Install the toolkit (`pip install sim_lab`) and use the class interface: `from sim_lab.core import StockMarketSimulation`. Read the [Stock Market doc](../../simulations/basic/stock_market.md) for the price rule.

## Instructions
1. **Simulate one crash.** Create a 252-day path for a $100 stock with a 20% crash on day 100, a small positive drift, and `random_seed=42`:
   ```python
   from sim_lab.core import StockMarketSimulation

   sim = StockMarketSimulation(
       start_price=100, days=252, volatility=0.01, drift=0.001,
       event_day=100, event_impact=-0.20, random_seed=42,
   )
   prices = sim.run_simulation()
   ```

2. **Validate the crash.** On the event day the random step is *replaced* by the event, so the price must drop by exactly `(1 + event_impact)`. Check it:
   ```python
   ratio = prices[100] / prices[99]
   print(ratio, 1 + sim.event_impact)   # 0.8  0.8
   ```

3. **Define recovery.** Recovery day = the first index after 100 whose price is back at or above the pre-crash level `prices[99]`. Find it:
   ```python
   pre_crash = prices[99]
   recovery = next((d for d in range(101, len(prices)) if prices[d] >= pre_crash), None)
   print("days to recover:", None if recovery is None else recovery - 100)
   ```

4. **Sweep drift.** Recovery is driven mainly by drift. Re-run with `drift` in `{0.0005, 0.001, 0.002}` (same seed) and record days-to-recover for each.

5. **Sweep volatility and seed.** Re-run with `volatility` in `{0.005, 0.01, 0.02}`, and for one setting try seeds 42–46 to see the *spread* of recovery times. Plot the paths with a horizontal line at the pre-crash level.

## Things to explore
- How does recovery time change as the crash gets deeper (`event_impact` from −0.10 to −0.40)? Does recovery time scale roughly linearly with crash size for a fixed drift?
- Plot recovery time (y) against drift (x). Is there a drift below which recovery *never* happens within the horizon? Why?
- For a fixed drift and crash, run 50 seeds and histogram the recovery times. What does the spread tell you about the reliability of an "expected" recovery time?
- What happens to recovery time if you add a *second* negative event partway through the recovery?

## Extension ideas
- Add an opportunity-cost framing: while below the pre-crash level, capital is "trapped" — estimate the area between the price and the pre-crash line (the "recovery deficit") as a risk metric.
- Replace the single crash with a *cluster* of smaller shocks on consecutive days of the same total impact; does a clustered crash recover differently from a one-day crash?
- Compare recovery behaviour between `StockMarketSimulation` and a mean-reverting model (write your own) to see how the absence of mean reversion in this simulator affects long-run recovery.

## Assessment criteria
- **Reproducibility** — `random_seed=42` set and stated; re-running reproduces identical prices and recovery day.
- **Validation** — the event-day price check `prices[100] == prices[99] * (1 + event_impact)` is shown and passes; the pre-crash baseline used for "recovery" is correctly defined as the day *before* the event.
- **Analysis** — recovery time is reported across drift and volatility, and the student explains *why* drift (not volatility) is the dominant driver of *expected* recovery time, while noting that volatility widens the spread of recovery times across seeds.
- **Code quality** — recovery logic is a clean parameterised function, not buried magic numbers; the sweep is looped, not copy-pasted.
