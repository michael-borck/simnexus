# Supply Chain Simulation

## Purpose

This simulation models the flow of products through a multi-tier supply chain network made up of factories, distributors, and retailers connected by directed links. It lets students explore how inventory decisions, ordering policies, and lead times propagate through a network — and, in particular, how small swings in customer demand can grow into large swings in upstream orders. It is a practical tool for studying service levels, holding and stockout costs, and the classic *bullwhip effect*.

## Parameters

- `nodes` (`Dict[str, SupplyChainNode]`): Dictionary of every node in the network, keyed by node name. Nodes are typically `Factory`, `Distributor`, and `Retailer` instances.
- `links` (`List[SupplyChainLink]`): Ordered connections between nodes. Each `SupplyChainLink(source, destination)` defines a directed supplier → customer relationship; nodes with no outgoing customers are treated as retailers that face end-customer demand.
- `demand_generator` (`callable`): A function `(day, retailer_name) -> float` that returns the customer demand for a retailer on a given day. Use the bundled helpers `constant_demand`, `seasonal_demand`, or `normal_demand`, or supply your own.
- `ordering_policies` (`Dict[str, callable]`): Maps **every** node name to an ordering-policy function `(node, day, simulation) -> Dict[str, float]` that returns how much to order from each supplier. Use the bundled `base_stock_policy` or `economic_order_quantity`, or supply your own. A policy must be provided for every node (including sources with no suppliers, whose policy is never invoked).
- `days` (`int`, default `100`): Number of days to simulate.
- `random_seed` (`Optional[int]`, default `None`): Seed for reproducible random number generation (e.g. for `normal_demand`).

## Example Code

```python
from sim_lab.core import (
    SupplyChainSimulation,
    Factory,
    Distributor,
    Retailer,
    SupplyChainLink,
    base_stock_policy,
    constant_demand,
)
import matplotlib.pyplot as plt

# Build a three-tier network: Factory -> Distributor -> Retailer.
factory = Factory(
    name="Factory",
    production_capacity=60,
    production_cost=2.0,
    initial_inventory=500,
)
distributor = Distributor(
    name="Distributor",
    shipping_cost=0.30,
    initial_inventory=800,
    lead_time=2,
)
retailer = Retailer(
    name="Retailer",
    selling_price=8.0,
    holding_cost=0.10,
    stockout_cost=2.0,
    initial_inventory=500,
    lead_time=1,
)

nodes = {"Factory": factory, "Distributor": distributor, "Retailer": retailer}
links = [
    SupplyChainLink(factory, distributor),
    SupplyChainLink(distributor, retailer),
]

# Every node restocks toward a target level; the retailer faces steady demand.
sim = SupplyChainSimulation(
    nodes=nodes,
    links=links,
    demand_generator=constant_demand(15),
    ordering_policies={
        "Factory": base_stock_policy(target_level=400),
        "Distributor": base_stock_policy(target_level=300),
        "Retailer": base_stock_policy(target_level=250),
    },
    days=30,
    random_seed=42,
)

results = sim.run_simulation()

# Plot inventory across the three tiers.
plt.figure(figsize=(10, 6))
plt.plot(results["Retailer"]["inventory"], label="Retailer inventory")
plt.plot(results["Distributor"]["inventory"], label="Distributor inventory")
plt.plot(results["Factory"]["inventory"], label="Factory inventory")
plt.xlabel("Day")
plt.ylabel("Units in inventory")
plt.title("Supply Chain Simulation: Inventory Across Tiers")
plt.legend()
plt.show()

print(f"Service level: {sim.service_level:.1%}")
print(f"Total profit:  ${sim.total_profit:,.2f}")
```

## Use Case Ideas

### Investigate the Bullwhip Effect

The bullwhip effect is the tendency for order variability to grow as it moves *upstream* — away from the customer. A modest wobble in retail demand can become a large swing in distributor orders, and an even larger swing in factory orders, because each tier over-orders to protect itself against uncertainty and lead-time delays. Build the network above, switch the demand generator to `seasonal_demand` or `normal_demand`, and plot the `orders_received` history recorded at each tier.

Questions to Consider:

  - How does the variance of `orders_received` compare between the retailer, distributor, and factory? Which tier shows the largest swings?

  - What happens to the amplification when you lengthen a node's `lead_time`? Why do longer lead times tend to worsen the bullwhip?

  - If every tier uses the same `base_stock_policy` target, does that dampen or amplify the effect compared with tiers using very different targets?

### Investigate Ordering Policies and Inventory Costs

Compare `base_stock_policy` against `economic_order_quantity` on the same network and demand. Each policy trades off ordering frequency against inventory holding cost differently, which shows up directly in the recorded cost histories.

