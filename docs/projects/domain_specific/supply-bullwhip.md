# The Bullwhip Effect

**Difficulty**: Advanced
**Time**: ~75 minutes
**Learning Focus**: demand variability amplification, multi-tier inventory dynamics, lead-time effects
**Simulator**: `SupplyChainSimulation` (registry `"SupplyChain"`)

## Overview

A small wiggle in customer demand can grow into a violent swing in the orders a
factory receives. This *bullwhip effect* — order variability amplifying as it
travels upstream, away from the customer — is the central pathology of multi-tier
supply chains: each tier over-orders to protect itself against uncertainty and
lead-time delay, and the distortion compounds tier by tier. This project asks:
**how much does order variability grow between the retailer, the distributor, and
the factory, and what makes it worse?** You will build a three-tier chain, drive the
retailer with noisy demand, and measure the variance of the order stream at each
tier.

## Setup

Install sim-lab and build networks from `Factory`, `Distributor`, `Retailer`, and
`SupplyChainLink` connected inside a `SupplyChainSimulation`. See the
[Supply Chain Simulation docs](../../simulations/domain_specific/supply_chain.md)
for the node, policy, and demand-generator reference.

```bash
pip install sim_lab
```

## Instructions

1. **Build a three-tier network.** Connect a Factory to a Distributor to a
   Retailer with directed links. Give each tier enough starting stock and a
   `base_stock_policy` that restocks toward a target level.

   ```python
   from sim_lab.core import (
       SupplyChainSimulation, Factory, Distributor, Retailer, SupplyChainLink,
       base_stock_policy, normal_demand,
   )
   import numpy as np

   factory = Factory("Factory", production_capacity=2000, production_cost=2.0,
                     initial_inventory=2000, lead_time=1)
   distributor = Distributor("Distributor", shipping_cost=0.3,
                             initial_inventory=1500, lead_time=3)
   retailer = Retailer("Retailer", holding_cost=0.10, stockout_cost=2.0,
                       initial_inventory=600, lead_time=2)

   nodes = {"Factory": factory, "Distributor": distributor, "Retailer": retailer}
   links = [SupplyChainLink(factory, distributor), SupplyChainLink(distributor, retailer)]
   ```

2. **Drive the retailer with noisy demand.** Use `normal_demand` so each day's
   demand fluctuates around a mean — the random wobble is what the bullwhip
   amplifies.

   ```python
   sim = SupplyChainSimulation(
       nodes=nodes,
       links=links,
       demand_generator=normal_demand(100, 15),   # mean 100, std 15
       ordering_policies={
           "Factory": base_stock_policy(2000),
           "Distributor": base_stock_policy(1200),
           "Retailer": base_stock_policy(500),
       },
       days=200,
       random_seed=42,
   )
   results = sim.run_simulation()
   ```

3. **Extract the order stream at each tier.** The order *received* by a node is the
   order *placed* by the tier below it, so the bullwhip is read straight from the
   `orders_received` history as you move upstream:

   - **Customer demand** the retailer sees → `results["Retailer"]["demand"]`
   - **Retailer → distributor orders** → `results["Distributor"]["orders_received"]`
   - **Distributor → factory orders** → `results["Factory"]["orders_received"]`

   ```python
   demand     = np.array(results["Retailer"]["demand"][1:])
   ret_orders = np.array(results["Distributor"]["orders_received"][1:])
   dist_orders = np.array(results["Factory"]["orders_received"][1:])

   print("tier              variance")
   print("demand         ", round(demand.var(), 1))
   print("retailer orders", round(ret_orders.var(), 1))
   print("distributor ord", round(dist_orders.var(), 1))
   ```

4. **Confirm amplification upstream.** Compute the variance of each series. The
   chain should show monotone growth — `Var(demand) < Var(retailer orders) <
   Var(distributor orders)`. With the setup above you should see roughly
   $\sim\!240 \to \sim\!2{,}500 \to \sim\!31{,}000$, i.e. the factory's order
   stream varies well over a hundred times more than the demand that started it.

5. **Visualise the whip.** Plot all three series on shared axes (or as three
   stacked sub-panels) so the growing swings are obvious as your eye moves upstream
   toward the factory.

   ```python
   import matplotlib.pyplot as plt
   fig, ax = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
   ax[0].plot(demand, color="tab:blue");     ax[0].set_ylabel("Customer demand")
   ax[1].plot(ret_orders, color="tab:orange"); ax[1].set_ylabel("Retailer orders")
   ax[2].plot(dist_orders, color="tab:green"); ax[2].set_ylabel("Distributor orders")
   ax[2].set_xlabel("Day")
   fig.suptitle("The bullwhip effect: order variance grows upstream")
   plt.show()
   ```

6. **Quantify the amplification.** Report a *variance amplification ratio* at each
   tier, e.g. `Var(retailer orders)/Var(demand)` and
   `Var(distributor orders)/Var(demand)`, and state which tier shows the largest
   swing.

## Things to explore

- **Worsen it with lead time.** Raise the distributor's `lead_time` from 3 to 6.
  Does the upstream amplification grow? Why do longer lead times make the bullwhip
  worse?
- **Steady demand kills it.** Swap `normal_demand(100, 15)` for
   `constant_demand(100)`. Does any amplification remain? What does that tell you
   about the *source* of the whip?
- **Policy matters.** Try very different base-stock targets per tier versus
  identical targets — does mismatched targeting dampen or amplify the effect?
- **Vary the noise.** Sweep the demand standard deviation over `5, 15, 30`. Does
  the amplification *ratio* stay roughly constant, or grow with the noise?

## Extension ideas

- Replace `base_stock_policy` with `economic_order_quantity` at one tier and
  measure whether fixed-lot ordering dampens or amplifies the whip compared with a
  reactive base-stock rule.
- Add a *second retailer* sharing the single distributor and spike both retailers'
  demand on the same day — how much worse does the factory's swing get?
- Compute a moving average of demand at the distributor (a simple "smoothing"
  policy) and show how much it cuts the upstream variance — the basis of real-world
  demand-smoothing and VMI (vendor-managed inventory) countermeasures.

## Assessment criteria

- [ ] **Reproducibility** — `random_seed=42` is set on the simulation (and the same
      seed feeds `normal_demand`'s draws); re-running reproduces identical order
      series and variances.
- [ ] **Validation** — the student demonstrates the bullwhip law: order variance
      amplifies **monotonically upstream**,
      `Var(demand) < Var(retailer orders) < Var(distributor orders)` (here roughly
      $\sim\!240 < \sim\!2{,}500 < \sim\!31{,}000$), and explicitly maps each
      variance to the correct `orders_received` / `demand` history series.
- [ ] **Analysis** — the three-panel plot is interpreted: *why* variability grows
      tier by tier (each node reacts to perceived demand change plus its own
      inventory/lead-time buffer), and at least one driver (lead time or demand
      noise) is varied with its effect explained.
- [ ] **Code quality** — the three-tier network is built from reusable node/link
      objects; variance is computed with `numpy` over the recorded histories rather
      than hand-rolled loops; no magic numbers buried in the simulation setup.
