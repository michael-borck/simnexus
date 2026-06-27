import numpy as np
import pytest

from sim_lab.core import SimulatorRegistry

# Cell states in the Drossel-Schwabl forest fire model.
EMPTY = 0
TREE = 1
BURNING = 2


def test_initialization():
    """Test initialization of the ForestFireSimulation class."""
    sim = SimulatorRegistry.create(
        "ForestFire",
        grid_size=(12, 12),
        p=1e-4,
        g=1e-2,
        days=10,
        random_seed=42,
    )
    assert sim.grid_size == (12, 12)
    assert sim.p == pytest.approx(1e-4)
    assert sim.g == pytest.approx(1e-2)
    assert sim.days == 10
    assert sim.random_seed == 42
    assert sim.boundary == "periodic"


def test_run_simulation_output_length():
    """Test that the simulation returns one tree count per generation."""
    sim = SimulatorRegistry.create(
        "ForestFire",
        grid_size=(12, 12),
        days=10,
        random_seed=42,
    )
    trees = sim.run_simulation()
    assert len(trees) == sim.days


def test_run_simulation_reproducibility():
    """Test that the simulation results are reproducible with the same random seed."""
    sim1 = SimulatorRegistry.create(
        "ForestFire",
        grid_size=(12, 12),
        days=10,
        random_seed=42,
    )
    sim2 = SimulatorRegistry.create(
        "ForestFire",
        grid_size=(12, 12),
        days=10,
        random_seed=42,
    )
    trees1 = sim1.run_simulation()
    trees2 = sim2.run_simulation()
    assert trees1 == trees2


def test_no_fire_without_ignition():
    """With p=0.0 and no initial burning cells, fires never start.

    Spontaneous ignition is impossible (lightning probability zero) and there
    are no burning neighbours to spread the fire, so every entry of the fire
    history must be zero, and the run still produces one sample per day.
    """
    sim = SimulatorRegistry.create(
        "ForestFire",
        grid_size=(12, 12),
        initial_density=0.5,
        p=0.0,
        g=0.0,
        days=10,
        random_seed=42,
    )
    # Sanity: the random initial grid contains only empty/tree cells.
    assert sim.initial_state.max() == TREE

    trees = sim.run_simulation()
    assert len(trees) == sim.days
    assert max(sim.fire_history) == 0


def test_fire_spreads_from_burning_cell():
    """With p=0.0 but one burning cell present, the fire spreads to adjacent trees.

    With lightning disabled, ignition can only come from a burning neighbour.
    Starting from a fully forested grid with a single burning cell at the
    centre, the eight neighbouring trees ignite in the next generation, so the
    tree count must strictly decrease.
    """
    grid = np.full((12, 12), TREE, dtype=int)
    grid[5, 5] = BURNING

    sim = SimulatorRegistry.create(
        "ForestFire",
        grid_size=(12, 12),
        initial_state=grid,
        p=0.0,
        g=0.0,
        days=10,
        random_seed=42,
    )
    trees = sim.run_simulation()

    trees_before = trees[0]
    trees_after = trees[1]
    # Fire spread: neighbours ignited in the next generation.
    assert sim.fire_history[1] > 0
    assert trees_after < trees_before


def test_get_statistics():
    """Test that get_statistics returns the expected summary keys."""
    sim = SimulatorRegistry.create(
        "ForestFire",
        grid_size=(12, 12),
        days=10,
        random_seed=42,
    )
    sim.run_simulation()
    stats = sim.get_statistics()

    assert isinstance(stats, dict)
    assert "mean_trees" in stats
    assert "max_fires" in stats
    assert isinstance(stats["mean_trees"], float)
    assert isinstance(stats["max_fires"], float)
    assert stats["mean_trees"] >= 0.0
    assert stats["max_fires"] >= 0.0


def test_base_simulation_methods():
    """Test methods inherited from BaseSimulation."""
    sim = SimulatorRegistry.create(
        "ForestFire",
        grid_size=(12, 12),
        days=10,
        random_seed=42,
    )

    # Test reset method: running again after reset reproduces the run.
    result1 = sim.run_simulation()
    sim.reset()
    result2 = sim.run_simulation()
    assert result1 == result2

    # Test get_parameters_info
    params = sim.get_parameters_info()
    assert isinstance(params, dict)
    assert "days" in params
    assert "random_seed" in params
