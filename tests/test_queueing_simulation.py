import pytest
from sim_lab.core import SimulatorRegistry


def test_initialization():
    """Test initialization of the QueueingSimulation class."""
    sim = SimulatorRegistry.create(
        "QueueingSystem",
        max_time=100,
        arrival_rate=0.5,
        service_rate=1.0,
        num_servers=1,
        random_seed=42,
    )
    assert sim.max_time == 100
    assert sim.arrival_rate == 0.5
    assert sim.service_rate == 1.0
    assert sim.num_servers == 1
    assert sim.max_queue_length is None
    assert sim.time_step == 1.0
    assert sim.days == 100  # days == int(max_time) for base-class compatibility
    assert sim.random_seed == 42


def test_run_simulation_output_length():
    """Test that the simulation returns the correct number of queue-length samples.

    The discrete-event base records one sample per integer time step (plus the
    initial value), so for max_time=100 the series has 101 entries.
    """
    sim = SimulatorRegistry.create(
        "QueueingSystem",
        max_time=100,
        arrival_rate=0.5,
        service_rate=1.0,
        random_seed=42,
    )
    queue_lengths = sim.run_simulation()
    assert isinstance(queue_lengths, list)
    assert len(queue_lengths) == 101


def test_run_simulation_reproducibility():
    """Test that the simulation results are reproducible with the same random seed."""
    sim1 = SimulatorRegistry.create(
        "QueueingSystem",
        max_time=100,
        arrival_rate=0.5,
        service_rate=1.0,
        random_seed=42,
    )
    sim2 = SimulatorRegistry.create(
        "QueueingSystem",
        max_time=100,
        arrival_rate=0.5,
        service_rate=1.0,
        random_seed=42,
    )
    results1 = sim1.run_simulation()
    results2 = sim2.run_simulation()
    assert results1 == results2


def test_stable_mm1_invariants():
    """Stability and non-negativity invariants for a stable M/M/1 queue.

    For service_rate > arrival_rate the traffic intensity rho = lambda / mu < 1,
    so the configured system is stable. The queue length is a non-negative state
    variable (the implementation only ever increments or decrements it from an
    initial value of 0), so every recorded sample must be a non-negative real,
    and the summary statistics returned by get_statistics() must be non-negative.
    """
    arrival_rate = 0.5
    service_rate = 1.0
    rho = arrival_rate / service_rate

    sim = SimulatorRegistry.create(
        "QueueingSystem",
        max_time=500,
        arrival_rate=arrival_rate,
        service_rate=service_rate,
        num_servers=1,
        random_seed=42,
    )
    series = sim.run_simulation()
    stats = sim.get_statistics()

    # Stability condition for an M/M/1 queue: rho < 1.
    assert rho < 1.0

    # Queue length is a non-negative state variable across the whole run.
    assert len(series) > 0
    assert all(isinstance(v, (int, float)) for v in series)
    assert all(v >= 0.0 for v in series)

    # get_statistics() always returns a dict of non-negative values when present.
    assert isinstance(stats, dict)
    assert all(v >= 0.0 for v in stats.values())


def test_base_simulation_methods():
    """Test methods inherited from BaseSimulation."""
    sim = SimulatorRegistry.create(
        "QueueingSystem",
        max_time=100,
        arrival_rate=0.5,
        service_rate=1.0,
        random_seed=42,
    )

    # Test reset method leaves the simulation reusable.
    sim.run_simulation()            # run once
    result1 = sim.run_simulation()  # run again without reset
    sim.reset()                     # reset state
    result2 = sim.run_simulation()  # run after reset
    assert result1 == result2       # same results after reset

    # Test get_parameters_info.
    params = sim.get_parameters_info()
    assert isinstance(params, dict)
    # NOTE: DiscreteEventSimulation replaces the base 'days' key with 'max_time'.
    assert "max_time" in params
    assert "arrival_rate" in params
    assert "service_rate" in params
    assert "num_servers" in params
    assert "max_queue_length" in params
    assert "random_seed" in params
