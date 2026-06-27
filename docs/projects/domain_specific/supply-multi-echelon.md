# Multi-Echelon Inventory

**Difficulty**: Advanced
**Time**: ~80 minutes
**Learning Focus**: inventory ordering policies, the EOQ tradeoff $Q^*=\sqrt{2DK/h}$, responsiveness vs. cost
**Simulator**: `SupplyChainSimulation` (registry `"SupplyChain"`)

## Overview

In a multi-tier supply chain, *how* each node restocks is as important as *how
much*. Two classic policies sit at opposite ends of a spectrum: a **base-stock**
policy reacts to every demand signal and restocks to a target each period, while an
**Economic Order Quantity (EOQ)** policy ignores day-to-day noise and places
fixed-size lots of an analytically optimal size. This project asks: **how do the
two policies differ in their order pattern, and what is the cost of a reactive
policy?** You will run the same Factory→Distributor→Retailer chain under each policy,
verify the EOQ lot size against its formula, and trade total cost against
responsiveness.

## Setup

Install sim-lab and build networks from `Factory`, `Distributor`, `Retailer`, and
`SupplyChainLink` inside a `SupplyChainSimulation`. Use the bundled `base_stock_policy`
and `economic_order_quantity` policies and the `normal_demand` generator. See the
[Supply Chain Simulation docs](../../simulations/domain_specific/supply_chain.md)
for the full reference.

```bash
pip install sim_lab
```

## Instructions

1. **Build the three-tier chain** and a helper to run it under a chosen retailer and
   distributor policy.

   ```python
   from sim_lab.core import (
       SupplyChainSimulation, Factory, Distributor, Retailer, SupplyChainLink,
       base_stock_policy, economic_order_quantity, normal_demand,
   )
   import numpy as np
   import math

   def build_chain():
       factory = Factory("Factory", production_capacity=5000, production_cost=2.0,
                         initial_inventory=20000, lead_time=1)
       distributor = Distributor("Distributor", shipping_cost=0.3,
                                 initial_inventory=5000, lead_time=2)
       retailer = Retailer("Retailer", holding_cost=0.10, stockout_cost=2.0,
                           initial_inventory=1500, lead_time=2)
       nodes = {"Factory": factory, "Distributor": distributor, "Retailer": retailer}
       links = [SupplyChainLink(factory, distributor), SupplyChainLink(distributor, retailer)]
       return nodes, links

   def run(policy_d, policy_r, days=80):
       nodes, links = build_chain()
       sim = SupplyChainSimulation(
           nodes=nodes, links=links,
           demand_generator=normal_demand(100, 20),
           ordering_policies={
               "Factory": base_stock_policy(3000),
               "Distributor": policy_d,
               "Retailer": policy_r,
           },
           days=days, random_seed=42,
       )
       return sim, sim.run_simulation()
   ```

2. **Verify the EOQ lot size against its formula.** With average demand $D=100$,
   setup cost $K=50$, and holding cost $h=0.10$, the optimal lot size is
   $Q^* = \sqrt{2DK/h} = \sqrt{2\cdot100\cdot50/0.10} \approx 316.2$. Run the chain
   under EOQ and read the orders the retailer places — each non-zero order should be
   exactly $Q^*$.

   ```python
   D, K, h = 100, 50, 0.10
   Qstar = math.sqrt(2 * D * K / h)
   print("Q* =", round(Qstar, 1))

   _, res = run(economic_order_quantity(D, K, h), economic_order_quantity(D, K, h))
   retailer_orders = np.array(res["Distributor"]["orders_received"][1:])
   nonzero = [round(x) for x in retailer_orders if x > 0]
   print("retailer order sizes:", nonzero[:8])
   print("every order equals Q*?", all(abs(x - Qstar) < 1 for x in nonzero))
   ```

3. **Show base-stock reacts to demand shocks.** Run the same chain under a base-stock
   rule and compare the retailer's order stream. Base-stock restocks the full deficit
   each period, so its order sizes vary widely with demand; EOQ's are a train of
   identical $Q^*$ pulses. Capture this with the order variance.

   ```python
   _, res_bs = run(base_stock_policy(3000), base_stock_policy(1500))
   bs_orders = np.array(res_bs["Distributor"]["orders_received"][1:])
   eoq_orders = np.array(res["Distributor"]["orders_received"][1:])

   print("base-stock order sizes:", [round(x) for x in bs_orders if x > 0][:8])
   print("EOQ      order sizes:", [round(x) for x in eoq_orders if x > 0][:8])
   print("base-stock order variance:", round(bs_orders.var(), 0))
   print("EOQ       order variance:", round(eoq_orders.var(), 0))
   ```

