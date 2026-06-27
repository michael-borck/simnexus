# Product Popularity Simulation

## Purpose

This simulation models the dynamics of product popularity, allowing students to explore factors affecting market demand and the effectiveness of marketing strategies.

## Parameters

- `start_demand`: The initial demand for the product.
- `days`: The duration of the simulation.
- `growth_rate`: The rate at which product demand grows or declines naturally over time.
- `marketing_impact`: The impact of marketing efforts on demand, represented as a percentage increase.
- `promotion_day`: Specifies the day on which a major marketing campaign starts (optional).
- `promotion_effectiveness`: The effectiveness of the promotional campaign, impacting demand growth positively.

## Example Code

```python
from sim_lab.core import ProductPopularitySimulation
import matplotlib.pyplot as plt

# Setting up a scenario with moderate natural growth and a significant marketing campaign.
sim = ProductPopularitySimulation(start_demand=500, days=180, growth_rate=0.02, 
                                  marketing_impact=0.1, promotion_day=30, promotion_effectiveness=0.5)

demand = sim.run_simulation()

# Visualizing product popularity
plt.figure(figsize=(10, 6))
plt.plot(demand, label='Product Demand')
plt.axvline(x=sim.promotion_day, color='blue', linestyle='--', label='Marketing Campaign Start')
plt.xlabel('Days')
plt.ylabel('Demand Units')
plt.title('Product Popularity Simulation')
plt.legend()
plt.show()
```

## Conducting Visual Analysis Using the Simulation

Experiment! Use the simulation to explore and test various scenarios. Adjust parameters, try different strategies, and analyse the outcomes to gain deeper insights into resource management under fluctuating conditions.

- **Baseline Scenario Without Marketing Efforts**: Begin by running simulations without any marketing efforts to understand the natural demand growth. This baseline will help you compare the effectiveness of different marketing strategies.
  
- **Labeling and Annotations**: Make sure your plots are well-labeled with days on the x-axis and demand units on the y-axis. Use annotations or markers to highlight when significant marketing campaigns start and their duration if applicable.

- **Interactive Exploration**: If possible, use interactive tools to adjust the parameters like growth rate, marketing impact, and timing of campaigns dynamically. This can help visualize the immediate effects of these changes on the demand curve.

- **Comparative Analysis**: Run multiple scenarios side-by-side to directly compare different growth rates, marketing impacts, or strategies. This comparison can make it easier to visualize which scenarios are most effective. Consider calculating and comparing statistics such as the average price before and after a disruption event to quantify its impact.


## Use Case Ideas

### Examine How Changes in Growth Rate and Marketing Impact Affect Demand

Start by considering how natural growth influences demand over time. Introduce varying levels of marketing impact and observe how each setting alters the demand curve. Questions to Consider:

  - How does increasing the growth rate affect the overall demand by the end of the simulation?

  - What happens when you combine high growth rates with strong marketing impacts?

### Simulate a Major Marketing Campaign and Analyze Its Effect on Demand Growth

Set up a scenario where a marketing campaign kicks in at a specific day. Vary the effectiveness of these campaigns to see different outcomes. Questions to Consider:

  - How does the timing of a marketing campaign influence its effectiveness?

  - Compare the demand before and after the promotion day. What insights can you gain about the campaign’s impact?

### Explore Different Marketing Strategies and Their Cost-Effectiveness

Implement various hypothetical marketing strategies with assumed costs and effectiveness. Calculate the return on investment (ROI) for each strategy based on the increase in demand they generate versus their costs. Questions to Consider:

  - Which marketing strategy offers the best ROI?

  - How does the cost of a strategy relate to its effectiveness in boosting demand?

## Model Description

The Product Popularity Simulation class models the demand for a product over time, considering factors such as natural growth, marketing impact, and promotional campaigns. The simulation formula includes:

- Natural Growth: \( \text{Natural Growth} = \text{Previous Demand} \times (1 + \text{Growth Rate}) \)
- Marketing Influence: \( \text{Marketing Influence} = \text{Previous Demand} \times \text{Marketing Impact} \)
- Promotional Impact: On promotional days, the demand is further adjusted by a factor of \( \text{Promotion Effectiveness} \).

See [Modelling Market Dynamics](./modelling_market_dynamics.md) for more information.