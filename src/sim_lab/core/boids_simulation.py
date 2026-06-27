"""Boids flocking agent-based simulation (Reynolds, 1987).

Each boid steers itself using three local rules -- separation, alignment, and
cohesion -- evaluated against its neighbours within a perception radius. Flocking
behaviour emerges from these simple rules with no central coordinator.
"""

from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from .agent_based_simulation import Agent, AgentBasedSimulation
from .registry import SimulatorRegistry


class Boid(Agent):
    """A single bird-like agent with a position and velocity.

    Attributes:
        velocity (np.ndarray): Current (vx, vy) velocity.
        max_speed (float): Speed cap; steering cannot push a boid faster than this.
        max_force (float): Per-step cap on the steering acceleration.
    """

    def __init__(
        self,
        agent_id: int,
        position: Tuple[float, float],
        velocity: Tuple[float, float],
        width: float,
        height: float,
        max_speed: float = 3.0,
        max_force: float = 0.05,
        weight_separation: float = 1.5,
        weight_alignment: float = 1.0,
        weight_cohesion: float = 1.0,
    ) -> None:
        """Initialize a boid with a position, velocity, and steering weights."""
        super().__init__(agent_id=agent_id, position=(float(position[0]), float(position[1])))
        self.velocity = np.asarray(velocity, dtype=float)
        self.width = float(width)
        self.height = float(height)
        self.max_speed = float(max_speed)
        self.max_force = float(max_force)
        self.w_sep = float(weight_separation)
        self.w_ali = float(weight_alignment)
        self.w_coh = float(weight_cohesion)
        self.state = {"speed": float(np.linalg.norm(self.velocity))}

    @property
    def speed(self) -> float:
        """Current scalar speed."""
        return float(np.linalg.norm(self.velocity))

    def update(self, environment: Any, neighbors: List["Boid"]) -> None:
        """Apply the three Reynolds rules, integrate, and wrap around the field."""
        steering = (
            self.w_sep * self._separation(neighbors)
            + self.w_ali * self._alignment(neighbors)
            + self.w_coh * self._cohesion(neighbors)
        )
        steering = self._limit(steering, self.max_force)
        self.velocity = self._limit(self.velocity + steering, self.max_speed)

        nx = (self.position[0] + self.velocity[0]) % self.width
        ny = (self.position[1] + self.velocity[1]) % self.height
        self.move((nx, ny))
        self.state = {"speed": self.speed}

    # --- Reynolds rules --------------------------------------------------

    def _separation(self, neighbors: List["Boid"]) -> np.ndarray:
        """Steer away from nearby neighbours, weighted by inverse distance."""
        steer = np.zeros(2)
        count = 0
        for other in neighbors:
            diff = np.array(self.position) - np.array(other.position)
            dist = np.linalg.norm(diff)
            if dist > 1e-6:
                steer += diff / (dist * dist)
                count += 1
        if count:
            return self._steer_to(steer / count)
        return steer

    def _alignment(self, neighbors: List["Boid"]) -> np.ndarray:
        """Steer toward the average heading of nearby neighbours."""
        if not neighbors:
            return np.zeros(2)
        return self._steer_to(np.mean([n.velocity for n in neighbors], axis=0))

    def _cohesion(self, neighbors: List["Boid"]) -> np.ndarray:
        """Steer toward the average position of nearby neighbours."""
        if not neighbors:
            return np.zeros(2)
        center = np.mean([np.array(n.position) for n in neighbors], axis=0)
        return self._steer_to(center - np.array(self.position))

    def _steer_to(self, vector: np.ndarray) -> np.ndarray:
        """Return a bounded steering force toward ``vector``."""
        norm = np.linalg.norm(vector)
        if norm < 1e-6:
            return np.zeros(2)
        desired = vector / norm * self.max_speed
        return self._limit(desired - self.velocity, self.max_force)

    @staticmethod
    def _limit(vector: np.ndarray, maximum: float) -> np.ndarray:
        """Scale ``vector`` down so its magnitude never exceeds ``maximum``."""
        norm = np.linalg.norm(vector)
        if norm > maximum > 1e-12:
            return vector / norm * maximum
        return vector


