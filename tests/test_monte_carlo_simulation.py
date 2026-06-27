import math

import numpy as np
import pytest

from sim_lab.core import SimulatorRegistry


# ---------------------------------------------------------------------------
# Pi-estimation demo: sample a point uniformly in [0,1]^2 and score 1.0 if it
# lands inside the unit quarter-circle. The expected value of that score is
# pi/4, so the running mean converges to pi/4. The sampling uses np.random,
# which BaseSimulation re-seeds on reset()/run_simulation() -- hence identical
# results across instances sharing the same random_seed.
# ---------------------------------------------------------------------------


def _pi_sample():
    """Generate a random (x, y) point uniformly in the unit square [0, 1]^2."""
    return (np.random.random(), np.random.random())


def _pi_evaluate(point):
    """Score a point 1.0 if inside the unit quarter-circle, else 0.0."""
    x, y = point
    return 1.0 if x * x + y * y <= 1.0 else 0.0


def test_initialization():
    """Test initialization of the MonteCarloSimulation class."""
    sim = SimulatorRegistry.create(
        "MonteCarlo",
        sample_function=_pi_sample,
        evaluation_function=_pi_evaluate,
        num_samples=2000,
        days=5,
        random_seed=42,
    )
    assert sim.sample_function is _pi_sample
    assert sim.evaluation_function is _pi_evaluate
    assert sim.num_samples == 2000
    assert sim.days == 5
    assert sim.confidence_interval is True
    assert sim.random_seed == 42


def test_run_simulation_output_length():
    """Test that run_simulation returns one mean per simulated day."""
    sim = SimulatorRegistry.create(
        "MonteCarlo",
        sample_function=_pi_sample,
        evaluation_function=_pi_evaluate,
        num_samples=2000,
        days=5,
        random_seed=42,
    )
    results = sim.run_simulation()
    assert isinstance(results, list)
    assert len(results) == 5


def test_run_simulation_reproducibility():
    """Test that two instances with the same seed produce identical results."""
    sim1 = SimulatorRegistry.create(
        "MonteCarlo",
        sample_function=_pi_sample,
        evaluation_function=_pi_evaluate,
        num_samples=2000,
        days=5,
        random_seed=42,
    )
    sim2 = SimulatorRegistry.create(
        "MonteCarlo",
        sample_function=_pi_sample,
        evaluation_function=_pi_evaluate,
        num_samples=2000,
        days=5,
        random_seed=42,
    )
    results1 = sim1.run_simulation()
    results2 = sim2.run_simulation()
    assert results1 == results2


def test_pi_estimation_and_statistics():
    """Domain test: the mean score converges to pi/4 (~0.7854).

    Also verifies get_statistics() returns a dict carrying a 'mean' key.
    """
    sim = SimulatorRegistry.create(
        "MonteCarlo",
        sample_function=_pi_sample,
        evaluation_function=_pi_evaluate,
        num_samples=2000,
        days=5,
        random_seed=42,
    )
    sim.run_simulation()

    # get_statistics must report a 'mean' key.
    stats = sim.get_statistics()
    assert isinstance(stats, dict)
    assert "mean" in stats

    # The overall mean over all samples should approximate pi/4.
    assert stats["mean"] == pytest.approx(math.pi / 4, abs=0.05)


def test_base_simulation_methods():
    """Test reset() reusability and get_parameters_info() key presence."""
    sim = SimulatorRegistry.create(
        "MonteCarlo",
        sample_function=_pi_sample,
        evaluation_function=_pi_evaluate,
        num_samples=2000,
        days=5,
        random_seed=42,
    )

    sim.run_simulation()          # run once
    result1 = sim.run_simulation()  # run again without reset

    sim.reset()                  # reset state
    result2 = sim.run_simulation()  # run after reset

    assert result1 == result2  # identical results after reset

    params = sim.get_parameters_info()
    assert isinstance(params, dict)
    assert "days" in params
    assert "random_seed" in params


def test_confidence_interval_disabled_raises():
    """When confidence_interval=False, get_confidence_intervals() must raise."""
    sim = SimulatorRegistry.create(
        "MonteCarlo",
        sample_function=_pi_sample,
        evaluation_function=_pi_evaluate,
        num_samples=2000,
        days=5,
        confidence_interval=False,
        random_seed=42,
    )
    sim.run_simulation()
    with pytest.raises(ValueError):
        sim.get_confidence_intervals()
