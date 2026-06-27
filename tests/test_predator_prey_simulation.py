import pytest
from sim_lab.core import SimulatorRegistry


def test_initialization():
    """Test initialization of the PredatorPreySimulation class."""
    sim = SimulatorRegistry.create(
        "PredatorPrey",
        initial_prey=40.0,
        initial_predators=9.0,
        prey_growth_rate=0.1,
        predation_rate=0.02,
        predator_death_rate=0.1,
        predator_growth_factor=0.01,
        days=100,
        dt=0.1,
        random_seed=42,
    )
    assert sim.initial_prey == 40.0
    assert sim.initial_predators == 9.0
    assert sim.prey_growth_rate == 0.1
    assert sim.predation_rate == 0.02
    assert sim.predator_death_rate == 0.1
    assert sim.predator_growth_factor == 0.01
    assert sim.days == 100
    assert sim.dt == 0.1
    assert sim.random_seed == 42
    assert sim.prey_population == 40.0
    assert sim.predator_population == 9.0


def test_run_simulation_output_length():
    """Test that the simulation returns prey/predator histories of the expected length."""
    sim = SimulatorRegistry.create(
        "PredatorPrey",
        initial_prey=40.0,
        initial_predators=9.0,
        prey_growth_rate=0.1,
        predation_rate=0.02,
        predator_death_rate=0.1,
        predator_growth_factor=0.01,
        days=100,
        dt=0.1,
        random_seed=42,
    )
    result = sim.run_simulation()
    assert set(result.keys()) == {"prey", "predators"}
    assert len(result["prey"]) == 100
    assert len(result["predators"]) == 100


def test_run_simulation_reproducibility():
    """Test that the simulation results are reproducible with the same random seed."""
    kwargs = dict(
        initial_prey=40.0,
        initial_predators=9.0,
        prey_growth_rate=0.1,
        predation_rate=0.02,
        predator_death_rate=0.1,
        predator_growth_factor=0.01,
        days=100,
        dt=0.1,
        random_seed=42,
    )
    sim1 = SimulatorRegistry.create("PredatorPrey", **kwargs)
    sim2 = SimulatorRegistry.create("PredatorPrey", **kwargs)
    result1 = sim1.run_simulation()
    result2 = sim2.run_simulation()
    assert result1["prey"] == result2["prey"]
    assert result1["predators"] == result2["predators"]


def test_populations_stay_positive_and_oscillate():
    """Prey and predator populations stay positive and prey oscillates (max > mean > min)."""
    sim = SimulatorRegistry.create(
        "PredatorPrey",
        initial_prey=40.0,
        initial_predators=9.0,
        prey_growth_rate=0.1,
        predation_rate=0.02,
        predator_death_rate=0.1,
        predator_growth_factor=0.01,
        days=200,
        dt=0.05,
        random_seed=42,
    )
    result = sim.run_simulation()

    prey = result["prey"]
    predators = result["predators"]

    # Both populations remain strictly positive across the whole run.
    assert min(prey) > 0
    assert min(predators) > 0

    # The Lotka-Volterra dynamics produce oscillations, so the prey series
    # should sweep from a minimum through its mean up to a maximum.
    prey_max = max(prey)
    prey_min = min(prey)
    prey_mean = sum(prey) / len(prey)
    assert prey_max > prey_mean
    assert prey_mean > prey_min
    assert prey_max > prey_min


def test_base_simulation_methods():
    """Test methods inherited from BaseSimulation."""
    sim = SimulatorRegistry.create(
        "PredatorPrey",
        initial_prey=40.0,
        initial_predators=9.0,
        prey_growth_rate=0.1,
        predation_rate=0.02,
        predator_death_rate=0.1,
        predator_growth_factor=0.01,
        days=100,
        dt=0.1,
        random_seed=42,
    )
    # reset() leaves the simulation reusable.
    sim.run_simulation()
    sim.reset()
    assert sim.prey_population == sim.initial_prey
    assert sim.predator_population == sim.initial_predators
    assert sim.prey_history == [sim.initial_prey]
    assert sim.predator_history == [sim.initial_predators]

    result_after_reset = sim.run_simulation()
    assert len(result_after_reset["prey"]) == 100

    params = sim.get_parameters_info()
    assert isinstance(params, dict)
    assert "days" in params
    assert "random_seed" in params