@SimulatorRegistry.register("Boids")
class BoidsSimulation(AgentBasedSimulation):
    """Reynolds boids flocking on a toroidal 2-D field.

    Agents steer using separation, alignment, and cohesion within a perception
    radius. Each step reports the mean speed, the observed maximum speed, the
    flock centroid, and the flock's positional spread.

    Attributes:
        width (float): Field width.
        height (float): Field height.
        num_boids (int): Number of boids in the flock.
    """

    def __init__(
        self,
        num_boids: int = 100,
        width: float = 100.0,
        height: float = 100.0,
        max_speed: float = 3.0,
        max_force: float = 0.05,
        perception_radius: float = 10.0,
        weight_separation: float = 1.5,
        weight_alignment: float = 1.0,
        weight_cohesion: float = 1.0,
        days: int = 100,
        save_history: bool = False,
        random_seed: Optional[int] = None,
    ) -> None:
        """Initialize the boids flocking simulation."""
        self.width = float(width)
        self.height = float(height)
        self.max_speed = float(max_speed)
        self.max_force = float(max_force)
        self._w_sep = float(weight_separation)
        self._w_ali = float(weight_alignment)
        self._w_coh = float(weight_cohesion)
        self._num_boids = int(num_boids)
        self._rng = np.random.RandomState(random_seed)
        super().__init__(
            agent_factory=self._make_boid,
            num_agents=self._num_boids,
            days=days,
            neighborhood_radius=perception_radius,
            save_history=save_history,
            random_seed=random_seed,
        )

    def _make_boid(self, agent_id: int) -> Boid:
        """Create one boid with a random position and a unit random heading."""
        position = (self._rng.uniform(0, self.width), self._rng.uniform(0, self.height))
        velocity = self._rng.uniform(-1, 1, size=2)
        norm = np.linalg.norm(velocity)
        if norm < 1e-6:
            velocity = np.array([1.0, 0.0])
            norm = 1.0
        velocity = velocity / norm * self.max_speed
        return Boid(
            agent_id=agent_id,
            position=position,
            velocity=velocity,
            width=self.width,
            height=self.height,
            max_speed=self.max_speed,
            max_force=self.max_force,
            weight_separation=self._w_sep,
            weight_alignment=self._w_ali,
            weight_cohesion=self._w_coh,
        )

    def calculate_metrics(self) -> Dict[str, Any]:
        """Per-step flock statistics."""
        positions = np.array([a.position for a in self.agents])
        speeds = np.array([a.speed for a in self.agents])
        centroid = positions.mean(axis=0)
        return {
            "num_boids": len(self.agents),
            "mean_speed": float(speeds.mean()),
            "max_speed_observed": float(speeds.max()),
            "centroid_x": float(centroid[0]),
            "centroid_y": float(centroid[1]),
            "flock_spread": float(positions.std(axis=0).mean()),
        }

    def reset(self) -> None:
        """Reseed and rebuild the flock so re-runs are reproducible."""
        super().reset()
        self._rng = np.random.RandomState(self.random_seed)
        self.agents = [self._make_boid(i) for i in range(self._num_boids)]

    @classmethod
    def get_parameters_info(cls) -> Dict[str, Dict[str, Any]]:
        """Get information about the parameters required by this simulation."""
        params = super().get_parameters_info()
        # The generic agent-factory interface is not part of the boid API.
        params.pop("agent_factory", None)
        params.pop("num_agents", None)
        params.update({
            "num_boids": {
                "type": "int",
                "description": "Number of boids in the flock",
                "required": False,
                "default": 100,
            },
            "width": {
                "type": "float", "description": "Field width", "required": False, "default": 100.0,
            },
            "height": {
                "type": "float", "description": "Field height", "required": False, "default": 100.0,
            },
            "max_speed": {
                "type": "float", "description": "Maximum boid speed", "required": False, "default": 3.0,
            },
            "max_force": {
                "type": "float",
                "description": "Maximum steering force applied per step",
                "required": False,
                "default": 0.05,
            },
            "perception_radius": {
                "type": "float",
                "description": "Radius within which a boid sees neighbours",
                "required": False,
                "default": 10.0,
            },
            "weight_separation": {
                "type": "float", "description": "Relative weight of the separation rule",
                "required": False, "default": 1.5,
            },
            "weight_alignment": {
                "type": "float", "description": "Relative weight of the alignment rule",
                "required": False, "default": 1.0,
            },
            "weight_cohesion": {
                "type": "float", "description": "Relative weight of the cohesion rule",
                "required": False, "default": 1.0,
            },
        })
        return params
