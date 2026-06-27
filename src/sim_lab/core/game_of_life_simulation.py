"""Game of Life simulation built on the cellular automaton engine.

Conway's Game of Life is already a predefined rule of CellularAutomatonSimulation.
This module adds a catalogue of classic starting patterns -- still lifes,
oscillators, spaceships, and the Gosper glider gun -- plus a convenience
simulator that places a named pattern on a grid and evolves it with the
Game of Life rule.
"""

from typing import Any, Dict, Optional, Tuple

import numpy as np

from .cellular_automaton_simulation import CellularAutomatonSimulation
from .registry import SimulatorRegistry

# --- Classic Game of Life patterns (1 = live cell) ------------------------

BLOCK = np.array([
    [1, 1],
    [1, 1],
], dtype=int)  # still life

BEEHIVE = np.array([
    [0, 1, 1, 0],
    [1, 0, 0, 1],
    [0, 1, 1, 0],
], dtype=int)  # still life

BLINKER = np.array([[1, 1, 1]], dtype=int)  # period-2 oscillator

TOAD = np.array([
    [0, 1, 1, 1],
    [1, 1, 1, 0],
], dtype=int)  # period-2 oscillator

BEACON = np.array([
    [1, 1, 0, 0],
    [1, 1, 0, 0],
    [0, 0, 1, 1],
    [0, 0, 1, 1],
], dtype=int)  # period-2 oscillator

GLIDER = np.array([
    [0, 1, 0],
    [0, 0, 1],
    [1, 1, 1],
], dtype=int)  # spaceship (travels diagonally)

LWSS = np.array([  # lightweight spaceship
    [0, 1, 0, 0, 1],
    [1, 0, 0, 0, 0],
    [1, 0, 0, 0, 1],
    [1, 1, 1, 1, 0],
], dtype=int)

PULSAR = np.array([
    [0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1],
    [0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0],
    [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0],
], dtype=int)  # period-3 oscillator

# Gosper glider gun (36 wide x 9 tall) -- emits a glider every 30 generations.
GOSPER_GLIDER_GUN = np.array([
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0],
    [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
], dtype=int)

PATTERNS = {
    "block": BLOCK,
    "beehive": BEEHIVE,
    "blinker": BLINKER,
    "toad": TOAD,
    "beacon": BEACON,
    "glider": GLIDER,
    "lwss": LWSS,
    "pulsar": PULSAR,
    "gosper_glider_gun": GOSPER_GLIDER_GUN,
}


def place_pattern(
    pattern: np.ndarray,
    grid_size: Tuple[int, int],
    offset: Optional[Tuple[int, int]] = None,
) -> np.ndarray:
    """Place a small pattern onto a zeroed grid of the given size.

    Args:
        pattern: 2-D array of 0/1 describing the pattern.
        grid_size: (rows, cols) of the target grid.
        offset: Top-left (row, col) placement. Defaults to centring the pattern.

    Returns:
        A grid_size array containing the pattern on a background of zeros.
    """
    rows, cols = grid_size
    p_rows, p_cols = pattern.shape
    if p_rows > rows or p_cols > cols:
        raise ValueError(
            f"Pattern of shape {pattern.shape} is larger than the grid {grid_size}"
        )
    grid = np.zeros(grid_size, dtype=int)
    if offset is None:
        offset = ((rows - p_rows) // 2, (cols - p_cols) // 2)
    r0, c0 = offset
    if r0 < 0 or c0 < 0 or r0 + p_rows > rows or c0 + p_cols > cols:
        raise ValueError(
            f"Pattern placement at {offset} falls outside the grid {grid_size}"
        )
    grid[r0:r0 + p_rows, c0:c0 + p_cols] = pattern
    return grid


@SimulatorRegistry.register("GameOfLife")
class GameOfLifeSimulation(CellularAutomatonSimulation):
    """Conway's Game of Life seeded with classic starting patterns.

    A thin convenience wrapper around CellularAutomatonSimulation that seeds the
    grid with a named pattern (e.g. a glider or the Gosper glider gun) or a random
    soup, then evolves it with the standard Game of Life rule.

    Attributes:
        pattern (Optional[str]): Name of the starting pattern, or None for a random grid.
    """

    def __init__(
        self,
        grid_size: Tuple[int, int] = (50, 50),
        pattern: Optional[str] = None,
        offset: Optional[Tuple[int, int]] = None,
        initial_density: float = 0.3,
        days: int = 100,
        boundary: str = "periodic",
        random_seed: Optional[int] = None,
    ) -> None:
        """Initialize the Game of Life simulation.

        Args:
            grid_size: Dimensions of the grid as (rows, columns).
            pattern: Name of a pattern in PATTERNS (e.g. "glider"). None for random.
            offset: Top-left placement of the pattern; None centres it.
            initial_density: Probability of a live cell in a random grid.
            days: Number of generations to simulate.
            boundary: Boundary condition ('periodic' or 'fixed').
            random_seed: Seed for random number generation.
        """
        if pattern is not None:
            if pattern not in PATTERNS:
                raise ValueError(
                    f"Unknown pattern '{pattern}'. Choose from {sorted(PATTERNS)}"
                )
            initial_state = place_pattern(PATTERNS[pattern], grid_size, offset)
        else:
            initial_state = None  # let the base class build a random grid

        self.pattern = pattern
        self.offset = offset
        super().__init__(
            grid_size=grid_size,
            initial_state=initial_state,
            initial_density=initial_density,
            rule=self.GAME_OF_LIFE,
            days=days,
            boundary=boundary,
            random_seed=random_seed,
        )

    @classmethod
    def get_parameters_info(cls) -> Dict[str, Dict[str, Any]]:
        """Get information about the parameters required by this simulation."""
        params = super().get_parameters_info()
        params.update({
            "pattern": {
                "type": "Optional[str]",
                "description": "Named starting pattern (see PATTERNS). None for a random grid.",
                "required": False,
                "default": None,
            },
            "offset": {
                "type": "Optional[Tuple[int, int]]",
                "description": "Top-left placement of the pattern; None centres it.",
                "required": False,
                "default": None,
            },
        })
        params["rule"]["description"] = "Fixed to Conway's Game of Life"
        params["rule"]["default"] = "game_of_life"
        return params
