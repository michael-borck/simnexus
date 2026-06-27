import pytest

from sim_lab.core import create_decay_model


def test_initialization():
    """Test initialization of the GillespieSSASimulation via the decay model factory."""
    sim = create_decay_model(a0=100, rate=0.2, max_time=30, random_seed=42)
    assert sim.species_names == ["A", "B"]
    assert sim.initial_counts == [100, 0]
    assert sim.max_time == pytest.approx(30.0)
    assert sim.random_seed == 42
    assert len(sim.reactions) == 1
    assert sim.reactions[0].stoichiometry == [-1, 1]
    assert sim.reactions[0].name == "decay"


def test_run_simulation_output_length():
    """Test that run_simulation returns a non-empty trajectory with matching times."""
    sim = create_decay_model(a0=100, rate=0.2, max_time=30, random_seed=42)
    trajectory = sim.run_simulation()
    assert len(trajectory) > 1  # initial snapshot plus at least one event
    assert len(trajectory) == len(sim.get_times())


def test_run_simulation_reproducibility():
    """Test that the SSA trajectory is reproducible with the same random seed."""
    sim1 = create_decay_model(a0=100, rate=0.2, max_time=30, random_seed=42)
    sim2 = create_decay_model(a0=100, rate=0.2, max_time=30, random_seed=42)
    traj1 = sim1.run_simulation()
    traj2 = sim2.run_simulation()
    assert traj1 == traj2
    assert sim1.get_times() == sim2.get_times()


def test_decay_dynamics_invariants():
    """Domain-specific invariants for the first-order decay A -> B."""
    sim = create_decay_model(a0=100, rate=0.2, max_time=30, random_seed=42)
    trajectory = sim.run_simulation()

    # Trajectory is non-empty.
    assert len(trajectory) > 0

    # Mass conservation: at every snapshot A + B == 100 (exact integer invariant).
    for snapshot in trajectory:
        assert sum(snapshot) == 100

    # Species A is non-increasing over the run (decay only consumes A).
    a_counts = sim.get_species("A")
    for prev, curr in zip(a_counts, a_counts[1:]):
        assert curr <= prev

    # Event times are strictly increasing and the first snapshot is at t = 0.0.
    times = sim.get_times()
    assert times[0] == pytest.approx(0.0)
    for prev, curr in zip(times, times[1:]):
        assert curr > prev

    # Summary statistics expose the expected keys.
    stats = sim.get_statistics()
    assert set(stats.keys()) == {"events", "final_time", "A", "B"}


def test_base_simulation_methods():
    """Test methods inherited from BaseSimulation."""
    sim = create_decay_model(a0=100, rate=0.2, max_time=30, random_seed=42)

    # Test reset method: re-running after reset reproduces the first run.
    first = sim.run_simulation()
    rerun_no_reset = sim.run_simulation()
    sim.reset()
    after_reset = sim.run_simulation()

    assert first == rerun_no_reset  # run_simulation itself calls reset
    assert first == after_reset     # explicit reset is reusable

    # Test get_parameters_info
    params = sim.get_parameters_info()
    assert isinstance(params, dict)
    assert "days" in params
    assert "random_seed" in params