4. **Trade total cost against responsiveness.** Pull the overall metrics from each
   run and break the cost into its components. Base-stock's reactivity transmits
   demand swings upstream (the factory produces in large, costly bursts to chase
   the amplified order signal), so its total cost is far higher than EOQ's even
   though both face identical demand.

   ```python
   sim_bs, res_bs = run(base_stock_policy(3000), base_stock_policy(1500))
   sim_eoq, res_eoq = run(economic_order_quantity(D, K, h), economic_order_quantity(D, K, h))

   for label, sim in [("base-stock", sim_bs), ("EOQ", sim_eoq)]:
       print(f"{label:10s} service_level={sim.service_level:.2f} "
             f"total_cost={sim.total_costs:,.0f} profit={sim.total_profit:,.0f}")

   # Break the cost down by component for each policy.
   for label, res in [("base-stock", res_bs), ("EOQ", res_eoq)]:
       print(f"\n{label} costs:")
       print("  holding  :", round(sum(res["Retailer"]["holding_cost"]), 0))
       print("  stockout :", round(sum(res["Retailer"]["stockout_cost"]), 0))
       print("  shipping :", round(sum(res["Distributor"]["shipping_cost"]), 0))
       print("  production:", round(sum(res["Factory"]["production_cost"]), 0))
   ```

   Which component explains most of the cost gap between the two policies?

5. **Plot the two order streams** on shared axes. The base-stock series should look
   like a noisy echo of demand; the EOQ series like a regular comb of equal pulses.

   ```python
   import matplotlib.pyplot as plt
   plt.figure(figsize=(10, 5))
   plt.plot(bs_orders, label="base-stock orders", alpha=0.8)
   plt.plot(eoq_orders, label="EOQ orders", alpha=0.8)
   plt.axhline(Qstar, color="grey", linestyle="--", label=f"Q* = {Qstar:.0f}")
   plt.xlabel("Day"); plt.ylabel("Retailer order quantity")
   plt.legend(); plt.title("Base-stock (reactive) vs EOQ (fixed-lot) ordering")
   plt.show()
   ```

## Things to explore

- **Perturb the EOQ inputs.** Double the holding cost $h$, then double the setup
  cost $K$. Does the observed lot size track the new $Q^*=\sqrt{2DK/h}$ each time?
- **Vary the base-stock target.** Raise the retailer's target from 1500 toward 3000.
  How do the order variance and the retailer holding cost change?
- **Mix the policies.** Put base-stock on the retailer and EOQ on the distributor
  (or vice-versa). Does a fixed-lot tier dampen the upstream amplification?
- **Inventory-vs-service tradeoff.** Raise the retailer's `initial_inventory` (and
  its base-stock target) step by step. How does `service_level` rise, and how much
  extra `holding_cost` does each point of service cost?

## Extension ideas

- Add a per-order **setup cost** to the cost model (a fixed charge every time a node
  places an order) and show that EOQ minimises the classic holding-plus-setup
  tradeoff that its formula is derived from.
- Drive the chain with `seasonal_demand` instead of `normal_demand` and compare how
  each policy tracks a predictable surge versus a random one.
- Combine this project with *The Bullwhip Effect*: measure the upstream variance
  amplification under base-stock versus EOQ and argue, from your cost numbers, why
  fixed-lot ordering is a practical bullwhip countermeasure.

## Assessment criteria

- [ ] **Reproducibility** — `random_seed=42` is set on every run (and seeds
      `normal_demand`'s draws); re-running reproduces identical order series, lot
      sizes, and cost figures.
- [ ] **Validation** — the student verifies two laws: (1) **EOQ orders in lots of
      $Q^* = \sqrt{2DK/h}$** — the formula value (≈316.2 for $D=100,K=50,h=0.10$)
      matches every observed order; and (2) **base-stock reacts to demand shocks**
      — its order stream varies widely (e.g. ~200–980, variance ~100,000) while
      EOQ's is a fixed-size pulse train (variance ~13,000).
- [ ] **Analysis** — the cost comparison is interpreted: *why* the reactive base-stock
      policy is far more expensive than EOQ (it amplifies demand variability
      upstream into costly factory production swings), and the responsiveness-vs-cost
      tradeoff is stated clearly.
- [ ] **Code quality** — the chain is built once by a reusable helper and reused for
      both policies (no duplicated network setup); the cost breakdown reads from the
      recorded histories rather than being recomputed by hand; EOQ parameters are
      named constants ($D,K,h$), not magic numbers.
