import pytest
from sim_lab.core import SimulatorRegistry


def test_initialization():
    """Test initialization of the EpidemiologicalSimulation class."""
    sim = SimulatorRegistry.create(
        "Epidemiological",
        population_size=1000,
        initial_infected=10,
        initial_recovered=0,
        beta=0.3,
        gamma=0.1,
        days=100,
        random_seed=42,
    )
    assert sim.population_size == 1000
    assert sim.initial_infected == 10
    assert sim.initial_recovered == 0
    assert sim.beta == 0.3
    assert sim.gamma == 0.1
    assert sim.days == 100
    assert sim.random_seed == 42
    # Derived initial susceptible is population minus infected and recovered.
    assert sim.initial_susceptible == 990


def test_run_simulation_output_length():
    """Test that the simulation returns the correct number of infected-day points."""
    sim = SimulatorRegistry.create(
        "Epidemiological",
        population_size=1000,
        initial_infected=10,
        beta=0.3,
        gamma=0.1,
        days=100,
        random_seed=42,
    )
    infected = sim.run_simulation()
    assert isinstance(infected, list)
    assert len(infected) == 100


def test_run_simulation_reproducibility():
    """Test that two simulations with the same seed produce identical results."""
    sim1 = SimulatorRegistry.create(
        "Epidemiological",
        population_size=1000,
        initial_infected=10,
        beta=0.3,
        gamma=0.1,
        days=100,
        random_seed=42,
    )
    sim2 = SimulatorRegistry.create(
        "Epidemiological",
        population_size=1000,
        initial_infected=10,
        beta=0.3,
        gamma=0.1,
        days=100,
        random_seed=42,
    )
    infected1 = sim1.run_simulation()
    infected2 = sim2.run_simulation()
    assert infected1 == infected2


def test_population_conservation():
    """The total population (S + I + R) is conserved across the whole run."""
    sim = SimulatorRegistry.create(
        "Epidemiological",
        population_size=1000,
        initial_infected=10,
        beta=0.3,
        gamma=0.1,
        days=100,
        random_seed=42,
    )
    sim.run_simulation()
    compartments = sim.get_compartments()
    s = compartments["susceptible"]
    i = compartments["infected"]
    r = compartments["recovered"]

    assert len(s) == len(i) == len(r) == 100

    initial_total = s[0] + i[0] + r[0]
    assert initial_total == pytest.approx(1000)

    # Population is conserved at every day-step within floating-point tolerance.
    for s_t, i_t, r_t in zip(s, i, r):
        assert s_t + i_t + r_t == pytest.approx(initial_total, rel=1e-6)


def test_infection_peaks_then_declines():
    """With a high transmission rate, infections rise to a peak then decline."""
    sim = SimulatorRegistry.create(
        "Epidemiological",
        population_size=1000,
        initial_infected=10,
        beta=0.5,
        gamma=0.1,
        days=150,
        random_seed=42,
    )
    infected = sim.run_simulation()

    # R0 = beta / gamma = 5.0 > 1, so an epidemic that peaks and then declines.
    assert sim.get_reproduction_number() == pytest.approx(5.0)
    peak_day, peak_value = sim.get_peak_infection()
    assert peak_value > infected[0]  # the outbreak grows from the seed
    assert peak_value > infected[-1]  # and falls below its peak
    assert peak_day > 0  # peak is not the initial day


def test_base_simulation_methods():
    """Test methods inherited from BaseSimulation."""
    sim = SimulatorRegistry.create(
        "Epidemiological",
        population_size=1000,
        initial_infected=10,
        beta=0.3,
        gamma=0.1,
        days=100,
        random_seed=42,
    )

    # reset() should leave the simulator reusable and reproducible.
    result_before = sim.run_simulation()
    sim.reset()
    result_after = sim.run_simulation()
    assert result_before == result_after

    # get_parameters_info returns a dict with the expected keys.
    params = sim.get_parameters_info()
    assert isinstance(params, dict)
    assert "days" in params
    assert "random_seed" in params
