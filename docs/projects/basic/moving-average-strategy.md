# Build a Moving-Average Strategy
**Difficulty**: Intermediate
**Time**: ~50 minutes
**Learning Focus**: time-series backtesting, strategy vs benchmark comparison
**Simulator**: StockMarketSimulation (registry `StockMarket`)

## Overview
A moving-average-crossover strategy buys when a fast average crosses above a slow one (an uptrend) and sells when it crosses back — a classic trend-following rule. Using `StockMarketSimulation` to generate a realistic price series, you implement this rule as a backtest and compare its return to the simplest benchmark of all: buying on day 0 and holding. The question is whether following the trend can beat doing nothing, and you answer it by stating both returns honestly.

## Setup
Install the toolkit (`pip install sim_lab`) and use the class interface: `from sim_lab.core import StockMarketSimulation`. Read the [Stock Market doc](../../simulations/basic/stock_market.md) for the price rule.

## Instructions
1. **Generate a price series.** Make a 252-day trending market with `random_seed=42`:
   ```python
   from sim_lab.core import StockMarketSimulation

   sim = StockMarketSimulation(
       start_price=100, days=252, volatility=0.015, drift=0.0005,
       random_seed=42,
   )
   prices = sim.run_simulation()
   ```

2. **Compute buy-and-hold.** The benchmark return is just the total percentage move:
   ```python
   buy_hold_return = (prices[-1] / prices[0] - 1) * 100
   print("Buy & hold: %.2f%%" % buy_hold_return)
   ```

3. **Code the crossover.** Use a 10-day fast average and a 50-day slow average. Hold the stock when fast > slow, sit in cash otherwise. Track each round-trip:
   ```python
   SHORT, LONG = 10, 50
   in_market = False
   entry = 0
   gains = 0
   for d in range(LONG, len(prices)):
       fast = sum(prices[d - SHORT + 1 : d + 1]) / SHORT
       slow = sum(prices[d - LONG + 1 : d + 1]) / LONG
       if fast > slow and not in_market:
           in_market = True
           entry = prices[d]
       elif fast < slow and in_market:
           in_market = False
           gains += prices[d] - entry
   if in_market:                      # close any open position at the end
       gains += prices[-1] - entry
   strategy_return = gains / prices[0] * 100
   print("MA crossover: %.2f%%" % strategy_return)
   ```

4. **State both returns.** Print the buy-and-hold return and the strategy return side by side, and plot the price with both moving averages and vertical marks at each buy/sell.

5. **Stress-test the rule.** Re-run the backtest across a few market regimes — re-generate the series with different `volatility`/`drift` (and a couple of seeds) — and record whether the strategy beats buy-and-hold in each.

## Things to explore
- Does the strategy add value in a *trending* market (high drift) or a *choppy* one (high volatility, near-zero drift)? Build a small table.
- How sensitive is the result to the window lengths? Try (5, 20) and (20, 100) — which catches bigger moves, which whipsaws more?
- Count the number of round-trip trades. More trades usually means more whipsaw — does return fall as trade count rises?
- If you added a 0.1% transaction cost per trade, does the strategy still beat buy-and-hold?

## Extension ideas
- Add a risk-adjusted comparison: compute the max drawdown of each strategy, not just the return.
- Combine the signal with the crash event from `event_day`/`event_impact` — does the crossover rule get you out before a large negative event, or does it react too slowly?
- Optimise the window lengths over one seed, then test the "best" windows on a *different* seed. Does an in-sample edge survive out-of-sample? (This is overfitting in miniature.)

## Assessment criteria
- **Reproducibility** — `random_seed=42` set and stated; re-running reproduces identical prices and trade list.
- **Validation** — both the buy-and-hold return and the strategy return are computed and stated numerically (validation = the two returns are reported and compared, not merely asserted).
- **Analysis** — the student interprets *why* the strategy wins or loses against buy-and-hold in each regime (trend vs chop), rather than just reporting the number.
- **Code quality** — the backtest is a clean loop with named constants (`SHORT`, `LONG`) and open positions are correctly closed at the end of the series.
