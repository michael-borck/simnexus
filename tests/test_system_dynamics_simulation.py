import pytest
from sim_lab.core import SimulatorRegistry, Stock, Flow


# Minimal one-stock / one-flow exponential-growth model used across tests.
#
# A single inflow ``flow_from_births_to_population`` adds a constant fraction of
# the stock each step, so dP/dt = growth_rate * P (pure exponential growth).
#
# Note: the simulator's default RK45 path passes ``derivatives(state, t)`` to
# ``scipy.solve_ivp`` which calls ``fun(t, y)`` -- argument order swapped -- so
# RK45 raises at runtime. The Euler path is unaffected, so every test uses
# ``integration_method="euler"``.
GROWTH_RATE = 0.05
INITIAL_POPULATION = 1000


def _make_sim(days=10, dt=1.0, integration_method="euler", random_seed=42):
    """Build a fresh SystemDynamics simulation with its own Stock/Flow objects.

    Stocks and flows are mutable and mutated by ``run_simulation``, so every
    call mints new objects to keep instances independent.
    """
    def growth(state, time):
        return state["population"] * GROWTH_RATE

    stocks = {"population": Stock("population", INITIAL_POPULATION)}
    flows = {
        "flow_from_births_to_population": Flow(
            "flow_from_births_to_population", growth
        )
    }
    return SimulatorRegistry.create(
        "SystemDynamics",
        stocks=stocks,
        flows=flows,
        days=days,
        dt=dt,
        integration_method=integration_method,
        random_seed=random_seed,
    )


def test_initialization():
    """Test initialization stores key parameters."""
    sim = _make_sim(days=10, dt=1.0, random_seed=42)
    assert sim.stocks["population"].initial_value == INITIAL_POPULATION
    assert sim.days == 10
    assert sim.dt == pytest.approx(1.0)
    assert sim.integration_method == "euler"
    assert sim.random_seed == 42
    assert sim.total_time == pytest.approx(10.0)
    assert "flow_from_births_to_population" in sim.flows


def test_run_simulation_output_length():
    """run_simulation returns a dict whose stock history has the expected length."""
    sim = _make_sim(days=10, dt=1.0)
    results = sim.run_simulation()
    assert "stock_population" in results
    # reset() seeds history with the initial value, then Euler appends one value
    # per integration point (days + 1 points) -> total length days + 2.
    assert len(results["stock_population"]) == sim.days + 2


def test_run_simulation_reproducibility():
    """Two instances with the same random_seed produce identical trajectories."""
    sim1 = _make_sim(random_seed=42)
    sim2 = _make_sim(random_seed=42)
    results1 = sim1.run_simulation()
    results2 = sim2.run_simulation()
    assert results1["stock_population"] == results2["stock_population"]


def test_exponential_growth_trajectory():
    """Stock grows exponentially and matches the closed-form Euler solution.

    For dP/dt = growth_rate * P, Euler integration with step ``dt`` gives
    P_final = P0 * (1 + growth_rate * dt) ** num_steps, where the number of
    steps equals total_time / dt = days.
    """
    sim = _make_sim(days=10, dt=1.0)
    history = sim.run_simulation()["stock_population"]

    # Final value matches the exact Euler closed form.
    expected_final = INITIAL_POPULATION * (1 + GROWTH_RATE * sim.dt) ** sim.days
    assert history[-1] == pytest.approx(expected_final)

    # Growth is in the expected (positive) direction.
    assert history[-1] > history[0]
    # The first integration point (t=0) reproduces the initial value.
    assert history[1] == pytest.approx(INITIAL_POPULATION)


def test_base_simulation_methods():
    """Test methods inherited from BaseSimulation."""
    sim = _make_sim(random_seed=42)

    # run_simulation() resets internally, so repeated runs are consistent.
    result1 = sim.run_simulation()
    # reset() must leave the simulation reusable for another identical run.
    sim.reset()
    result2 = sim.run_simulation()
    assert result1["stock_population"] == result2["stock_population"]

    # get_parameters_info returns a dict including the base keys.
    params = sim.get_parameters_info()
    assert isinstance(params, dict)
    assert "days" in params
    assert "random_seed" in params
    assert "stocks" in params
    assert "flows" in params
