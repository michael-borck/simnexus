"""Supply Chain Simulation implementation."""

import numpy as np
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from .base_simulation import BaseSimulation
from .registry import SimulatorRegistry


class SupplyChainNode:
    """Base class for all nodes in a supply chain network.
    
    This class defines the common interface for all nodes,
    including factories, warehouses, retailers, etc.
    
    Attributes:
        name (str): The name of the node.
        inventory (float): Current inventory level.
        capacity (float): Maximum inventory capacity.
        lead_time (int): Time delay for incoming shipments.
        pending_shipments (List[Tuple[int, float]]): List of (arrival_day, amount) tuples.
        order_backlog (float): Unfulfilled orders.
        history (Dict[str, List[float]]): History of key metrics.
    """
    
    def __init__(
        self, 
        name: str,
        initial_inventory: float = 0,
        capacity: float = float('inf'),
        lead_time: int = 1
    ) -> None:
        """Initialize a new supply chain node.
        
        Args:
            name: The name of the node.
            initial_inventory: Initial inventory level.
            capacity: Maximum inventory capacity.
            lead_time: Time delay for incoming shipments in days.
        """
        self.name = name
        self.inventory = initial_inventory
        self._initial_inventory = initial_inventory
        self.capacity = capacity
        self.lead_time = lead_time
        self.pending_shipments = []  # (arrival_day, amount) tuples
        self.order_backlog = 0.0
        
        # Track history
        self.history = {
            'inventory': [initial_inventory],
            'orders_received': [0.0],
            'orders_fulfilled': [0.0],
            'shipments_sent': [0.0],
            'shipments_received': [0.0],
            'backlog': [0.0]
        }
    
    def place_order(self, amount: float) -> float:
        """Place an order to this node. 
        
        The node will try to fulfill it from inventory.
        
        Args:
            amount: Amount of product to order.
            
        Returns:
            Amount that was successfully fulfilled.
        """
        # Add to received orders history
        if len(self.history['orders_received']) <= 0:
            self.history['orders_received'].append(amount)
        else:
            self.history['orders_received'][-1] += amount
        
        # Try to fulfill from inventory
        fulfilled = min(amount, self.inventory)
        self.inventory -= fulfilled
        
        # Add to history
        if len(self.history['orders_fulfilled']) <= 0:
            self.history['orders_fulfilled'].append(fulfilled)
        else:
            self.history['orders_fulfilled'][-1] += fulfilled
        
        # Add unfulfilled amount to backlog
        if fulfilled < amount:
            self.order_backlog += (amount - fulfilled)
        
        return fulfilled
    
    def receive_shipment(self, amount: float) -> None:
        """Receive a shipment of products.
        
        Args:
            amount: Amount of product being received.
        """
        # Add to history
        if len(self.history['shipments_received']) <= 0:
            self.history['shipments_received'].append(amount)
        else:
            self.history['shipments_received'][-1] += amount
        
        # Add to inventory (up to capacity)
        usable_amount = min(amount, self.capacity - self.inventory)
        self.inventory += usable_amount
        
        # Excess amounts are lost (or could be handled differently)
    
    def schedule_shipment(self, day: int, amount: float) -> None:
        """Schedule a shipment to arrive on a future day.
        
        Args:
            day: The day the shipment will arrive.
            amount: Amount of product in the shipment.
        """
        self.pending_shipments.append((day, amount))
    
    def update(self, current_day: int) -> None:
        """Update the node's state for the current day.
        
        This method should be called once per simulation day.
        
        Args:
            current_day: The current simulation day.
        """
        # Process any shipments due to arrive today
        arrived_shipments = []
        remaining_shipments = []
        
        for arrival_day, amount in self.pending_shipments:
            if arrival_day <= current_day:
                self.receive_shipment(amount)
                arrived_shipments.append((arrival_day, amount))
            else:
                remaining_shipments.append((arrival_day, amount))
        
        self.pending_shipments = remaining_shipments
        
        # Try to fulfill backlog orders from inventory
        if self.order_backlog > 0 and self.inventory > 0:
            fulfilled = min(self.order_backlog, self.inventory)
            self.inventory -= fulfilled
            self.order_backlog -= fulfilled
            
            # Add to fulfilled orders history
            if len(self.history['orders_fulfilled']) <= 0:
                self.history['orders_fulfilled'].append(fulfilled)
            else:
                self.history['orders_fulfilled'][-1] += fulfilled
    
    def end_day(self) -> None:
        """Record end-of-day metrics and prepare for the next day."""
        # Record current state in history
        self.history['inventory'].append(self.inventory)
        self.history['backlog'].append(self.order_backlog)
        
        # Initialize next day's metrics
        self.history['orders_received'].append(0.0)
        self.history['orders_fulfilled'].append(0.0)
        self.history['shipments_sent'].append(0.0)
        self.history['shipments_received'].append(0.0)
    
    def get_history(self) -> Dict[str, List[float]]:
        """Get the history of key metrics.
        
        Returns:
            Dictionary of metric histories.
        """
        return self.history

    def reset(self) -> None:
        """Reset the node to its initial state.
+
        Restores inventory, clears pending shipments and order backlog, and
        rebuilds the history to the same state recorded at construction.
        """
        self.inventory = self._initial_inventory
        self.pending_shipments = []
        self.order_backlog = 0.0
        self.history = {
            'inventory': [self._initial_inventory],
            'orders_received': [0.0],
            'orders_fulfilled': [0.0],
            'shipments_sent': [0.0],
            'shipments_received': [0.0],
            'backlog': [0.0],
        }


