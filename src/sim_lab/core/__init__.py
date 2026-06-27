"""Core simulation modules for the sim-lab package."""

from .agent_based_simulation import Agent, AgentBasedSimulation, Environment
from .base_simulation import BaseSimulation
from .boids_simulation import Boid, BoidsSimulation
from .cellular_automaton_simulation import CellularAutomatonSimulation
from .discrete_event_simulation import DiscreteEventSimulation, Event
from .epidemiological_simulation import EpidemiologicalSimulation
from .forest_fire_simulation import ForestFireSimulation
from .game_of_life_simulation import (
    BEACON,
    BEEHIVE,
    BLINKER,
    BLOCK,
    GLIDER,
    GOSPER_GLIDER_GUN,
    LWSS,
    PATTERNS,
    PULSAR,
    TOAD,
    GameOfLifeSimulation,
    place_pattern,
)
from .gillespie_simulation import GillespieSSASimulation, Reaction, create_decay_model
from .markov_chain_simulation import (
    MarkovChainSimulation,
    create_inventory_model,
    create_random_walk,
    create_weather_model,
)
from .monte_carlo_simulation import MonteCarloSimulation
from .network_simulation import (
    Edge,
    NetworkSimulation,
    Node,
    create_random_network,
    create_scale_free_network,
    create_small_world_network,
)
from .predator_prey_simulation import PredatorPreySimulation, create_predator_prey_model
from .product_popularity_simulation import ProductPopularitySimulation
from .queueing_simulation import QueueingSimulation
from .registry import SimulatorRegistry
from .resource_fluctuations_simulation import ResourceFluctuationsSimulation
from .stock_market_simulation import StockMarketSimulation
from .supply_chain_simulation import (
    Distributor,
    Factory,
    Retailer,
    SupplyChainLink,
    SupplyChainNode,
    SupplyChainSimulation,
    base_stock_policy,
    constant_demand,
    economic_order_quantity,
    normal_demand,
    seasonal_demand,
)
from .system_dynamics_simulation import (
    Auxiliary,
    Flow,
    Stock,
    SystemDynamicsSimulation,
    create_predefined_model,
)

__all__ = [
    # Base classes
    "BaseSimulation",
    "SimulatorRegistry",
    
    # Basic simulations
    "ProductPopularitySimulation",
    "ResourceFluctuationsSimulation",
    "StockMarketSimulation",
    
    # Discrete event simulations
    "DiscreteEventSimulation",
    "Event",
    "QueueingSimulation",
    
    # Statistical simulations
    "MonteCarloSimulation",
    "MarkovChainSimulation",
    "create_weather_model",
    "create_random_walk",
    "create_inventory_model",
    "GillespieSSASimulation",
    "Reaction",
    "create_decay_model",
    
    # Domain-specific simulations
    "EpidemiologicalSimulation",
    "CellularAutomatonSimulation",

    # Cellular automata (Game of Life / Forest Fire)
    "GameOfLifeSimulation",
    "ForestFireSimulation",
    "place_pattern",
    "PATTERNS",
    "GLIDER",
    "BLINKER",
    "TOAD",
    "BEACON",
    "BLOCK",
    "BEEHIVE",
    "LWSS",
    "PULSAR",
    "GOSPER_GLIDER_GUN",
    
    # Network simulations
    "NetworkSimulation",
    "Node",
    "Edge",
    "create_random_network",
    "create_scale_free_network",
    "create_small_world_network",
    
    # Agent-based simulation
    "AgentBasedSimulation",
    "Agent",
    "Environment",
    "BoidsSimulation",
    "Boid",
    
    # System dynamics
    "SystemDynamicsSimulation",
    "Stock",
    "Flow",
    "Auxiliary",
    "create_predefined_model",
    
    # Supply chain
    "SupplyChainSimulation",
    "SupplyChainNode",
    "Factory",
    "Distributor",
    "Retailer",
    "SupplyChainLink",
    "base_stock_policy",
    "economic_order_quantity",
    "constant_demand",
    "seasonal_demand",
    "normal_demand",
    
    # Ecological simulations
    "PredatorPreySimulation",
    "create_predator_prey_model"
]