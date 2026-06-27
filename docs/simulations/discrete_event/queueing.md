# Queueing Simulation

## Purpose

This simulation models customers arriving at a service station, waiting in a FIFO queue, and being served by one or more identical servers — the classic **M/M/c** queue. It is a hands-on way to study congestion, waiting time, and server utilisation, and to see why queueing systems behave so non-linearly as the arrival rate approaches the service capacity. Because it is built on a discrete-event engine, it also doubles as a clear introduction to event-driven simulation: time jumps straight from one arrival or departure to the next rather than ticking in fixed steps.

## Parameters

- `max_time`: `float` — The maximum simulation time. The engine processes events until the clock reaches this value.
- `arrival_rate`: `float` — The average number of customer arrivals per time unit ($\lambda$). Inter-arrival times are drawn from an exponential distribution.
- `service_rate`: `float` — The average number of customers a single server can serve per time unit ($\mu$). Service times are drawn from an exponential distribution.
- `num_servers`: `int` (default `1`) — The number of parallel servers in the system ($c$). Set to `1` for an M/M/1 queue, higher for an M/M/c queue.
- `max_queue_length`: `Optional[int]` (default `None`) — The maximum number of customers allowed to wait. `None` means an unbounded queue; a finite value turns arrivals away once the buffer is full (a loss system).
- `time_step`: `float` (default `1.0`) — The interval at which the current queue length is sampled and recorded into the results time series.
- `random_seed`: `Optional[int]` (default `None`) — Seed for the random number generator, so a given run is reproducible.

## Example Code

```python
from sim_lab.core import QueueingSimulation
import matplotlib.pyplot as plt

# An M/M/1 queue: lambda=0.8 arrivals/unit, mu=1.0 service/unit, so rho = 0.8 < 1 (stable).
sim = QueueingSimulation(
    max_time=100,
    arrival_rate=0.8,
    service_rate=1.0,
    num_servers=1,
    random_seed=42,
)

queue_length = sim.run_simulation()          # queue length sampled every time_step
stats = sim.get_statistics()

# Visualise how the queue length evolves over the run
plt.figure(figsize=(10, 6))
plt.plot(queue_length, label='Queue length')
plt.axhline(y=stats.get('avg_queue_length', 0.0), color='red', linestyle='--',
            label=f"Mean = {stats.get('avg_queue_length', 0.0):.2f}")
plt.xlabel('Time step')
plt.ylabel('Number waiting')
plt.title('M/M/1 Queue Length Over Time')
plt.legend()
plt.show()

print("Average waiting time per customer:", round(stats.get('avg_waiting_time', 0.0), 3))
print("Server utilisation (rho):", round(stats.get('server_utilization', 0.0), 3))
print("Rejection rate:", round(stats.get('rejection_rate', 0.0), 3))
```

## Use Case Ideas

### Investigate the Stability Boundary and Traffic Intensity

Hold the service rate fixed and sweep the arrival rate toward and beyond the server capacity, watching what happens to the queue and waiting times. Recall the stability condition $\rho = \lambda / (c\mu) < 1$. Questions to Consider:

- As $\rho$ rises from `0.5` toward `0.95`, how does the average queue length grow? Is the relationship linear?
- What happens to the average waiting time when $\rho \ge 1$? Does the queue settle, or drift upward?
- Run the same configuration several times with different `random_seed` values. How much does the average queue length vary run-to-run near $\rho = 0.9$ versus near $\rho = 0.5$?

### Investigate the Effect of Adding Servers (M/M/1 vs M/M/c)

Keep the total offered load fixed and compare a single fast server against several slower ones. For example, one server with $\mu = 1.0$ versus two servers each with $\mu = 0.5$ both give $c\mu = 1.0$. Questions to Consider:

- For the same $\lambda$, does pooling capacity into more servers increase or decrease the average waiting time?
- Which configuration has the higher peak queue length during a burst of arrivals?
- How does server utilisation differ between the two designs? Which one keeps servers busier?

### Investigate Finite-Capacity Systems and Customer Rejection

Set a finite `max_queue_length` to turn the model into a loss system, where excess arrivals are turned away instead of queuing forever. Questions to Consider:

- As `max_queue_length` shrinks, how does the rejection rate rise and the average waiting time fall?
- Under heavy load ($\rho \ge 1$), what is the trade-off between a long queue (large average waiting time, few rejections) and a short queue (low waiting time, many rejections)?
- Plot the queue length over time for both the unbounded and finite cases on the same axes. Where do they diverge?

## Model Description

The `QueueingSimulation` class implements a single-station queue in **Kendall's notation M/M/c**: **M**arkovian (Poisson) arrivals, **M**arkovian (exponential) service times, and $c$ parallel identical servers, serving customers first-in, first-out. When `max_queue_length` is set the model becomes an **M/M/c/K** loss system.

**Discrete-event engine.** The class extends `DiscreteEventSimulation`, which maintains a min-heap priority queue of `Event` objects ordered by `(time, priority)`. Each event carries a timestamp and a callback. The engine pops the earliest event, advances the simulation clock straight to that event's time, invokes the callback, and repeats until `max_time` is reached. The clock therefore jumps from event to event rather than advancing in fixed increments — the key efficiency of event-driven simulation. Three callbacks drive the whole model:

- **Arrival** (`_process_arrival`): draws the next inter-arrival time from an exponential distribution, $t_a \sim \text{Exp}(1/\lambda)$, and schedules the subsequent arrival. If a server is free the customer enters service immediately and a departure is scheduled with service time $t_s \sim \text{Exp}(1/\mu)$. Otherwise the customer joins the FIFO queue — or is rejected (incrementing the rejected counter) if `max_queue_length` has been reached.
- **Departure** (`_process_departure`): on service completion, if the queue is non-empty the head customer is dequeued, their waiting time $W_q = t_{\text{now}} - t_{\text{arrival}}$ is accumulated, and a fresh service interval is scheduled for the next customer. If the queue is empty the server simply becomes idle.

**Recorded outputs.** The current queue length $L_q(t)$ is sampled at every `time_step` and returned by `run_simulation()` as a time series. The `get_statistics()` method summarises a run into:

- `avg_waiting_time` — mean waiting time per customer who entered service, $\bar{W}_q = \sum W_q / N$;
- `avg_queue_length` — time-average of the recorded queue-length series;
- `server_utilization` — effective arrival rate divided by total capacity, $\lambda_{\text{eff}} / (c\mu)$, i.e. the realised $\rho$;
- `rejection_rate` — fraction of arrivals turned away (zero for an unbounded queue).

**Stability condition.** For an unbounded M/M/c queue a steady state exists only when the offered load per server stays below capacity:

$$\rho = \frac{\lambda}{c\mu} < 1.$$

When $\rho \ge 1$ arrivals outrun service and the queue grows without bound; the simulation still runs, but the recorded queue length and average waiting time drift upward rather than converging.

**Little's Law.** In steady state the long-run averages satisfy $L = \lambda W$: the mean number of customers in the system equals the effective arrival rate times the mean time spent in the system. The queue analog is $L_q = \lambda W_q$. The `avg_queue_length` and `avg_waiting_time` statistics are exactly the quantities needed to verify this identity empirically against the simulation's own data.
