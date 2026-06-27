import math

import pytest
from sim_lab.core import (
    SimulatorRegistry,
    Factory,
    Distributor,
    Retailer,
    SupplyChainLink,
    base_stock_policy,
    constant_demand,
)


def _build_supply_chain(days=20, random_seed=42, retailer_stockout_cost=1.0):
    """Build a small Factory -> Distributor -> Retailer supply chain.

    Returns a kwargs dict ready for ``SimulatorRegistry.create("SupplyChain", ...)``.
    Fresh node/link/policy objects are constructed on every call so that each
    simulation instance owns an independent, mutable history.
    """
    factory = Factory(
        name="Factory",
        production_capacity=100,
        production_cost=1.0,
        initial_inventory=100,
        capacity=1000,
        lead_time=1,
    )
    distributor = Distributor(
        name="Distributor",
        shipping_cost=0.5,
        initial_inventory=50,
        capacity=1000,
        lead_time=1,
    )
    retailer = Retailer(
        name="Retailer",
        selling_price=5.0,
        holding_cost=0.1,
        stockout_cost=retailer_stockout_cost,
        initial_inventory=0,
        capacity=1000,
        lead_time=1,
    )
    nodes = {"Factory": factory, "Distributor": distributor, "Retailer": retailer}
    links = [
        SupplyChainLink(factory, distributor),
        SupplyChainLink(distributor, retailer),
    ]
    # The simulation requires an ordering policy for every node, including the
    # Factory (which has no suppliers and is therefore skipped at runtime).
    ordering_policies = {
        "Factory": base_stock_policy(target_level=200),
        "Distributor": base_stock_policy(target_level=100),
        "Retailer": base_stock_policy(target_level=60),
    }
    return {
        "nodes": nodes,
        "links": links,
        "demand_generator": constant_demand(20),
        "ordering_policies": ordering_policies,
        "days": days,
        "random_seed": random_seed,
    }


def test_initialization():
    """Test initialization of the SupplyChainSimulation class."""
    sim = SimulatorRegistry.create(
        "SupplyChain", **_build_supply_chain(days=20, random_seed=42)
    )
    assert sim.days == 20
    assert sim.random_seed == 42
    assert set(sim.nodes.keys()) == {"Factory", "Distributor", "Retailer"}
    assert len(sim.links) == 2
    # Nodes with no downstream customers are detected as retailers.
    assert sim.retailers == ["Retailer"]
    assert isinstance(sim.nodes["Factory"], Factory)
    assert isinstance(sim.nodes["Distributor"], Distributor)
    assert isinstance(sim.nodes["Retailer"], Retailer)
    # Every node must have a registered ordering policy.
    assert set(sim.ordering_policies.keys()) == set(sim.nodes.keys())


def test_run_simulation_output_length():
    """Test that run_simulation records one entry per simulated day per node."""
    days = 20
    sim = SimulatorRegistry.create(
        "SupplyChain", **_build_supply_chain(days=days, random_seed=42)
    )
    result = sim.run_simulation()

    # Overall metrics are always present.
    assert "overall_metrics" in result
    for key in ("service_level", "total_profit", "total_revenue", "total_costs"):
        assert key in result["overall_metrics"]

    # Inventory history starts at the initial state and appends one value per
    # simulated day via end_day(), so its length is days + 1.
    for node_name in sim.nodes:
        assert len(result[node_name]["inventory"]) == days + 1


def test_run_simulation_reproducibility():
    """Test that two instances with the same seed produce identical results."""
    sim1 = SimulatorRegistry.create(
        "SupplyChain", **_build_supply_chain(days=20, random_seed=42)
    )
    sim2 = SimulatorRegistry.create(
        "SupplyChain", **_build_supply_chain(days=20, random_seed=42)
    )
    result1 = sim1.run_simulation()
    result2 = sim2.run_simulation()
    assert result1 == result2


def test_constant_demand_drives_stockout_costs():
    """Behavioral test: constant demand depletes the retailer and incurs stockout cost.

    With the retailer starting empty and constant demand of 20 units/day, customers
    cannot be fully satisfied early on. Three real invariants follow:
      * the service level stays within [0, 1] (sales can never exceed demand),
      * the downstream retailer's inventory is always finite, non-negative, and
        bounded by its capacity,
      * raising the per-unit stockout cost strictly raises total cost, because
        the inventory dynamics are independent of stockout_cost (only the cost
        accounting changes, and there is positive unfulfilled demand).
    """
    days = 20
    result_low = SimulatorRegistry.create(
        "SupplyChain",
        **_build_supply_chain(days=days, random_seed=42, retailer_stockout_cost=1.0),
    ).run_simulation()
    result_high = SimulatorRegistry.create(
        "SupplyChain",
        **_build_supply_chain(days=days, random_seed=42, retailer_stockout_cost=10.0),
    ).run_simulation()

    # History spans exactly the simulated horizon (initial state + one per day).
    assert len(result_low["Retailer"]["inventory"]) == days + 1

    # Downstream stock metric: finite, non-negative, within capacity.
    inventory = result_low["Retailer"]["inventory"]
    assert all(math.isfinite(x) for x in inventory)
    assert all(x >= 0 for x in inventory)
    assert all(x <= 1000 for x in inventory)

    # Downstream order metric: backlog never goes negative.
    backlog = result_low["Retailer"]["backlog"]
    assert all(x >= 0 for x in backlog)

    # Conservation invariant: 0 <= service_level <= 1.
    service_level = result_low["overall_metrics"]["service_level"][0]
    assert 0.0 <= service_level <= 1.0

    # Directional invariant: higher stockout cost -> strictly higher total cost.
    cost_low = result_low["overall_metrics"]["total_costs"][0]
    cost_high = result_high["overall_metrics"]["total_costs"][0]
    assert cost_high > cost_low


def test_base_simulation_methods():
    """Test reset() and get_parameters_info() inherited from BaseSimulation."""
    sim = SimulatorRegistry.create(
        "SupplyChain", **_build_supply_chain(days=20, random_seed=42)
    )

    # reset() must leave the simulation reusable: a re-run produces the same
    # result as the first run.
    result1 = sim.run_simulation()
    sim.reset()
    result2 = sim.run_simulation()
    assert result1 == result2

    # get_parameters_info returns a dict including the base and supply-chain params.
    params = sim.get_parameters_info()
    assert isinstance(params, dict)
    assert "days" in params
    assert "random_seed" in params
    assert "nodes" in params
    assert "links" in params
    assert "demand_generator" in params
    assert "ordering_policies" in params
