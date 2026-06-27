from sim_lab.core import SimulatorRegistry


def test_initialization():
    """Test initialization of the BoidsSimulation class."""
    sim = SimulatorRegistry.create(
        "Boids",
        num_boids=30,
        width=80,
        height=80,
        days=10,
        random_seed=42,
    )
    assert sim.width == 80
    assert sim.height == 80
    assert sim.max_speed == 3.0  # default
    assert sim.days == 10
    assert sim.random_seed == 42
    # num_boids is materialized as the agent roster, never a public attribute.
    assert len(sim.agents) == 30


def test_run_simulation_output_length():
    """Test that the simulation returns one metrics dict per step."""
    sim = SimulatorRegistry.create(
        "Boids",
        num_boids=30,
        width=80,
        height=80,
        days=10,
        random_seed=42,
    )
    metrics = sim.run_simulation()
    assert isinstance(metrics, list)
    assert len(metrics) == 10  # one entry per day (initial state + days-1 steps)


def test_run_simulation_reproducibility():
    """Test that the simulation results are reproducible with the same random seed."""
    sim1 = SimulatorRegistry.create(
        "Boids",
        num_boids=30,
        width=80,
        height=80,
        days=10,
        random_seed=42,
    )
    sim2 = SimulatorRegistry.create(
        "Boids",
        num_boids=30,
        width=80,
        height=80,
        days=10,
        random_seed=42,
    )
    metrics1 = sim1.run_simulation()
    metrics2 = sim2.run_simulation()
    assert metrics1 == metrics2


def test_flock_invariants():
    """Test Reynolds-flock invariants: boid conservation and bounded speed.

    Boids are neither created nor destroyed, so every step reports the full
    roster, and because each boid's velocity is clamped to ``max_speed`` the
    flock's mean speed can never exceed it.
    """
    sim = SimulatorRegistry.create(
        "Boids",
        num_boids=30,
        width=80,
        height=80,
        days=10,
        random_seed=42,
    )
    metrics = sim.run_simulation()
    assert len(metrics) > 0
    for entry in metrics:
        assert isinstance(entry, dict)
        assert entry["num_boids"] == 30  # conservation: no births/deaths
        mean_speed = entry["mean_speed"]
        assert 0 <= mean_speed <= sim.max_speed


def test_base_simulation_methods():
    """Test methods inherited from BaseSimulation."""
    sim = SimulatorRegistry.create(
        "Boids",
        num_boids=30,
        width=80,
        height=80,
        days=10,
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
