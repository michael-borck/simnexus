"""Queueing Simulation implementation."""

import heapq
import random
import numpy as np
from typing import Any, Dict, List, Optional, Tuple

from .base_simulation import BaseSimulation
from .registry import SimulatorRegistry
from .discrete_event_simulation import DiscreteEventSimulation, Event


@SimulatorRegistry.register("QueueingSystem")
class QueueingSimulation(DiscreteEventSimulation):
    """A simulation class for queueing systems (e.g., M/M/1, M/M/c).
    
    This simulation models the arrival and service of customers in a queueing system.
    It tracks metrics like queue length, waiting time, and system utilization.
    
    Attributes:
        arrival_rate (float): The average number of arrivals per time unit.
        service_rate (float): The average number of customers served per time unit.
        num_servers (int): The number of servers in the system.
        max_queue_length (Optional[int]): The maximum queue length (None for unlimited).
        state (Dict[str, Any]): The current state of the simulation, including:
            - queue_length: Current number of customers in the queue
            - servers_busy: Number of busy servers
            - total_customers: Total number of customers processed
            - total_waiting_time: Total waiting time of all customers
            - rejected_customers: Number of customers rejected due to queue limits
    """
    
    def __init__(
        self, max_time: float, arrival_rate: float, service_rate: float,
        num_servers: int = 1, max_queue_length: Optional[int] = None,
        time_step: float = 1.0, random_seed: Optional[int] = None
    ) -> None:
        """Initialize the queueing simulation.
        
        Args:
            max_time: The maximum simulation time.
            arrival_rate: The average number of arrivals per time unit.
            service_rate: The average number of customers served per time unit.
            num_servers: The number of servers in the system.
            max_queue_length: The maximum queue length (None for unlimited).
            time_step: The time step for recording results.
            random_seed: Seed for random number generation.
        """
        super().__init__(max_time=max_time, time_step=time_step, random_seed=random_seed)
        
        self.arrival_rate = arrival_rate
        self.service_rate = service_rate
        self.num_servers = num_servers
        self.max_queue_length = max_queue_length
        
        # Initialize state
        self.reset()
        
        # Schedule the first arrival
        self._schedule_arrival()
    
    def reset(self) -> None:
        """Reset the simulation to its initial state."""
        super().reset()
        
        # Initialize the queueing system state
        self.state = {
            "queue_length": 0,          # Current queue length
            "servers_busy": 0,          # Number of busy servers
            "total_customers": 0,       # Total customers processed
            "total_waiting_time": 0.0,  # Total waiting time
            "rejected_customers": 0,    # Customers rejected due to queue limits
            "value": 0.0                # Current value for results (queue length)
        }
        
        # Clear the event queue, then schedule the first arrival so the system
        # is ready to run after a single reset() (the discrete-event engine calls
        # reset() once at the start of run_simulation).
        self.event_queue = []
        self._schedule_arrival()
    
    def _schedule_arrival(self) -> None:
        """Schedule the next customer arrival."""
        # Generate time until next arrival (exponential distribution)
        inter_arrival_time = np.random.exponential(1.0 / self.arrival_rate)
        arrival_time = self.current_time + inter_arrival_time
        
        # Schedule the arrival event
        self.schedule_event(arrival_time, self._process_arrival)
    
    def _process_arrival(self, sim: DiscreteEventSimulation, data: Any) -> None:
        """Process a customer arrival.
        
        Args:
            sim: The simulation instance.
            data: Additional data (not used for arrivals).
        """
        # Schedule the next arrival
        self._schedule_arrival()
        
        # Check if there's an available server
        if self.state["servers_busy"] < self.num_servers:
            # Server is available, start service immediately
            self.state["servers_busy"] += 1
            
            # Schedule service completion
            service_time = np.random.exponential(1.0 / self.service_rate)
            service_end_time = self.current_time + service_time
            self.schedule_event(service_end_time, self._process_departure)
            
            # Record statistics
            self.state["total_customers"] += 1
            
        else:
            # All servers are busy, check if queue has space
            if self.max_queue_length is None or self.state["queue_length"] < self.max_queue_length:
                # Add customer to queue
                self.state["queue_length"] += 1
                self.state["value"] = float(self.state["queue_length"])  # Update value for recording
                
                # Record arrival time for waiting time calculation
                arrival_data = {"arrival_time": self.current_time}
                heapq.heappush(self.event_queue, Event(
                    self.current_time, self._join_queue, data=arrival_data, priority=1
                ))
            else:
                # Queue is full, reject customer
                self.state["rejected_customers"] += 1
    
    def _join_queue(self, sim: DiscreteEventSimulation, data: Any) -> None:
        """Add a customer to the queue. This is a virtual event that doesn't advance time.
        
        Args:
            sim: The simulation instance.
            data: Contains the customer's arrival time.
        """
        # This event just records the arrival time of the customer in the queue
        pass
    
    def _process_departure(self, sim: DiscreteEventSimulation, data: Any) -> None:
        """Process a customer departure (service completion).
        
        Args:
            sim: The simulation instance.
            data: Additional data (not used for departures).
        """
        # Check if there are customers waiting in the queue
        if self.state["queue_length"] > 0:
            # Get the next customer from the queue
            self.state["queue_length"] -= 1
            self.state["value"] = float(self.state["queue_length"])  # Update value for recording
            
            # Calculate waiting time if we have arrival time
            next_customer = None
            for i, event in enumerate(self.event_queue):
                if event.action == self._join_queue:
                    next_customer = event
                    waiting_time = self.current_time - event.data["arrival_time"]
                    self.state["total_waiting_time"] += waiting_time
                    self.event_queue.pop(i)
                    heapq.heapify(self.event_queue)
                    break
            
            # Schedule service completion for the next customer
            service_time = np.random.exponential(1.0 / self.service_rate)
            service_end_time = self.current_time + service_time
            self.schedule_event(service_end_time, self._process_departure)
            
        else:
            # No customers in queue, server becomes idle
            self.state["servers_busy"] -= 1
    
    def run_simulation(self) -> List[float]:
        """Run the queueing simulation and return queue length over time.
        
        Returns:
            A list of queue lengths at regular intervals.
        """
        # Delegate to the discrete-event engine. It calls reset() exactly once,
        # and reset() schedules the first arrival, so the event queue is populated
        # and the loop actually processes events.
        return super().run_simulation()
    
    def get_statistics(self) -> Dict[str, float]:
        """Get summary statistics from the simulation.
        
        Returns:
            A dictionary of statistics including average queue length,
            average waiting time, server utilization, and rejection rate.
        """
        stats = {}
        
        # Only calculate if we've processed some customers
        if self.state["total_customers"] > 0:
            # Average waiting time per customer
            stats["avg_waiting_time"] = self.state["total_waiting_time"] / self.state["total_customers"]
            
            # Average queue length (approximated from our time series)
            stats["avg_queue_length"] = sum(self.results) / len(self.results)
            
            # Estimate server utilization from queue dynamics
            arrival_rate_effective = self.state["total_customers"] / self.max_time
            stats["server_utilization"] = arrival_rate_effective / (self.num_servers * self.service_rate)
            
            # Rejection rate (if applicable)
            total_arrivals = self.state["total_customers"] + self.state["rejected_customers"]
            if total_arrivals > 0:
                stats["rejection_rate"] = self.state["rejected_customers"] / total_arrivals
            else:
                stats["rejection_rate"] = 0.0
        
        return stats
    
    @classmethod
    def get_parameters_info(cls) -> Dict[str, Dict[str, Any]]:
        """Get information about the parameters required by this simulation.
        
        Returns:
            A dictionary mapping parameter names to their metadata.
        """
        # Get parameters from parent class
        params = super().get_parameters_info()
        
        # Add class-specific parameters
        params.update({
            'arrival_rate': {
                'type': 'float',
                'description': 'Average number of customer arrivals per time unit',
                'required': True
            },
            'service_rate': {
                'type': 'float',
                'description': 'Average number of customers served per time unit per server',
                'required': True
            },
            'num_servers': {
                'type': 'int',
                'description': 'Number of servers in the queueing system',
                'required': False,
                'default': 1
            },
            'max_queue_length': {
                'type': 'int',
                'description': 'Maximum queue length (None for unlimited)',
                'required': False,
                'default': None
            }
        })
        
        return params