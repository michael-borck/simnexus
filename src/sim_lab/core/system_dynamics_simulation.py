"""System Dynamics Simulation implementation."""

import numpy as np
import scipy.integrate
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from .base_simulation import BaseSimulation
from .registry import SimulatorRegistry


class Stock:
    """Represents a stock (accumulation) in a system dynamics model.
    
    Stocks are state variables that accumulate or deplete over time.
    
    Attributes:
        name (str): The name of the stock.
        initial_value (float): The initial value of the stock.
        current_value (float): The current value of the stock.
        history (List[float]): The history of the stock's values over time.
    """
    
    def __init__(self, name: str, initial_value: float) -> None:
        """Initialize a new stock.
        
        Args:
            name: The name of the stock.
            initial_value: The initial value of the stock.
        """
        self.name = name
        self.initial_value = initial_value
        self.current_value = initial_value
        self.history = [initial_value]
    
    def reset(self) -> None:
        """Reset the stock to its initial value."""
        self.current_value = self.initial_value
        self.history = [self.initial_value]
    
    def update(self, new_value: float) -> None:
        """Update the stock's value.
        
        Args:
            new_value: The new value of the stock.
        """
        self.current_value = new_value
        self.history.append(new_value)


class Flow:
    """Represents a flow in a system dynamics model.
    
    Flows represent rates of change that affect stocks.
    
    Attributes:
        name (str): The name of the flow.
        rate_function (Callable): A function that computes the flow rate.
        history (List[float]): The history of the flow's rates over time.
    """
    
    def __init__(
        self, 
        name: str, 
        rate_function: Callable[[Dict[str, float], float], float]
    ) -> None:
        """Initialize a new flow.
        
        Args:
            name: The name of the flow.
            rate_function: A function that takes the current system state and time
                          and returns the flow rate.
        """
        self.name = name
        self.rate_function = rate_function
        self.history = []
    
    def get_rate(self, state: Dict[str, float], time: float) -> float:
        """Calculate the current flow rate.
        
        Args:
            state: The current system state as a dictionary of stock values.
            time: The current simulation time.
            
        Returns:
            The calculated flow rate.
        """
        rate = self.rate_function(state, time)
        self.history.append(rate)
        return rate
    
    def reset(self) -> None:
        """Reset the flow's history."""
        self.history = []


class Auxiliary:
    """Represents an auxiliary variable in a system dynamics model.
    
    Auxiliary variables are intermediate calculations that depend on stocks,
    flows, and other auxiliaries.
    
    Attributes:
        name (str): The name of the auxiliary variable.
        formula (Callable): A function that computes the auxiliary value.
        history (List[float]): The history of the auxiliary's values over time.
    """
    
    def __init__(
        self, 
        name: str, 
        formula: Callable[[Dict[str, float], Dict[str, float], float], float]
    ) -> None:
        """Initialize a new auxiliary variable.
        
        Args:
            name: The name of the auxiliary variable.
            formula: A function that takes the current system state, flow rates, and time
                    and returns the auxiliary value.
        """
        self.name = name
        self.formula = formula
        self.history = []
    
    def get_value(
        self, 
        state: Dict[str, float], 
        flow_rates: Dict[str, float], 
        time: float
    ) -> float:
        """Calculate the current value of the auxiliary variable.
        
        Args:
            state: The current system state as a dictionary of stock values.
            flow_rates: The current flow rates as a dictionary.
            time: The current simulation time.
            
        Returns:
            The calculated auxiliary value.
        """
        value = self.formula(state, flow_rates, time)
        self.history.append(value)
        return value
    
    def reset(self) -> None:
        """Reset the auxiliary's history."""
        self.history = []