Questions to Consider:

  - Under `economic_order_quantity`, how does the optimal order quantity $Q^* = \sqrt{2DK/h}$ change when you raise the holding cost `h` or the setup cost `K`? Do your runs match the formula?

  - Which policy keeps the retailer's `stockout_cost` lower, and at what cost in `holding_cost`?

  - How does the overall `total_profit` ($\text{revenue} - \text{costs}$) differ between the two policies for the same demand?

### Investigate Service Level Under Stress

Drive demand up or shrink the retailers' starting buffers and watch the service level $\text{SL} = \sum \text{sales} / \sum \text{demand}$ degrade as stockouts appear. This is a direct way to connect inventory decisions to customer-facing performance.

Questions to Consider:

  - At what demand level does the retailer start losing sales, and how quickly does the service level fall once stockouts begin?

  - How does raising the base-stock target (or the EOQ reorder point) recover the service level, and how much extra holding cost does that cost?

  - If you add a second retailer sharing one distributor, how is the service level of each affected when demand spikes simultaneously?

## Model Description

Each simulated day runs through a fixed sequence, mirroring the daily loop in `SupplyChainSimulation.run_simulation`:

1. **Demand and sales.** Every node with no downstream customers is a *retailer*. For each retailer, `demand_generator(day, retailer_name)` returns the day's customer demand, and the retailer fulfils what it can from inventory. Sales are capped at available stock: $\text{sold} = \min(\text{demand}, \text{inventory})$. The shortfall $\text{demand} - \text{sold}$ incurs a per-unit `stockout_cost`, and the revenue is $\text{sold} \times \text{selling\_price}$.

2. **Ordering.** Each node that has suppliers applies its ordering policy, which returns a `{supplier_name: amount}` map. The simulation then calls `supplier.place_order(amount)` on each supplier, which pulls units out of the supplier's inventory immediately ($\text{fulfilled} = \min(\text{amount}, \text{inventory})$) and adds any shortfall to the supplier's `order_backlog`. The two bundled policies are:

   - **Base stock policy** — on every review day, order enough to restore the inventory position to a target level $S$:
     $$Q = S - IP, \qquad IP = \text{inventory} + \sum \text{pending\_shipments}$$
     where $Q$ is split equally across the node's suppliers and is placed only when $Q > 0$.

   - **Economic Order Quantity (EOQ)** — place a fixed optimal lot size whenever the inventory position drops to the reorder point:
     $$Q^* = \sqrt{\frac{2 D K}{h}}, \qquad R = D \cdot L$$
     Here $D$ is the demand rate, $K$ the setup cost per order, $h$ the per-unit holding cost, and $L$ the node's `lead_time`. The lot $Q^*$ is split equally across suppliers.

3. **Production.** Each `Factory` produces to clear its order backlog, bounded by both its daily `production_capacity` and its free storage capacity: $\text{produced} = \min(\text{backlog}, \text{production\_capacity}, \text{capacity} - \text{inventory})$. Production incurs `production_cost` per unit.

4. **Shipping.** Along each link, a `Distributor` ships available inventory against the destination's order backlog: $\text{shipped} = \min(\text{source.inventory}, \text{destination.order\_backlog})$. The shipment is scheduled to arrive after the destination's `lead_time` and incurs the distributor's `shipping_cost` per unit.

5. **State update.** Each node processes shipments due to arrive that day (`receive_shipment` adds them to inventory up to capacity), then works off its own backlog from any remaining inventory. Retailers also accrue `holding_cost` on the units still in stock.

6. **Metrics.** Across the run the simulation aggregates:
   - Service level: $\text{SL} = \dfrac{\sum \text{sales}}{\sum \text{demand}}$
   - Total revenue (from retailers), and total costs split into production (factories), shipping (distributors), and holding + stockout (retailers)
   - Profit: $\Pi = \text{revenue} - (C_{\text{production}} + C_{\text{shipping}} + C_{\text{holding}} + C_{\text{stockout}})$

   `run_simulation` returns a dictionary keyed by node name, each holding that node's full metric history (`inventory`, `orders_received`, `orders_fulfilled`, `shipments_sent`, `shipments_received`, `backlog`, plus the role-specific series), together with an `overall_metrics` entry carrying `service_level`, `total_profit`, `total_revenue`, and `total_costs`.

The bundled **demand generators** drive the retailers:

- `constant_demand(rate)` — flat demand: $d(t) = \text{rate}$.
- `seasonal_demand(base_rate, amplitude, period)` — sinusoidal demand:
  $$d(t) = \text{base\_rate}\left(1 + a \cdot \sin\!\left(\frac{2\pi t}{T}\right)\right)$$
- `normal_demand(mean, std_dev)` — Gaussian demand $d \sim \mathcal{N}(\mu, \sigma^2)$, clamped to be non-negative. This is the generator most likely to reveal the bullwhip effect, since its random fluctuations are amplified tier by tier as each node's policy reacts to perceived demand changes.