class Factory(SupplyChainNode):
    """A factory node that produces new products.
    
    Attributes:
        production_capacity (float): Maximum units producible per day.
        production_cost (float): Cost per unit produced.
    """
    
    def __init__(
        self, 
        name: str,
        production_capacity: float,
        production_cost: float = 1.0,
        initial_inventory: float = 0,
        capacity: float = float('inf'),
        lead_time: int = 1
    ) -> None:
        """Initialize a new factory node.
        
        Args:
            name: The name of the factory.
            production_capacity: Maximum units producible per day.
            production_cost: Cost per unit produced.
            initial_inventory: Initial inventory level.
            capacity: Maximum inventory capacity.
            lead_time: Time delay for incoming shipments in days.
        """
        super().__init__(name, initial_inventory, capacity, lead_time)
        self.production_capacity = production_capacity
        self.production_cost = production_cost
        
        # Additional history metrics for factories
        self.history['production'] = [0.0]
        self.history['production_cost'] = [0.0]
    
    def produce(self, amount: float) -> float:
        """Produce new products.
        
        Args:
            amount: Amount to try to produce.
            
        Returns:
            Amount actually produced.
        """
        # Limited by production capacity
        produced = min(amount, self.production_capacity)
        
        # Limited by available capacity
        available_capacity = self.capacity - self.inventory
        produced = min(produced, available_capacity)
        
        # Update inventory and cost
        self.inventory += produced
        cost = produced * self.production_cost
        
        # Update history
        if len(self.history['production']) <= 0:
            self.history['production'].append(produced)
            self.history['production_cost'].append(cost)
        else:
            self.history['production'][-1] += produced
            self.history['production_cost'][-1] += cost
            
        return produced
    
    def end_day(self) -> None:
        """Record end-of-day metrics and prepare for the next day."""
        super().end_day()
        
        # Initialize next day's production metrics
        self.history['production'].append(0.0)
        self.history['production_cost'].append(0.0)

    def reset(self) -> None:
        """Reset the factory, including its production history."""
        super().reset()
        self.history['production'] = [0.0]
        self.history['production_cost'] = [0.0]