@SimulatorRegistry.register("SystemDynamics")
class SystemDynamicsSimulation(BaseSimulation):
    """A simulation class for system dynamics modeling.
    
    This simulation models complex systems with stocks, flows, and feedback loops
    using differential equations.
    
    Attributes:
        stocks (Dict[str, Stock]): Dictionary of stock variables.
        flows (Dict[str, Flow]): Dictionary of flow variables.
        auxiliaries (Dict[str, Auxiliary]): Dictionary of auxiliary variables.
        days (int): Number of time steps to simulate.
        dt (float): Time step size.
        random_seed (Optional[int]): Seed for random number generation.
    """
    
    def __init__(
        self,
        stocks: Dict[str, Stock],
        flows: Dict[str, Flow],
        auxiliaries: Optional[Dict[str, Auxiliary]] = None,
        days: int = 100,
        dt: float = 1.0,
        integration_method: str = 'RK45',
        random_seed: Optional[int] = None
    ) -> None:
        """Initialize the system dynamics simulation.
        
        Args:
            stocks: Dictionary of stock variables.
            flows: Dictionary of flow variables.
            auxiliaries: Dictionary of auxiliary variables (optional).
            days: Number of time steps to simulate.
            dt: Time step size.
            integration_method: The integration method to use ('euler', 'RK45', etc.).
            random_seed: Seed for random number generation.
        """
        super().__init__(days=days, random_seed=random_seed)
        
        self.stocks = stocks
        self.flows = flows
        self.auxiliaries = auxiliaries or {}
        self.dt = dt
        self.integration_method = integration_method
        
        # Calculate the total simulation time
        self.total_time = days * dt
        
        # Initialize result storage
        self.time_points = None
        self.results = None
    
    def derivatives(self, state_vector: np.ndarray, t: float) -> np.ndarray:
        """Calculate the derivatives of all stocks.
        
        This function is used by the ODE solver to compute state changes.
        
        Args:
            state_vector: Current values of all stocks as an array.
            t: Current simulation time.
            
        Returns:
            Array of derivatives for each stock.
        """
        # Convert state vector to dictionary for easier access
        state = {}
        for i, (name, _) in enumerate(self.stocks.items()):
            state[name] = state_vector[i]
        
        # Calculate flow rates
        flow_rates = {}
        for name, flow in self.flows.items():
            flow_rates[name] = flow.get_rate(state, t)
        
        # Calculate auxiliary variables
        auxiliary_values = {}
        for name, aux in self.auxiliaries.items():
            auxiliary_values[name] = aux.get_value(state, flow_rates, t)
        
        # Calculate derivatives (net flow for each stock)
        derivatives = np.zeros_like(state_vector)
        
        # Each stock's derivative is the sum of inflows minus outflows
        stock_names = list(self.stocks.keys())
        for flow_name, flow in self.flows.items():
            # The flow influences some stocks (positive or negative)
            # This mapping should be determined based on the model structure
            # For this implementation, we'll use a simple naming convention:
            # flow_from_A_to_B means A decreases, B increases
            
            parts = flow_name.split('_')
            if len(parts) >= 4 and parts[0] == 'flow' and parts[1] == 'from' and parts[3] == 'to':
                from_stock = parts[2]
                to_stock = parts[4]
                
                flow_rate = flow_rates[flow_name]
                
                if from_stock in stock_names:
                    from_idx = stock_names.index(from_stock)
                    derivatives[from_idx] -= flow_rate
                
                if to_stock in stock_names:
                    to_idx = stock_names.index(to_stock)
                    derivatives[to_idx] += flow_rate
            
        return derivatives
    
    def run_simulation(self) -> Dict[str, List[float]]:
        """Run the system dynamics simulation.
        
        Returns:
            A dictionary with the history of each stock, flow, and auxiliary variable.
        """
        self.reset()
        
        # Set up initial state
        stock_names = list(self.stocks.keys())
        initial_state = np.array([self.stocks[name].initial_value for name in stock_names])
        
        # Define time points
        if self.integration_method == 'euler':
            # Simple Euler integration
            num_steps = int(self.total_time / self.dt)
            time_points = np.linspace(0, self.total_time, num_steps + 1)
            
            # Initialize result arrays
            state = initial_state.copy()
            results = np.zeros((len(time_points), len(initial_state)))
            results[0] = state
            
            # Perform Euler integration
            for i in range(1, len(time_points)):
                t = time_points[i-1]
                derivatives = self.derivatives(state, t)
                state = state + derivatives * self.dt
                results[i] = state
            
            self.time_points = time_points
            self.results = results
            
        else:
            # Use SciPy's ODE integrator
            time_points = np.linspace(0, self.total_time, int(self.days) + 1)
            
            # Solve the ODE system
            solution = scipy.integrate.solve_ivp(
                lambda t, y: self.derivatives(y, t),
                [0, self.total_time],
                initial_state,
                method=self.integration_method,
                t_eval=time_points
            )
            
            self.time_points = solution.t
            self.results = solution.y.T
        
        # Update stock histories
        for i, name in enumerate(stock_names):
            for value in self.results[:, i]:
                self.stocks[name].update(value)
        
        # Format output as a dictionary
        result_dict = {}
        
        # Add stocks
        for name, stock in self.stocks.items():
            result_dict[f"stock_{name}"] = stock.history
        
        # Add flows
        for name, flow in self.flows.items():
            result_dict[f"flow_{name}"] = flow.history
        
        # Add auxiliaries
        for name, aux in self.auxiliaries.items():
            result_dict[f"aux_{name}"] = aux.history
        
        return result_dict
    
    def get_stock_history(self, name: str) -> List[float]:
        """Get the history of a specific stock.
        
        Args:
            name: The name of the stock.
            
        Returns:
            List of stock values over time.
        """
        if name not in self.stocks:
            raise ValueError(f"Stock '{name}' not found")
        
        return self.stocks[name].history
    
    def get_flow_history(self, name: str) -> List[float]:
        """Get the history of a specific flow.
        
        Args:
            name: The name of the flow.
            
        Returns:
            List of flow rates over time.
        """
        if name not in self.flows:
            raise ValueError(f"Flow '{name}' not found")
        
        return self.flows[name].history
    
    def get_auxiliary_history(self, name: str) -> List[float]:
        """Get the history of a specific auxiliary variable.
        
        Args:
            name: The name of the auxiliary variable.
            
        Returns:
            List of auxiliary values over time.
        """
        if name not in self.auxiliaries:
            raise ValueError(f"Auxiliary variable '{name}' not found")
        
        return self.auxiliaries[name].history
    
    def reset(self) -> None:
        """Reset the simulation to its initial state."""
        super().reset()
        
        for stock in self.stocks.values():
            stock.reset()
        
        for flow in self.flows.values():
            flow.reset()
        
        for aux in self.auxiliaries.values():
            aux.reset()
    
    @classmethod
    def get_parameters_info(cls) -> Dict[str, Dict[str, Any]]:
        """Get information about the parameters required by this simulation.
        
        Returns:
            A dictionary mapping parameter names to their metadata.
        """
        # Get base parameters from parent class
        params = super().get_parameters_info()
        
        # Add class-specific parameters
        params.update({
            'stocks': {
                'type': 'Dict[str, Stock]',
                'description': 'Dictionary of stock variables',
                'required': True
            },
            'flows': {
                'type': 'Dict[str, Flow]',
                'description': 'Dictionary of flow variables',
                'required': True
            },
            'auxiliaries': {
                'type': 'Dict[str, Auxiliary]',
                'description': 'Dictionary of auxiliary variables',
                'required': False,
                'default': '{}'
            },
            'dt': {
                'type': 'float',
                'description': 'Time step size',
                'required': False,
                'default': 1.0
            },
            'integration_method': {
                'type': 'str',
                'description': "Integration method ('euler', 'RK45', etc.)",
                'required': False,
                'default': 'RK45'
            }
        })
        
        return params


