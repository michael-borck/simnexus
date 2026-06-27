import numpy as np
import pytest

from sim_lab.core import SimulatorRegistry


# A simple 2-state chain reused across tests: [[0.9, 0.1], [0.5, 0.5]].
# Its stationary distribution is analytically [5/6, 1/6] ~= [0.8333, 0.1667].
SIMPLE_MATRIX = np.array([[0.9, 0.1], [0.5, 0.5]])
SIMPLE_STATES = ["A", "B"]


def test_initialization():
    """Test initialization of the MarkovChainSimulation class."""
    sim = SimulatorRegistry.create(
        "MarkovChain",
        transition_matrix=SIMPLE_MATRIX,
        states=SIMPLE_STATES,
        initial_state=0,
        days=20,
        random_seed=42,
    )
    assert sim.days == 20
    assert sim.random_seed == 42
    assert sim.initial_state == 0
    assert sim.current_state == 0
    assert sim.num_states == 2
    assert sim.states == SIMPLE_STATES
    assert np.allclose(sim.transition_matrix, SIMPLE_MATRIX)


def test_run_simulation_output_length():
    """Test that run_simulation returns a state history of the expected length."""
    sim = SimulatorRegistry.create(
        "MarkovChain",
        transition_matrix=SIMPLE_MATRIX,
        states=SIMPLE_STATES,
        initial_state=0,
        days=20,
        random_seed=42,
    )
    history = sim.run_simulation()
    # run_simulation seeds history with the initial state then takes days-1 steps.
    assert isinstance(history, list)
    assert len(history) == 20
    # First entry is always the initial state.
    assert history[0] == 0


def test_run_simulation_reproducibility():
    """Test that the same random_seed yields identical state histories."""
    sim1 = SimulatorRegistry.create(
        "MarkovChain",
        transition_matrix=SIMPLE_MATRIX,
        states=SIMPLE_STATES,
        initial_state=0,
        days=50,
        random_seed=42,
    )
    sim2 = SimulatorRegistry.create(
        "MarkovChain",
        transition_matrix=SIMPLE_MATRIX,
        states=SIMPLE_STATES,
        initial_state=0,
        days=50,
        random_seed=42,
    )
    history1 = sim1.run_simulation()
    history2 = sim2.run_simulation()
    assert history1 == history2


def test_empirical_distribution_approximates_stationary():
    """Over a long run the empirical state distribution approximates the stationary one.

    For the chain [[0.9, 0.1], [0.5, 0.5]] the stationary distribution solves
    pi = pi @ P, giving pi = [5/6, 1/6] ~= [0.8333, 0.1667].
    """
    sim = SimulatorRegistry.create(
        "MarkovChain",
        transition_matrix=SIMPLE_MATRIX,
        states=SIMPLE_STATES,
        initial_state=0,
        days=3000,
        random_seed=42,
    )
    sim.run_simulation()

    # The analytic stationary distribution for this chain.
    expected_stationary = np.array([5.0 / 6.0, 1.0 / 6.0])
    # The simulator's own eigenvector-based computation should match the analytic value.
    computed_stationary = sim.compute_stationary_distribution()
    assert np.allclose(computed_stationary, expected_stationary, atol=1e-6)

    # The empirical long-run distribution should converge to the stationary one.
    distribution = sim.get_state_distribution()
    assert set(distribution.keys()) == {"A", "B"}
    empirical = np.array([distribution["A"], distribution["B"]])
    assert empirical == pytest.approx(expected_stationary, abs=0.04)


def test_base_simulation_methods():
    """Test methods inherited from BaseSimulation."""
    sim = SimulatorRegistry.create(
        "MarkovChain",
        transition_matrix=SIMPLE_MATRIX,
        states=SIMPLE_STATES,
        initial_state=0,
        days=20,
        random_seed=42,
    )

    # Test reset method leaves the simulation reusable: running after reset
    # reproduces the same history (reset re-seeds RNG and clears history).
    result1 = sim.run_simulation()
    sim.reset()
    result2 = sim.run_simulation()
    assert result1 == result2

    # After reset the history should be seeded with just the initial state.
    sim.reset()
    assert sim.state_history == [sim.initial_state]
    assert sim.current_state == sim.initial_state

    # Test get_parameters_info
    params = sim.get_parameters_info()
    assert isinstance(params, dict)
    assert "days" in params
    assert "random_seed" in params