class Distributor(SupplyChainNode):
    """A distributor node that moves products between supply chain nodes.
    
    Attributes:
        shipping_cost (float): Cost per unit shipped.
    """
    
    def __init__(
        self, 
        name: str,
        shipping_cost: float = 0.5,
        initial_inventory: float = 0,
        capacity: float = float('inf'),
        lead_time: int = 1
    ) -> None:
        """Initialize a new distributor node.
        
        Args:
            name: The name of the distributor.
            shipping_cost: Cost per unit shipped.
            initial_inventory: Initial inventory level.
            capacity: Maximum inventory capacity.
            lead_time: Time delay for incoming shipments in days.
        """
        super().__init__(name, initial_inventory, capacity, lead_time)
        self.shipping_cost = shipping_cost
        
        # Additional history metrics for distributors
        self.history['shipping_cost'] = [0.0]
    
    def ship(self, destination: SupplyChainNode, amount: float, current_day: int) -> float:
        """Ship products to a destination node.
        
        Args:
            destination: The node to ship to.
            amount: Amount to try to ship.
            current_day: The current simulation day.
            
        Returns:
            Amount actually shipped.
        """
        # Limited by available inventory
        shipped = min(amount, self.inventory)
        self.inventory -= shipped
        
        # Calculate cost
        cost = shipped * self.shipping_cost
        
        # Update history
        if len(self.history['shipments_sent']) <= 0:
            self.history['shipments_sent'].append(shipped)
            self.history['shipping_cost'].append(cost)
        else:
            self.history['shipments_sent'][-1] += shipped
            self.history['shipping_cost'][-1] += cost
        
        # Schedule arrival at destination
        arrival_day = current_day + destination.lead_time
        destination.schedule_shipment(arrival_day, shipped)
        
        return shipped
    
    def end_day(self) -> None:
        """Record end-of-day metrics and prepare for the next day."""
        super().end_day()
        
        # Initialize next day's shipping metrics
        self.history['shipping_cost'].append(0.0)

    def reset(self) -> None:
        """Reset the distributor, including its shipping-cost history."""
        super().reset()
        self.history['shipping_cost'] = [0.0]


class Retailer(SupplyChainNode):
    """A retailer node that sells products to end customers.
    
    Attributes:
        selling_price (float): Price per unit sold.
        holding_cost (float): Cost per unit held in inventory per day.
        stockout_cost (float): Cost per unit of unfulfilled demand per day.
    """
    
    def __init__(
        self, 
        name: str,
        selling_price: float = 5.0,
        holding_cost: float = 0.1,
        stockout_cost: float = 1.0,
        initial_inventory: float = 0,
        capacity: float = float('inf'),
        lead_time: int = 1
    ) -> None:
        """Initialize a new retailer node.
        
        Args:
            name: The name of the retailer.
            selling_price: Price per unit sold.
            holding_cost: Cost per unit held in inventory per day.
            stockout_cost: Cost per unit of unfulfilled demand per day.
            initial_inventory: Initial inventory level.
            capacity: Maximum inventory capacity.
            lead_time: Time delay for incoming shipments in days.
        """
        super().__init__(name, initial_inventory, capacity, lead_time)
        self.selling_price = selling_price
        self.holding_cost = holding_cost
        self.stockout_cost = stockout_cost
        
        # Additional history metrics for retailers
        self.history['sales'] = [0.0]
        self.history['revenue'] = [0.0]
        self.history['demand'] = [0.0]
        self.history['holding_cost'] = [0.0]
        self.history['stockout_cost'] = [0.0]
    
    def fulfill_demand(self, demand: float) -> float:
        """Fulfill customer demand.
        
        Args:
            demand: Amount demanded by customers.
            
        Returns:
            Amount actually sold.
        """
        # Record demand in history
        if len(self.history['demand']) <= 0:
            self.history['demand'].append(demand)
        else:
            self.history['demand'][-1] += demand
        
        # Try to fulfill from inventory
        sold = min(demand, self.inventory)
        self.inventory -= sold
        
        # Calculate revenue
        revenue = sold * self.selling_price
        
        # Calculate stockout cost
        unfulfilled = demand - sold
        stockout_cost = unfulfilled * self.stockout_cost
        
        # Update history
        if len(self.history['sales']) <= 0:
            self.history['sales'].append(sold)
            self.history['revenue'].append(revenue)
            self.history['stockout_cost'].append(stockout_cost)
        else:
            self.history['sales'][-1] += sold
            self.history['revenue'][-1] += revenue
            self.history['stockout_cost'][-1] += stockout_cost
        
        return sold
    
    def update(self, current_day: int) -> None:
        """Update the node's state for the current day.
        
        Args:
            current_day: The current simulation day.
        """
        super().update(current_day)
        
        # Calculate holding cost
        holding_cost = self.inventory * self.holding_cost
        
        # Update history
        if len(self.history['holding_cost']) <= 0:
            self.history['holding_cost'].append(holding_cost)
        else:
            self.history['holding_cost'][-1] += holding_cost
    
    def end_day(self) -> None:
        """Record end-of-day metrics and prepare for the next day."""
        super().end_day()
        
        # Initialize next day's retail metrics
        self.history['sales'].append(0.0)
        self.history['revenue'].append(0.0)
        self.history['demand'].append(0.0)
        self.history['holding_cost'].append(0.0)
        self.history['stockout_cost'].append(0.0)

    def reset(self) -> None:
        """Reset the retailer, including its sales and cost histories."""
        super().reset()
        self.history['sales'] = [0.0]
        self.history['revenue'] = [0.0]
        self.history['demand'] = [0.0]
        self.history['holding_cost'] = [0.0]
        self.history['stockout_cost'] = [0.0]


