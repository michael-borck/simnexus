# Stock Market Simulation

## Purpose

This simulation models the fluctuations of stock prices, enabling students to explore financial market dynamics and develop basic trading strategies. It serves as a practical tool for understanding the principles of market speculation and risk management.

## Parameters

- `start_price`: The initial price of the stock.
- `days`: The duration of the simulation.
- `volatility`: The measure of price fluctuations, indicating how much the price can vary day-to-day.
- `drift`: Represents the overall trend in stock prices, whether upward or downward.
- `event_day`: Specifies the day on which a major market event occurs (optional).
- `event_impact`: The magnitude of the event’s impact on stock prices, positive for beneficial events and negative for detrimental ones.

**Example Code**

```python
from sim_lab.core import StockMarketSimulation
import matplotlib.pyplot as plt

# Example scenario: High volatility with a downward price trend and a significant market event.
sim = StockMarketSimulation(start_price=100, days=365, volatility=0.03, 
                            drift=-0.001, event_day=100, event_impact=-0.2)

prices = sim.run_simulation()

# Visualising the stock market fluctuations
plt.figure(figsize=(10, 6))
plt.plot(prices, label='Stock Price')
plt.axvline(x=sim.event_day, color='red', linestyle='--', label='Major Market Event')
plt.xlabel('Days')
plt.ylabel('Price ($)')
plt.title('Stock Market Simulation')
plt.legend()
plt.show()
```

## Conducting Visual Analysis Using the Simulation:

Experiment! Use the simulation to explore and test various scenarios. Adjust parameters, try different strategies, and analyse the outcomes to gain deeper insights into resource management under fluctuating conditions.

- **Baseline Scenario Without Disruptions**: Begin by simulating the price path without any disruptions to establish a baseline for comparison with more complex scenarios.
  
- **Labeling and Annotations**: Ensure that your plots clearly show the days on the x-axis and price on the y-axis. Use lines or markers to indicate the day of the event or the implementation of a trading strategy.

- **Interactive Exploration**: If tools are available, adjust parameters such as volatility and drift dynamically to observe how these changes affect the price simulation. This can help in understanding the immediate effects of each parameter.

- **Comparative Analysis**: Conduct side-by-side comparisons of scenarios with different levels of volatility or different strategies to visually assess their impact. This can make it easier to understand which conditions or strategies lead to the most favorable outcomes.  Consider calculating and comparing statistics such as the average price before and after a disruption event to quantify its impact.

## Use Case Ideas

### Investigate How Volatility Affects Stock Price Stability

Begin by analysing how different levels of volatility impact the stability of stock prices and the potential for investment gains or losses. Questions to Consider:

  - How do changes in volatility affect the frequency and magnitude of price swings?

  - What implications does increased volatility have on the risk and potential returns of stock investments?

### Simulate a Major Market Event and Analyse Its Impact

Set up scenarios where a significant market event affects stock prices on a specific day. Adjust the impact of these events to observe varying outcomes. Questions to Consider:

  - How does the market respond to positive versus negative events?

  - Analyse the recovery or further decline in stock prices following the event. What does this tell you about market sentiment and investor behavior?

### Develop and Test Trading Strategies

Explore basic trading strategies such as "buy and hold", "moving average crossover", or "momentum-based" strategies. Implement these strategies in your simulation to test their effectiveness over time. Questions to Consider:

  - Which strategy performs best under stable versus volatile market conditions?

  - How do these strategies perform in response to the simulated market events?


## Model Description

The Stock Market Simulation class focuses on the fluctuations in stock prices influenced by daily volatility, market trends, and specific market events. The simulation adjusts stock prices daily based on:

- Random daily changes due to volatility and drift.
- Event impacts that multiplicatively affect the stock prices on designated days.

See [Modelling Market Dynamics](./modelling_market_dynamics.md) for more information.
