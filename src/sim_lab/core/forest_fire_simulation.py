"""Forest Fire cellular automaton (Drossel & Schwabl, 1992)."""

from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from .cellular_automaton_simulation import CellularAutomatonSimulation
from .registry import SimulatorRegistry

# Cell states
EMPTY = 0
TREE = 1
BURNING = 2


@SimulatorRegistry.register("ForestFire")
class ForestFireSimulation(CellularAutomatonSimulation):
    """The Drossel-Schwabl forest fire cellular automaton.

    Each cell is empty (0), a tree (1), or burning (2). At every generation:

    1. A burning cell becomes empty.
    2. A tree ignites if a neighbour is burning, or spontaneously with
       probability ``p`` (a lightning strike).
    3. An empty cell grows a tree with probability ``g``.

    With ``p << g`` the system self-organises into a critical state exhibiting
    power-law fire-size distributions -- a textbook example of self-organised
    criticality.

    Attributes:
        p (float): Spontaneous-ignition (lightning) probability per tree per step.
        g (float): Tree-growth probability per empty cell per step.
    """

    def __init__(
        self,
        grid_size: Tuple[int, int] = (50, 50),
        initial_density: float = 0.5,
        p: float = 1e-4,
        g: float = 1e-2,
        days: int = 100,
        boundary: str = "periodic",
        initial_state: Optional[np.ndarray] = None,
        random_seed: Optional[int] = None,
    ) -> None:
        """Initialize the forest fire simulation.

        Args:
            grid_size: Dimensions of the grid as (rows, columns).
            initial_density: Initial fraction of cells that are trees (0..1).
            p: Spontaneous-ignition (lightning) probability per tree per step.
            g: Regrowth probability per empty cell per step.
            days: Number of generations to simulate.
            boundary: Boundary condition ('periodic' or 'fixed').
            initial_state: Optional initial grid with values in {0, 1, 2};
                overrides ``initial_density``.
            random_seed: Seed for random number generation.
        """
        if not 0.0 <= p <= 1.0:
            raise ValueError("p (ignition probability) must be in [0, 1]")
        if not 0.0 <= g <= 1.0:
            raise ValueError("g (growth probability) must be in [0, 1]")
        self.p = float(p)
        self.g = float(g)
        self._rng = np.random.RandomState(random_seed)
        self.tree_history: List[int] = []
        self.fire_history: List[int] = []
        super().__init__(
            grid_size=grid_size,
            initial_state=initial_state,
            initial_density=initial_density,
            rule=self._forest_fire_rule,
            days=days,
            boundary=boundary,
            random_seed=random_seed,
        )

    def _forest_fire_rule(self, grid: np.ndarray) -> np.ndarray:
        """Apply one Drossel-Schwabl forest fire generation."""
        rows, cols = grid.shape
        if self.boundary == "periodic":
            padded = np.pad(grid, 1, mode="wrap")
        else:
            padded = np.pad(grid, 1, mode="constant", constant_values=EMPTY)

        burning = grid == BURNING
        trees = grid == TREE
        empty = grid == EMPTY

        # Count burning neighbours (exclude the cell itself).
        neighbour_burning = np.zeros((rows, cols), dtype=int)
        for i in range(3):
            for j in range(3):
                neighbour_burning += padded[i:i + rows, j:j + cols] == BURNING
        neighbour_burning -= burning

        new_grid = grid.copy()
        # 1. Burning -> empty.
        new_grid[burning] = EMPTY
        # 2. Tree ignites if a neighbour burns or lightning strikes.
        ignites = trees & ((neighbour_burning > 0) | (self._rng.random_sample((rows, cols)) < self.p))
        new_grid[ignites] = BURNING
        # 3. Empty -> tree (growth), using an independent random draw.
        grows = empty & (self._rng.random_sample((rows, cols)) < self.g)
        new_grid[grows] = TREE
        return new_grid

    def run_simulation(self) -> List[float]:
        """Run the forest fire simulation.

        Returns:
            A list with the number of trees for each generation.
        """
        self.reset()
        self.current_state = self.initial_state.copy()
        self.state_history = [self.initial_state.copy()]

        trees = [int(np.sum(self.current_state == TREE))]
        fires = [int(np.sum(self.current_state == BURNING))]

        for _ in range(1, self.days):
            self.current_state = self._forest_fire_rule(self.current_state)
            self.state_history.append(self.current_state.copy())
            trees.append(int(np.sum(self.current_state == TREE)))
            fires.append(int(np.sum(self.current_state == BURNING)))

        self.tree_history = trees
        self.fire_history = fires
        return [float(t) for t in trees]

    def get_statistics(self) -> Dict[str, float]:
        """Summary statistics over the run."""
        if not self.tree_history:
            raise ValueError("No simulation results available. Run the simulation first.")
        total_cells = self.grid_size[0] * self.grid_size[1]
        return {
            "mean_trees": float(np.mean(self.tree_history)),
            "mean_fires": float(np.mean(self.fire_history)),
            "max_fires": float(np.max(self.fire_history)),
            "final_tree_fraction": float(self.tree_history[-1] / total_cells),
        }

    def reset(self) -> None:
        """Reset the simulation to its initial state."""
        super().reset()
        self._rng = np.random.RandomState(self.random_seed)
        self.tree_history = []
        self.fire_history = []

    @classmethod
    def get_parameters_info(cls) -> Dict[str, Dict[str, Any]]:
        """Get information about the parameters required by this simulation."""
        params = super().get_parameters_info()
        params.update({
            "p": {
                "type": "float",
                "description": "Spontaneous-ignition (lightning) probability per tree per step",
                "required": False,
                "default": 1e-4,
            },
            "g": {
                "type": "float",
                "description": "Tree-regrowth probability per empty cell per step",
                "required": False,
                "default": 1e-2,
            },
        })
        params["rule"]["description"] = "Fixed to the Drossel-Schwabl forest fire rule"
        params["rule"]["default"] = "forest_fire"
        params["initial_density"]["description"] = "Initial fraction of cells that are trees"
        return params