# Helper function to create common system dynamics models
def create_predefined_model(model_type: str, **kwargs) -> SystemDynamicsSimulation:
    """Create a predefined system dynamics model.
    
    Args:
        model_type: The type of model to create ('population', 'lotka_volterra', etc.).
        **kwargs: Additional parameters for the specific model.
        
    Returns:
        A configured SystemDynamicsSimulation.
    """
    if model_type == 'population':
        # Simple population growth model
        birth_rate = kwargs.get('birth_rate', 0.03)
        death_rate = kwargs.get('death_rate', 0.01)
        initial_population = kwargs.get('initial_population', 1000)
        
        stocks = {
            'population': Stock('population', initial_population)
        }
        
        def births(state, time):
            return state['population'] * birth_rate
        
        def deaths(state, time):
            return state['population'] * death_rate
        
        flows = {
            'flow_from_births_to_population': Flow('flow_from_births_to_population', births),
            'flow_from_population_to_deaths': Flow('flow_from_population_to_deaths', deaths)
        }
        
        return SystemDynamicsSimulation(
            stocks=stocks,
            flows=flows,
            days=kwargs.get('days', 100),
            dt=kwargs.get('dt', 0.1)
        )
    
    elif model_type == 'lotka_volterra':
        # Predator-prey model
        alpha = kwargs.get('prey_growth_rate', 0.1)
        beta = kwargs.get('predation_rate', 0.01)
        delta = kwargs.get('predator_death_rate', 0.05)
        gamma = kwargs.get('predator_growth_rate', 0.005)
        initial_prey = kwargs.get('initial_prey', 100)
        initial_predators = kwargs.get('initial_predators', 20)
        
        stocks = {
            'prey': Stock('prey', initial_prey),
            'predators': Stock('predators', initial_predators)
        }
        
        def prey_growth(state, time):
            return state['prey'] * alpha
        
        def predation(state, time):
            return state['prey'] * state['predators'] * beta
        
        def predator_growth(state, time):
            return state['prey'] * state['predators'] * gamma
        
        def predator_death(state, time):
            return state['predators'] * delta
        
        flows = {
            'flow_from_growth_to_prey': Flow('flow_from_growth_to_prey', prey_growth),
            'flow_from_prey_to_predation': Flow('flow_from_prey_to_predation', predation),
            'flow_from_predation_to_predators': Flow('flow_from_predation_to_predators', predator_growth),
            'flow_from_predators_to_death': Flow('flow_from_predators_to_death', predator_death)
        }
        
        return SystemDynamicsSimulation(
            stocks=stocks,
            flows=flows,
            days=kwargs.get('days', 100),
            dt=kwargs.get('dt', 0.01)
        )
    
    elif model_type == 'sir':
        # SIR epidemiological model (alternative to the specialized implementation)
        population = kwargs.get('population', 10000)
        initial_infected = kwargs.get('initial_infected', 10)
        initial_recovered = kwargs.get('initial_recovered', 0)
        beta = kwargs.get('transmission_rate', 0.3)
        gamma = kwargs.get('recovery_rate', 0.1)
        
        initial_susceptible = population - initial_infected - initial_recovered
        
        stocks = {
            'susceptible': Stock('susceptible', initial_susceptible),
            'infected': Stock('infected', initial_infected),
            'recovered': Stock('recovered', initial_recovered)
        }
        
        def infection(state, time):
            return beta * state['susceptible'] * state['infected'] / population
        
        def recovery(state, time):
            return gamma * state['infected']
        
        flows = {
            'flow_from_susceptible_to_infected': Flow('flow_from_susceptible_to_infected', infection),
            'flow_from_infected_to_recovered': Flow('flow_from_infected_to_recovered', recovery)
        }
        
        return SystemDynamicsSimulation(
            stocks=stocks,
            flows=flows,
            days=kwargs.get('days', 100),
            dt=kwargs.get('dt', 0.1)
        )
    
    else:
        raise ValueError(f"Unknown model type: {model_type}")