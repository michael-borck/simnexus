import numpy as np
import pytest
from sim_lab.core import SimulatorRegistry


def test_initialization():
    """Test initialization of the CellularAutomatonSimulation class."""
    grid = np.zeros((10, 10), dtype=int)
    sim = SimulatorRegistry.create(
        "CellularAutomaton",
        grid_size=(10, 10),
        initial_state=grid,
        rule="game_of_life",
        days=10,
        boundary="periodic",
        random_seed=42,
    )
    assert sim.grid_size == (10, 10)
    assert sim.days == 10
    assert sim.boundary == "periodic"
    assert sim.random_seed == 42
    assert sim.initial_state.shape == (10, 10)
    # The 'game_of_life' string rule maps to the built-in rule method
    assert sim.update_rule == sim._game_of_life_rule


def test_run_simulation_output_length():
    """Test that run_simulation returns one live-cell count per generation."""
    sim = SimulatorRegistry.create(
        "CellularAutomaton",
        grid_size=(10, 10),
        initial_density=0.3,
        days=8,
        random_seed=42,
    )
    live_cells = sim.run_simulation()
    assert len(live_cells) == 8


def test_run_simulation_reproducibility():
    """Test that two sims with the same random_seed produce identical histories."""
    kwargs = dict(
        grid_size=(10, 10),
        initial_density=0.3,
        days=8,
        random_seed=42,
    )
    sim1 = SimulatorRegistry.create("CellularAutomaton", **kwargs)
    sim2 = SimulatorRegistry.create("CellularAutomaton", **kwargs)
    live1 = sim1.run_simulation()
    live2 = sim2.run_simulation()
    assert live1 == live2
    # The full grid histories must also match, not just the live-cell counts
    for state1, state2 in zip(sim1.get_all_states(), sim2.get_all_states()):
        assert np.array_equal(state1, state2)


def test_game_of_life_patterns():
    """Test known Game of Life invariants: still-life stability and blinker period-2."""
    # --- Still life: a 2x2 block is stable (live-cell count unchanged after 1 step) ---
    grid = np.zeros((10, 10), dtype=int)
    grid[3:5, 3:5] = 1  # 2x2 block at rows 3-4, cols 3-4
    sim = SimulatorRegistry.create(
        "CellularAutomaton",
        grid_size=(10, 10),
        initial_state=grid,
        rule="game_of_life",
        days=2,
        boundary="periodic",
        random_seed=42,
    )
    live = sim.run_simulation()
    assert live[0] == 4
    assert live[1] == 4  # block survives unchanged
    assert np.array_equal(sim.get_state_at_day(0), sim.get_state_at_day(1))

    # --- Oscillator: a horizontal blinker (3 in a row) has period 2 ---
    blinker = np.zeros((10, 10), dtype=int)
    blinker[5, 4:7] = 1  # horizontal line at (5,4),(5,5),(5,6)
    sim_b = SimulatorRegistry.create(
        "CellularAutomaton",
        grid_size=(10, 10),
        initial_state=blinker,
        rule="game_of_life",
        days=3,
        boundary="periodic",
        random_seed=42,
    )
    live_b = sim_b.run_simulation()
    # Population is conserved at 3 across the oscillation
    assert all(n == 3 for n in live_b)
    # After two generations the blinker returns to its original orientation
    assert np.array_equal(sim_b.get_state_at_day(0), sim_b.get_state_at_day(2))
    # After one generation it has changed (vertical vs horizontal)
    assert not np.array_equal(sim_b.get_state_at_day(0), sim_b.get_state_at_day(1))


def test_custom_rule():
    """Test that a custom callable rule is applied each generation."""
    def extinction_rule(grid):
        """Custom rule: every cell dies on each step."""
        return np.zeros_like(grid)

    grid = np.zeros((10, 10), dtype=int)
    grid[1:4, 1:4] = 1  # 9 live cells initially
    sim = SimulatorRegistry.create(
        "CellularAutomaton",
        grid_size=(10, 10),
        initial_state=grid,
        rule=extinction_rule,
        days=3,
        boundary="periodic",
        random_seed=42,
    )
    assert sim.update_rule is extinction_rule
    live = sim.run_simulation()
    assert live[0] == 9  # initial population
    assert live[1] == 0  # custom rule clears the grid
    assert live[2] == 0


def test_base_simulation_methods():
    """Test reset() and get_parameters_info() from BaseSimulation."""
    sim = SimulatorRegistry.create(
        "CellularAutomaton",
        grid_size=(10, 10),
        initial_density=0.3,
        days=6,
        random_seed=42,
    )
    result1 = sim.run_simulation()  # run once
    sim.reset()  # reset to initial state
    result2 = sim.run_simulation()  # run again after reset
    assert result1 == result2  # reset leaves the sim reusable and reproducible

    params = sim.get_parameters_info()
    assert isinstance(params, dict)
    assert "days" in params
    assert "random_seed" in params
    assert "grid_size" in params
    assert "boundary" in params
