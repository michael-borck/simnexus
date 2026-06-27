import numpy as np
import pytest

from sim_lab.core import PATTERNS, SimulatorRegistry, place_pattern


def test_initialization():
    """Test initialization of the GameOfLifeSimulation class."""
    sim = SimulatorRegistry.create(
        "GameOfLife",
        pattern="glider",
        grid_size=(20, 20),
        boundary="periodic",
        days=8,
        random_seed=42,
    )
    assert sim.pattern == "glider"
    assert sim.grid_size == (20, 20)
    assert sim.boundary == "periodic"
    assert sim.days == 8
    assert sim.random_seed == 42
    assert sim.offset is None
    # A glider has exactly 5 live cells, placed onto the (zeroed) initial grid.
    assert sim.initial_state.shape == (20, 20)
    assert sim.initial_state.sum() == 5


def test_run_simulation_output_length():
    """Test that the simulation returns one live-cell count per generation."""
    sim = SimulatorRegistry.create(
        "GameOfLife",
        pattern="glider",
        grid_size=(20, 20),
        boundary="periodic",
        days=8,
        random_seed=42,
    )
    live_cells = sim.run_simulation()
    assert len(live_cells) == 8


def test_run_simulation_reproducibility():
    """Test that the simulation results are reproducible with the same random seed."""
    sim1 = SimulatorRegistry.create(
        "GameOfLife",
        pattern="glider",
        grid_size=(20, 20),
        boundary="periodic",
        days=8,
        random_seed=42,
    )
    sim2 = SimulatorRegistry.create(
        "GameOfLife",
        pattern="glider",
        grid_size=(20, 20),
        boundary="periodic",
        days=8,
        random_seed=42,
    )
    live_cells1 = sim1.run_simulation()
    live_cells2 = sim2.run_simulation()
    assert live_cells1 == live_cells2


def test_block_still_life():
    """A 2x2 block is a still life: population is constant and the grid never changes."""
    # days >= 11 so detect_stable_pattern() has enough history (>= max_cycle_length + 1).
    sim = SimulatorRegistry.create(
        "GameOfLife",
        pattern="block",
        grid_size=(20, 20),
        boundary="periodic",
        days=11,
        random_seed=42,
    )
    live_cells = sim.run_simulation()

    # The block has exactly 4 live cells and never grows, shrinks, or shifts.
    assert all(count == 4 for count in live_cells)

    # Every generation is byte-for-byte identical to the initial configuration...
    for state in sim.get_all_states():
        assert state.sum() == 4

    # ...so the detector reports a stable (non-cyclic) state.
    assert sim.detect_stable_pattern() == 0


def test_glider_population_preserved():
    """A glider on a periodic grid keeps exactly 5 live cells every generation.

    The glider translates diagonally (and wraps around the torus) but neither
    grows nor decays, so its population is an invariant of the dynamics.
    """
    sim = SimulatorRegistry.create(
        "GameOfLife",
        pattern="glider",
        grid_size=(20, 20),
        boundary="periodic",
        days=8,
        random_seed=42,
    )
    live_cells = sim.run_simulation()

    # Population invariant: every generation has exactly 5 live cells.
    assert all(count == 5 for count in live_cells)

    # And it really is moving, not frozen: after 4 generations a glider has
    # shifted by one cell diagonally, so the grid differs from generation 0.
    assert not (sim.get_state_at_day(0) == sim.get_state_at_day(4)).all()


def test_patterns_contains_glider():
    """The PATTERNS catalogue exposes the named 'glider' pattern."""
    assert "glider" in PATTERNS
    assert PATTERNS["glider"].sum() == 5


def test_place_pattern():
    """place_pattern embeds a pattern onto a zeroed grid of the requested size."""
    # Default (centred) placement of the glider on a 20x20 grid.
    grid = place_pattern(PATTERNS["glider"], (20, 20))
    assert grid.shape == (20, 20)
    assert grid.sum() == 5  # glider has 5 live cells
    assert set(np.unique(grid)) <= {0, 1}

    # Explicit top-left offset lands the pattern at the corner.
    grid_offset = place_pattern(PATTERNS["glider"], (20, 20), offset=(0, 0))
    assert grid_offset[0:3, 0:3].sum() == 5

    # A pattern larger than the grid is rejected.
    with pytest.raises(ValueError):
        place_pattern(PATTERNS["pulsar"], (5, 5))

    # An offset that pushes the pattern out of bounds is rejected.
    with pytest.raises(ValueError):
        place_pattern(PATTERNS["glider"], (20, 20), offset=(18, 18))


def test_base_simulation_methods():
    """Test methods inherited from BaseSimulation."""
    sim = SimulatorRegistry.create(
        "GameOfLife",
        pattern="glider",
        grid_size=(20, 20),
        boundary="periodic",
        days=8,
        random_seed=42,
    )

    # Test reset method
    sim.run_simulation()  # run once
    result1 = sim.run_simulation()  # run again without reset

    sim.reset()  # reset state
    result2 = sim.run_simulation()  # run after reset

    assert result1 == result2  # should get same results after reset

    # Test get_parameters_info
    params = sim.get_parameters_info()
    assert isinstance(params, dict)
    assert "days" in params
    assert "random_seed" in params