class SupplyChainLink:
    """Represents a connection between two nodes in the supply chain.
    
    Attributes:
        source (SupplyChainNode): The source node.
        destination (SupplyChainNode): The destination node.
    """
    
    def __init__(self, source: SupplyChainNode, destination: SupplyChainNode) -> None:
        """Initialize a new supply chain link.
        
        Args:
            source: The source node.
            destination: The destination node.
        """
        self.source = source
        self.destination = destination


@SimulatorRegistry.register("SupplyChain")
class SupplyChainSimulation(BaseSimulation):
    """A simulation class for supply chain dynamics.
    
    This simulation models the flow of products through a network of
    interconnected supply chain nodes (factories, distributors, retailers, etc.).
    
    Attributes:
        nodes (Dict[str, SupplyChainNode]): Dictionary of all nodes in the network.
        links (List[SupplyChainLink]): List of connections between nodes.
        days (int): Number of days to simulate.
        demand_generator (Callable): Function that generates customer demand.
        ordering_policies (Dict[str, Callable]): Dictionary of ordering policies for each node.
        random_seed (Optional[int]): Seed for random number generation.
    """
    
    def __init__(
        self,
        nodes: Dict[str, SupplyChainNode],
        links: List[SupplyChainLink],
        demand_generator: callable,
        ordering_policies: Dict[str, callable],
        days: int = 100,
        random_seed: Optional[int] = None
    ) -> None:
        """Initialize the supply chain simulation.
        
        Args:
            nodes: Dictionary of all nodes in the supply chain network.
            links: List of connections between nodes.
            demand_generator: Function to generate customer demand for each retailer.
            ordering_policies: Dictionary mapping node names to their ordering policy functions.
            days: Number of days to simulate.
            random_seed: Seed for random number generation.
        """
        super().__init__(days=days, random_seed=random_seed)
        
        self.nodes = nodes
        self.links = links
        self.demand_generator = demand_generator
        self.ordering_policies = ordering_policies
        
        # Validate network consistency
        self._validate_network()
        
        # Prepare result storage
        self.total_profit = 0.0
        self.total_costs = 0.0
        self.total_revenue = 0.0
        self.service_level = 0.0
        
        # Create lookup dictionaries for efficiency
        self._build_network_lookups()
    
    def _validate_network(self) -> None:
        """Validate the consistency of the supply chain network."""
        # Check that all link endpoints exist in nodes
        for link in self.links:
            if link.source.name not in self.nodes:
                raise ValueError(f"Link source '{link.source.name}' not found in nodes dictionary")
            if link.destination.name not in self.nodes:
                raise ValueError(f"Link destination '{link.destination.name}' not found in nodes dictionary")
        
        # Check that all nodes have an ordering policy
        for node_name in self.nodes:
            if node_name not in self.ordering_policies:
                raise ValueError(f"No ordering policy defined for node '{node_name}'")
    
    def _build_network_lookups(self) -> None:
        """Build lookup dictionaries for the network."""
        # Build supplier lookup (for each node, who are its suppliers)
        self.suppliers = {node_name: [] for node_name in self.nodes}
        
        for link in self.links:
            self.suppliers[link.destination.name].append(link.source.name)
        
        # Build customer lookup (for each node, who are its customers)
        self.customers = {node_name: [] for node_name in self.nodes}
        
        for link in self.links:
            self.customers[link.source.name].append(link.destination.name)
        
        # Identify retailers (nodes with no customers)
        self.retailers = [node_name for node_name, customers in self.customers.items() if not customers]
    
    def run_simulation(self) -> Dict[str, Dict[str, List[float]]]:
        """Run the supply chain simulation.
        
        Returns:
            Dictionary with the history of each node and overall metrics.
        """
        self.reset()
        
        # Initialize metrics
        total_demand = 0.0
        total_sales = 0.0
        
        # Run for specified number of days
        for day in range(self.days):
            # Generate customer demand for retailers
            for retailer_name in self.retailers:
                retailer = self.nodes[retailer_name]
                demand = self.demand_generator(day, retailer_name)
                
                # Retailer fulfills customer demand
                sold = retailer.fulfill_demand(demand)
                
                # Track for service level calculation
                total_demand += demand
                total_sales += sold
            
            # Each node decides how much to order based on policy
            for node_name, node in self.nodes.items():
                # Skip nodes with no suppliers
                if not self.suppliers[node_name]:
                    continue
                
                # Apply ordering policy
                policy = self.ordering_policies[node_name]
                orders = policy(node, day, self)
                
                # Place orders with suppliers
                for supplier_name, amount in orders.items():
                    if amount > 0:
                        supplier = self.nodes[supplier_name]
                        supplier.place_order(amount)
            
            # Factories produce products
            for node_name, node in self.nodes.items():
                if isinstance(node, Factory):
                    # Determine production amount (could use a more sophisticated policy)
                    backlog = node.order_backlog
                    capacity_gap = node.capacity - node.inventory
                    production_target = min(backlog, capacity_gap)
                    
                    if production_target > 0:
                        node.produce(production_target)
            
            # Nodes ship products to customers
            for link in self.links:
                source = link.source
                destination = link.destination
                
                # Determine shipping amount (could use a more sophisticated policy)
                if source.inventory > 0 and destination.order_backlog > 0:
                    ship_amount = min(source.inventory, destination.order_backlog)
                    
                    if ship_amount > 0 and isinstance(source, Distributor):
                        source.ship(destination, ship_amount, day)
            
            # Update node states
            for node in self.nodes.values():
                node.update(day)
            
            # End the day and record metrics
            for node in self.nodes.values():
                node.end_day()
        
        # Calculate overall metrics
        self.service_level = total_sales / total_demand if total_demand > 0 else 0.0
        
        # Calculate financial metrics
        self.total_revenue = sum(
            sum(node.history['revenue']) 
            for node in self.nodes.values() 
            if isinstance(node, Retailer)
        )
        
        production_costs = sum(
            sum(node.history['production_cost']) 
            for node in self.nodes.values() 
            if isinstance(node, Factory)
        )
        
        shipping_costs = sum(
            sum(node.history['shipping_cost']) 
            for node in self.nodes.values() 
            if isinstance(node, Distributor)
        )
        
        holding_costs = sum(
            sum(node.history['holding_cost']) 
            for node in self.nodes.values() 
            if isinstance(node, Retailer)
        )
        
        stockout_costs = sum(
            sum(node.history['stockout_cost']) 
            for node in self.nodes.values() 
            if isinstance(node, Retailer)
        )
        
        self.total_costs = production_costs + shipping_costs + holding_costs + stockout_costs
        self.total_profit = self.total_revenue - self.total_costs
        
        # Format output
        result_dict = {}
        
        # Node histories
        for node_name, node in self.nodes.items():
            result_dict[node_name] = node.get_history()
        
        # Overall metrics
        result_dict['overall_metrics'] = {
            'service_level': [self.service_level],
            'total_profit': [self.total_profit],
            'total_revenue': [self.total_revenue],
            'total_costs': [self.total_costs]
        }
        
        return result_dict
    
    def get_node_history(self, node_name: str) -> Dict[str, List[float]]:
        """Get the history of a specific node.
        
        Args:
            node_name: The name of the node.
            
        Returns:
            Dictionary of metric histories for the node.
        """
        if node_name not in self.nodes:
            raise ValueError(f"Node '{node_name}' not found")
        
        return self.nodes[node_name].get_history()
    
    def reset(self) -> None:
        """Reset the simulation to its initial state."""
        super().reset()
        
        # Reset all nodes
        for node in self.nodes.values():
            # Reset through the appropriate class method
            if isinstance(node, (Factory, Distributor, Retailer)):
                node.reset()
        
        # Reset metrics
        self.total_profit = 0.0
        self.total_costs = 0.0
        self.total_revenue = 0.0
        self.service_level = 0.0
    
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
            'nodes': {
                'type': 'Dict[str, SupplyChainNode]',
                'description': 'Dictionary of all nodes in the network',
                'required': True
            },
            'links': {
                'type': 'List[SupplyChainLink]',
                'description': 'List of connections between nodes',
                'required': True
            },
            'demand_generator': {
                'type': 'callable',
                'description': 'Function to generate customer demand for each retailer',
                'required': True
            },
            'ordering_policies': {
                'type': 'Dict[str, callable]',
                'description': 'Dictionary mapping node names to their ordering policy functions',
                'required': True
            }
        })
        
        return params
    
    
