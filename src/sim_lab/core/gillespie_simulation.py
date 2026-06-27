"""Gillespie stochastic simulation algorithm (SSA) for chemical kinetics.

Implements the original Gillespie (1977) direct method: at each step the time to
the next reaction is drawn from an exponential distribution whose rate is the
total propensity, and the firing reaction is chosen with probability proportional
to its propensity. The result is an exact realisation of the continuous-time
Markov chain defined by the reactions -- the canonical stochastic simulator for
well-mixed chemical kinetics.
"""

from typing import Any, Callable, Dict, List, Optional

import numpy as np

from .base_simulation import BaseSimulation
from .registry import SimulatorRegistry


class Reaction:
    """A single reaction in a Gillespie model.

    Attributes:
        stoichiometry (List[int]): Net change in each species' count when this
            reaction fires once (negative = consumed, positive = produced).
        propensity_function (Callable[[List[int]], float]): Returns the reaction's
            propensity given the current species counts.
        name (str): Human-readable label.
    """

    def __init__(
        self,
        stoichiometry: List[int],
        propensity_function: Callable[[List[int]], float],
        name: str = "reaction",
    ) -> None:
        """Initialize a reaction with its stoichiometry and propensity."""
        self.stoichiometry = list(stoichiometry)
        self.propensity_function = propensity_function
        self.name = name


@SimulatorRegistry.register("GillespieSSA")
class GillespieSSASimulation(BaseSimulation):
    """Exact stochastic simulation of well-mixed chemical kinetics.

    Note:
        ``days`` is repurposed here as the maximum number of reaction events (a
        safety cap); the natural time horizon is ``max_time``.

    Attributes:
        species_names (List[str]): Names of the species, defining vector order.
        initial_counts (List[int]): Initial molecule count per species.
        reactions (List[Reaction]): The reactions defining the system.
        max_time (float): Simulated time horizon.
    """

    def __init__(
        self,
        species_names: List[str],
        initial_counts: List[int],
        reactions: List[Reaction],
        max_time: float = 10.0,
        days: int = 100000,
        random_seed: Optional[int] = None,
    ) -> None:
        """Initialize the Gillespie simulation.

        Args:
            species_names: Names of the species (defines the vector ordering).
            initial_counts: Initial molecule count for each species.
            reactions: List of Reaction objects defining the system.
            max_time: Stop when simulated time reaches this horizon.
            days: Maximum number of reaction events (safety cap).
            random_seed: Seed for random number generation.
        """
        if len(species_names) != len(initial_counts):
            raise ValueError("species_names and initial_counts must have equal length")
        super().__init__(days=days, random_seed=random_seed)
        self.species_names = list(species_names)
        self.initial_counts = [int(c) for c in initial_counts]
        self.reactions = list(reactions)
        self.max_time = float(max_time)
        self._rng = np.random.RandomState(random_seed)
        self.times: List[float] = []
        self.trajectory: List[List[int]] = []

    def run_simulation(self) -> List[List[int]]:
        """Run the SSA until ``max_time`` or until no reaction can fire.

        Returns:
            A list of species-count snapshots, one per recorded event time
            (including the initial state at t = 0). Use :meth:`get_species` for a
            single-species time series and :meth:`get_times` for the event times.
        """
        self.reset()
        state = list(self.initial_counts)
        time = 0.0
        self.times = [0.0]
        self.trajectory = [list(state)]

        events = 0
        while events < self.days:
            propensities = [r.propensity_function(state) for r in self.reactions]
            a0 = float(sum(propensities))
            if a0 <= 0.0:
                break  # no reaction can fire -- absorbing state
            r1, r2 = self._rng.random(), self._rng.random()
            tau = -np.log(r1) / a0 if r1 > 0.0 else float("inf")
            if time + tau > self.max_time:
                break
            # Choose the reaction via the cumulative propensity distribution.
            threshold = r2 * a0
            cumulative = 0.0
            chosen = len(self.reactions) - 1
            for j, aj in enumerate(propensities):
                cumulative += aj
                if threshold <= cumulative:
                    chosen = j
                    break
            for i, delta in enumerate(self.reactions[chosen].stoichiometry):
                state[i] += delta
            time += tau
            self.times.append(time)
            self.trajectory.append(list(state))
            events += 1

        return self.trajectory

    def get_species(self, name: str) -> List[int]:
        """Time series of molecule counts for a single species."""
        if name not in self.species_names:
            raise ValueError(f"Unknown species '{name}'. Choose from {self.species_names}")
        idx = self.species_names.index(name)
        return [snapshot[idx] for snapshot in self.trajectory]

    def get_times(self) -> List[float]:
        """Event times (including t = 0) recorded during the run."""
        return self.times

    def get_statistics(self) -> Dict[str, float]:
        """Summary statistics for the run."""
        if not self.trajectory:
            raise ValueError("No simulation results available. Run the simulation first.")
        final = self.trajectory[-1]
        stats = {
            "events": float(len(self.trajectory) - 1),
            "final_time": float(self.times[-1]),
        }
        stats.update({name: float(count) for name, count in zip(self.species_names, final, strict=True)})
        return stats

    def reset(self) -> None:
        """Reset the simulation and reseed the random generator."""
        super().reset()
        self._rng = np.random.RandomState(self.random_seed)
        self.times = []
        self.trajectory = []

    @classmethod
    def get_parameters_info(cls) -> Dict[str, Dict[str, Any]]:
        """Get information about the parameters required by this simulation."""
        params = super().get_parameters_info()
        params["days"]["description"] = "Maximum number of reaction events (safety cap)"
        params.update({
            "species_names": {
                "type": "List[str]", "description": "Names of the chemical species", "required": True,
            },
            "initial_counts": {
                "type": "List[int]", "description": "Initial molecule count per species", "required": True,
            },
            "reactions": {
                "type": "List[Reaction]", "description": "Reactions defining the system", "required": True,
            },
            "max_time": {
                "type": "float", "description": "Simulated time horizon", "required": False, "default": 10.0,
            },
        })
        return params


def create_decay_model(
    a0: int = 100,
    rate: float = 0.1,
    max_time: float = 50.0,
    random_seed: Optional[int] = None,
) -> GillespieSSASimulation:
    """First-order irreversible decay A -> B.

    The deterministic solution is A(t) = A0 * exp(-rate * t); the SSA reproduces
    it in expectation and conserves A + B = A0 at every step -- a clean teaching
    example of exact stochastic kinetics.
    """
    species = ["A", "B"]
    counts = [a0, 0]
    reactions = [
        Reaction(stoichiometry=[-1, 1], propensity_function=lambda s: rate * s[0], name="decay"),
    ]
    return GillespieSSASimulation(
        species_names=species,
        initial_counts=counts,
        reactions=reactions,
        max_time=max_time,
        random_seed=random_seed,
    )
