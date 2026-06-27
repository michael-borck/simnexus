import random

import pytest

from sim_lab.core import SimulatorRegistry, create_small_world_network


def _ring_topology(num_nodes=20, k=4):
    """Build a deterministic, connected 4-regular ring-lattice topology.

    Uses the project helper ``create_small_world_network`` with ``beta=0.0``
    (no rewiring) so the structure is fully deterministic: every node has
    degree ``k`` and the graph is connected.
    """
    base = create_small_world_network(num_nodes=num_nodes, k=k, beta=0.0)
    initial_nodes = {nid: dict(node.attributes) for nid, node in base.nodes.items()}
    initial_edges = [(e.source, e.target, {"weight": float(e.weight)}) for e in base.edges]
    return initial_nodes, initial_edges


def _si_update_factory(infection_rate):
    """Return an SI (susceptible->infected) update function.

    Each step, every infected node attempts to infect its susceptible
    neighbours. ``infection_rate >= 1.0`` is treated as certain transmission
    (no RNG), and ``infection_rate == 0.0`` never transmits -- both cases are
    therefore fully deterministic and independent of the global RNG state.
    """
    certain = infection_rate >= 1.0

    def update(network, day):
        infected = [
            nid for nid, node in network.nodes.items()
            if node.attributes.get("state") == "I"
        ]
        to_infect = set()
        for nid in infected:
            for neighbour in network.nodes[nid].neighbors:
                if network.nodes[neighbour].attributes.get("state") == "S":
                    if certain or random.random() < infection_rate:
                        to_infect.add(neighbour)
        for neighbour in to_infect:
            network.nodes[neighbour].update_attribute("state", "I")

    return update


def _edge_growth_update(network, day):
    """Add one random non-duplicate edge per step.

    Mutates topology (so the topology-only metrics returned by
    ``run_simulation`` evolve over time) and consumes the seeded RNG, which
    makes reproducibility a meaningful rather than trivial check. Only used on
    fresh instances, never re-run on the same instance.
    """
    node_ids = list(network.nodes.keys())
    if len(node_ids) < 2:
        return
    for _ in range(10):
        a, b = random.sample(node_ids, 2)
        if b not in network.nodes[a].neighbors:
            network.add_edge(a, b, network.directed, 1.0, {})
            return


def test_initialization():
    """Test initialization of the NetworkSimulation class."""
    initial_nodes, initial_edges = _ring_topology()

    sim = SimulatorRegistry.create(
        "Network",
        initial_nodes=initial_nodes,
        initial_edges=initial_edges,
        update_function=lambda network, day: None,
        directed=False,
        days=20,
        save_history=False,
        random_seed=42,
    )

    assert sim.days == 20
    assert sim.random_seed == 42
    assert sim.directed is False
    assert sim.save_history is False
    assert sim.update_function is not None
    assert len(sim.nodes) == 20
    # 4-regular ring: 20 nodes * 4 / 2 = 40 undirected edges.
    assert len(sim.edges) == 40
    # Metrics dict is initialised empty before the first run.
    assert sim.metrics == {}


def test_run_simulation_output_length():
    """Test that run_simulation returns one metrics dict per time step."""
    initial_nodes, initial_edges = _ring_topology()

    sim = SimulatorRegistry.create(
        "Network",
        initial_nodes=initial_nodes,
        initial_edges=initial_edges,
        update_function=lambda network, day: None,
        days=20,
        random_seed=42,
    )

    metrics = sim.run_simulation()

    assert isinstance(metrics, list)
    assert len(metrics) == 20
    assert set(metrics[0].keys()) == {"num_nodes", "num_edges", "avg_degree", "density"}
    # Static ring: node/edge counts and average degree are invariant.
    assert metrics[0]["num_nodes"] == 20
    assert metrics[0]["num_edges"] == 40
    assert metrics[0]["avg_degree"] == pytest.approx(4.0)
    # density = 2 * edges / (nodes * (nodes - 1)) = 80 / 380.
    assert metrics[0]["density"] == pytest.approx(80.0 / 380.0)


def test_run_simulation_reproducibility():
    """Two fresh instances with the same seed produce identical metric series."""
    def make():
        initial_nodes, initial_edges = _ring_topology()
        return SimulatorRegistry.create(
            "Network",
            initial_nodes=initial_nodes,
            initial_edges=initial_edges,
            update_function=_edge_growth_update,
            directed=False,
            days=20,
            random_seed=42,
        )

    sim1 = make()
    sim2 = make()

    out1 = sim1.run_simulation()
    out2 = sim2.run_simulation()

    assert out1 == out2
    # Confirm the series is non-trivial: edge growth actually advanced the
    # topology, so reproducibility is a real check rather than a constant list.
    assert out1[-1]["num_edges"] > out1[0]["num_edges"]


def test_infection_rate_directional_effect():
    """Higher infection rate yields strictly more spread on a connected ring."""
    num_nodes = 20

    def build(rate):
        initial_nodes, initial_edges = _ring_topology(num_nodes)
        seeded = {
            nid: {"state": "I" if nid == 0 else "S"}
            for nid in initial_nodes
        }
        return SimulatorRegistry.create(
            "Network",
            initial_nodes=seeded,
            initial_edges=initial_edges,
            update_function=_si_update_factory(rate),
            directed=False,
            days=20,
            random_seed=42,
        )

    def final_infected(sim):
        sim.run_simulation()
        return sum(
            1 for node in sim.nodes.values()
            if node.attributes.get("state") == "I"
        )

    final_low = final_infected(build(0.0))
    final_high = final_infected(build(1.0))

    # No transmission: only the seed node remains infected.
    assert final_low == 1
    # Certain transmission over a connected ring infects the whole population.
    assert final_high == num_nodes
    # Directional invariant: raising the rate increases total spread.
    assert final_high > final_low


def test_base_simulation_methods():
    """Test reset() reusability and get_parameters_info() from BaseSimulation."""
    initial_nodes, initial_edges = _ring_topology()
    seeded = {
        nid: {"state": "I" if nid == 0 else "S"}
        for nid in initial_nodes
    }

    sim = SimulatorRegistry.create(
        "Network",
        initial_nodes=seeded,
        initial_edges=initial_edges,
        update_function=_si_update_factory(0.5),
        directed=False,
        days=20,
        save_history=False,
        random_seed=42,
    )

    # The SI update mutates only node *attributes*, not topology, so the
    # topology-only metrics returned by run_simulation are identical whether
    # the instance is re-run directly or after an explicit reset().
    sim.run_simulation()
    result1 = sim.run_simulation()

    sim.reset()
    result2 = sim.run_simulation()

    assert result1 == result2
    assert len(result2) == 20

    params = sim.get_parameters_info()
    assert isinstance(params, dict)
    assert "days" in params
    assert "random_seed" in params
    assert "initial_nodes" in params
    assert "initial_edges" in params
    assert "update_function" in params
    assert "directed" in params
