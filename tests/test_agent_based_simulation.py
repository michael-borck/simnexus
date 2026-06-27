import pytest
from sim_lab.core import SimulatorRegistry
from sim_lab.core.agent_based_simulation import Agent


class MajorityFlipAgent(Agent):
    """A tiny agent whose boolean 'active' state flips to the neighbor majority.

    The simulation's default ``calculate_metrics`` records ``state_key_value``
    counts, so with a boolean ``active`` state each step's metrics contain
    ``active_True`` / ``active_False`` entries.
    """

    def update(self, environment, neighbors):
        if not neighbors:
            return  # No neighbors: keep current state.

        active_neighbors = sum(1 for n in neighbors if n.state.get("active", False))
        majority_active = active_neighbors > len(neighbors) / 2
        self.state = {"active": majority_active}


def _make_factory(initial_active_ids):
    """Return an agent_factory that activates the agents whose id is in the set."""
    def factory(agent_id: int) -> Agent:
        return MajorityFlipAgent(
            agent_id=agent_id,
            initial_state={"active": agent_id in initial_active_ids},
            position=(float(agent_id), 0.0),  # evenly spaced on a line
        )
    return factory


def test_initialization():
    """Test initialization of the AgentBasedSimulation class."""
    sim = SimulatorRegistry.create(
        "AgentBased",
        agent_factory=_make_factory({0, 1}),
        num_agents=5,
        days=10,
        neighborhood_radius=1.5,
        random_seed=42,
    )
    assert sim.days == 10
    assert sim.neighborhood_radius == pytest.approx(1.5)
    assert sim.random_seed == 42
    assert sim.save_history is False
    assert len(sim.agents) == 5
    # Agents were created by the factory with the expected positions/states.
    assert sim.agents[0].position == (0.0, 0.0)
    assert sim.agents[0].state == {"active": True}
    assert sim.agents[4].state == {"active": False}


def test_run_simulation_output_length():
    """Test that run_simulation returns one metrics entry per day."""
    sim = SimulatorRegistry.create(
        "AgentBased",
        agent_factory=_make_factory({0, 2}),
        num_agents=5,
        days=12,
        random_seed=42,
    )
    metrics = sim.run_simulation()
    assert len(metrics) == 12
    assert all(isinstance(entry, dict) for entry in metrics)


def test_run_simulation_reproducibility():
    """Test that the simulation is reproducible with the same random seed."""
    sim1 = SimulatorRegistry.create(
        "AgentBased",
        agent_factory=_make_factory({0, 1, 2}),
        num_agents=6,
        days=10,
        random_seed=42,
    )
    sim2 = SimulatorRegistry.create(
        "AgentBased",
        agent_factory=_make_factory({0, 1, 2}),
        num_agents=6,
        days=10,
        random_seed=42,
    )
    metrics1 = sim1.run_simulation()
    metrics2 = sim2.run_simulation()
    assert metrics1 == metrics2


def test_save_history_populates_agent_and_environment_history():
    """With save_history=True, agent and environment history grow one entry per day."""
    sim = SimulatorRegistry.create(
        "AgentBased",
        agent_factory=_make_factory({0, 1, 2}),
        num_agents=5,
        days=8,
        save_history=True,
        random_seed=42,
    )
    sim.run_simulation()
    # Initial snapshot + one per update step == days entries.
    for agent in sim.agents:
        assert len(agent.history) == 8
    assert len(sim.get_environment_history()) == 8


def test_base_simulation_methods():
    """Test methods inherited from BaseSimulation."""
    sim = SimulatorRegistry.create(
        "AgentBased",
        agent_factory=_make_factory({0, 1}),
        num_agents=5,
        days=10,
        random_seed=42,
    )

    # Test reset leaves the simulation reusable.
    sim.run_simulation()
    sim.reset()
    assert sim.metrics == []
    result = sim.run_simulation()
    assert len(result) == 10  # reusable after reset

    # Test get_parameters_info returns a dict with the expected keys.
    params = sim.get_parameters_info()
    assert isinstance(params, dict)
    assert "days" in params
    assert "random_seed" in params
    assert "agent_factory" in params
    assert "num_agents" in params
    assert "neighborhood_radius" in params
    assert "save_history" in params