# Common ordering policies
def base_stock_policy(target_level: float, review_period: int = 1):
    """Create a base stock ordering policy function.
    
    Orders enough to bring the inventory position up to the target level
    at regular review periods.
    
    Args:
        target_level: The desired inventory level.
        review_period: How often to review inventory (in days).
        
    Returns:
        A policy function that can be used in a SupplyChainSimulation.
    """
    def policy(node, day, simulation):
        orders = {}
        
        # Only order on review days
        if day % review_period == 0:
            # Calculate inventory position (current + on order)
            inventory_position = node.inventory
            for _, amount in node.pending_shipments:
                inventory_position += amount
            
            # Calculate order amount
            order_needed = target_level - inventory_position
            
            if order_needed > 0:
                # Distribute orders among suppliers (equally for now)
                suppliers = simulation.suppliers[node.name]
                if suppliers:
                    order_per_supplier = order_needed / len(suppliers)
                    orders = {supplier: order_per_supplier for supplier in suppliers}
        
        return orders
    
    return policy


def economic_order_quantity(demand_rate: float, setup_cost: float, holding_cost: float):
    """Create an Economic Order Quantity (EOQ) policy function.
    
    Orders a fixed optimal quantity when inventory drops below the reorder point.
    
    Args:
        demand_rate: Average demand per day.
        setup_cost: Fixed cost per order.
        holding_cost: Cost to hold one unit in inventory for one day.
        
    Returns:
        A policy function that can be used in a SupplyChainSimulation.
    """
    # Calculate optimal order quantity
    eoq = (2 * demand_rate * setup_cost / holding_cost) ** 0.5
    
    # Calculate reorder point (for simplicity, just based on lead time)
    def policy(node, day, simulation):
        orders = {}
        
        # Calculate inventory position
        inventory_position = node.inventory
        for _, amount in node.pending_shipments:
            inventory_position += amount
        
        # Order when inventory position drops below reorder point
        reorder_point = demand_rate * node.lead_time
        
        if inventory_position <= reorder_point:
            # Distribute orders among suppliers (equally for now)
            suppliers = simulation.suppliers[node.name]
            if suppliers:
                order_per_supplier = eoq / len(suppliers)
                orders = {supplier: order_per_supplier for supplier in suppliers}
        
        return orders
    
    return policy


# Common demand generators
def constant_demand(rate: float):
    """Create a constant demand generator function.
    
    Args:
        rate: The constant demand rate.
        
    Returns:
        A demand generator function that can be used in a SupplyChainSimulation.
    """
    def generator(day, retailer_name):
        return rate
    
    return generator


def seasonal_demand(base_rate: float, amplitude: float, period: int):
    """Create a seasonal demand generator function.
    
    Args:
        base_rate: The base demand rate.
        amplitude: The amplitude of the seasonal fluctuation.
        period: The period of the seasonal cycle in days.
        
    Returns:
        A demand generator function that can be used in a SupplyChainSimulation.
    """
    def generator(day, retailer_name):
        seasonal_factor = 1.0 + amplitude * np.sin(2 * np.pi * day / period)
        return base_rate * seasonal_factor
    
    return generator


def normal_demand(mean: float, std_dev: float):
    """Create a normally distributed demand generator function.
    
    Args:
        mean: The mean demand.
        std_dev: The standard deviation of demand.
        
    Returns:
        A demand generator function that can be used in a SupplyChainSimulation.
    """
    def generator(day, retailer_name):
        demand = np.random.normal(mean, std_dev)
        return max(0, demand)  # Ensure non-negative demand
    
    return generator