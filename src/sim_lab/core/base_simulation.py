"""Base class for all simulations."""

import random
import numpy as np
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union


class BaseSimulation(ABC):
    """Base class for all SimLab simulations.
    
    This abstract class defines the common interface and utility methods
    for all simulation types in the SimLab package.
    
    Attributes:
        random_seed (Optional[int]): Seed for random number generation to ensure reproducible results
    """
    
    def __init__(self, days: int, random_seed: Optional[int] = None, **kwargs):
        """Initialize the base simulation.
        
        Args:
            days (int): The duration of the simulation in days/steps.
            random_seed (Optional[int]): Seed for random number generation. If None, random results will vary.
            **kwargs: Additional parameters for specific simulation types.
        """
        self.days = days
        self.random_seed = random_seed
        self._initialize_random_generators()
    
    def _initialize_random_generators(self) -> None:
        """Initialize random number generators with the seed."""
        if self.random_seed is not None:
            random.seed(self.random_seed)
            np.random.seed(self.random_seed)
    
    @abstractmethod
    def run_simulation(self) -> List[Union[float, int]]:
        """Run the simulation and return results.
        
        This method must be implemented by all simulation subclasses.
        
        Returns:
            A list of values representing the simulation results over time.
        """
        pass
    
    def reset(self) -> None:
        """Reset the simulation to its initial state.
        
        This allows a simulation instance to be re-run with the same parameters.
        """
        self._initialize_random_generators()
    
    @classmethod
    def get_parameters_info(cls) -> Dict[str, Dict[str, Any]]:
        """Get information about the parameters required by this simulation.
        
        Returns:
            A dictionary mapping parameter names to their metadata (type, description, default, etc.)
        """
        return {
            'days': {
                'type': 'int',
                'description': 'The duration of the simulation in days/steps',
                'required': True
            },
            'random_seed': {
                'type': 'int',
                'description': 'Seed for random number generation to ensure reproducible results',
                'required': False,
                'default': None
            }
        }