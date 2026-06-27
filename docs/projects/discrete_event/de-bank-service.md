# Bank Service Desk
**Difficulty**: Beginner
**Time**: ~45 minutes
**Learning Focus**: Event-driven scheduling; the single-server FIFO queue and time-in-system
**Simulator**: DiscreteEventSimulation (registry `DiscreteEvent`)

## Overview
A bank teller serves customers one at a time. Customers walk in at random moments (a Poisson arrival process), join a single first-in-first-out line, and leave once their service finishes. The central questions are simple but powerful: does the teller always serve customers in the order they arrived, and how fast does the average time a customer spends in the bank — waiting *plus* being served — climb as customers arrive more frequently? This is the textbook **M/M/1** queue, and it is the smallest real system that shows why congestion blows up non-linearly as you approach a server's capacity.

## Setup
Install the toolkit and a plotting library, then import the discrete-event engine directly:

```bash
pip install sim-lab matplotlib
```

```python
from sim_lab.core import DiscreteEventSimulation
import random, statistics
```

## Instructions
The engine jumps the clock straight from one event to the next (an arrival or a service completion) rather than ticking in fixed steps. Every event is a plain function with the signature `action(sim, data)` that may change `sim.state` and schedule future events with `sim.schedule_event(time, action, data=...)`.

**Important engine detail:** `run_simulation()` calls `reset()` at the start, which clears `sim.state` back to a blank slate. So each event makes sure its bookkeeping keys exist first, using `setdefault`. Keeping all state inside the event functions makes the whole model self-contained.

1. **Build the bank model as one function.** The event functions are defined *inside* `run_bank` so they close over the two parameters (`mean_interarrival`, `mean_service`) — no globals. State holds a FIFO queue of arrival times, a busy flag for the teller, and a list that records each finished customer's time in system.

```python
def run_bank(mean_interarrival, mean_service, max_time=480.0, seed=42):
    def prepare(sim):
        # reset() wipes sim.state, so (re)create our keys on first use.
        sim.state.setdefault("queue", [])            # arrival times; front = next served
        sim.state.setdefault("teller_busy", False)
        sim.state.setdefault("times_in_system", [])  # one entry per finished customer
        sim.state.setdefault("served_arrivals", [])  # arrival order, for the FIFO check

    def arrival(sim, data):
        prepare(sim)
        sim.state["queue"].append(sim.current_time)         # join the back of the line
        if not sim.state["teller_busy"]:                    # teller free -> serve now
            sim.state["teller_busy"] = True
            sim.schedule_event(sim.current_time, start_service)
        gap = random.expovariate(1.0 / mean_interarrival)   # exponential inter-arrival
        next_time = sim.current_time + gap
        if next_time <= sim.max_time:
            sim.schedule_event(next_time, arrival)

    def start_service(sim, data):
        prepare(sim)
        if sim.state["queue"]:
            enter_time = sim.state["queue"].pop(0)          # FIFO: first in, first served
            service_time = random.expovariate(1.0 / mean_service)
            sim.schedule_event(sim.current_time + service_time,
                               finish_service, data={"enter": enter_time})

    def finish_service(sim, data):
        prepare(sim)
        sim.state["times_in_system"].append(sim.current_time - data["enter"])
        sim.state["served_arrivals"].append(data["enter"])
        if sim.state["queue"]:                              # next customer, same teller
            sim.schedule_event(sim.current_time, start_service)
        else:
            sim.state["teller_busy"] = False                # teller goes idle

    sim = DiscreteEventSimulation(
        max_time=max_time,
        initial_events=[(0.0, arrival, None)],
        time_step=1.0,
        random_seed=seed,
    )
    sim.run_simulation()
    return sim
```

2. **Run one working day (480 minutes)** with a customer every 5 minutes on average and 3-minute average service.

```python
sim = run_bank(mean_interarrival=5.0, mean_service=3.0, max_time=480.0, seed=42)
times = sim.state["times_in_system"]
print("Customers served:", len(times))
print("Mean time in system: %.2f minutes" % statistics.mean(times))
```

3. **Validate the FIFO discipline.** Customers must be served in arrival order. Check that the arrival times of *served* customers are non-decreasing — if any later-served customer has an *earlier* arrival time, FIFO was violated.

```python
order = sim.state["served_arrivals"]
fifo_ok = all(order[i] <= order[i + 1] for i in range(len(order) - 1))
print("FIFO order preserved:", fifo_ok)
```

4. **Sweep the arrival rate and watch congestion climb.** Re-run for several inter-arrival times. As customers arrive faster (smaller gap) the teller saturates and the time in system rises sharply. Compare each result to the M/M/1 formula for mean time in system, $W = 1/(\mu - \lambda)$.

```python
MEAN_SERVICE = 3.0
mu = 1.0 / MEAN_SERVICE
print(f"{'inter-arrival':>13}{'rho':>7}{'W_sim':>9}{'W_formula':>11}")
for ia in [8.0, 6.0, 5.0, 4.5, 4.2]:
    lam = 1.0 / ia
    run = run_bank(mean_interarrival=ia, mean_service=MEAN_SERVICE,
                   max_time=8000.0, seed=42)
    W_sim = statistics.mean(run.state["times_in_system"])
    W_formula = 1.0 / (mu - lam)
    print(f"{ia:>13}{lam / mu:>7.3f}{W_sim:>9.2f}{W_formula:>11.2f}")
```

5. **Interpret.** Confirm two things: the mean time in system **grows** as the arrival rate rises, and it tracks $W = 1/(\mu - \lambda)$. The system is only stable while $\rho = \lambda/\mu < 1$; at or above that, arrivals outrun service and the queue runs away.

## Things to explore
- Hold the arrival rate fixed and **double the teller speed** (halve `mean_service`). By what factor does the mean time in system drop? Does the formula predict the same factor?
- Run the *same* configuration with five different seeds. How much does the mean time in system vary near $\rho = 0.9$ versus near $\rho = 0.4$? Why is the high-load run so much noisier?
- Plot a histogram of individual times in system at $\rho = 0.8$. Is it symmetric, or does it have a long right tail?
- Push $\rho$ above 1 (e.g. inter-arrival 2.5, service 3.0). What happens to the mean time in system as you lengthen `max_time`?

## Extension ideas
- Add a **second teller**: model two parallel servers sharing one queue and compare the mean time in system to the single teller at the same total load.
- Use **deterministic** service times (replace `expovariate` with a constant) to turn the M/M/1 into an M/D/1, and compare the mean time in system.
- Model a **lunch break**: make the teller unavailable for a 30-minute window and measure how the queue spikes during the break and drains afterward.

## Assessment criteria
- [ ] The simulation is reproducible (`random_seed=42`) and reports a sensible number of served customers and a mean time in system.
- [ ] **FIFO validation:** served customers are processed in non-decreasing arrival order (the check prints `True`).
- [ ] **Monotonicity validation:** the mean time in system rises as the arrival rate increases across the sweep.
- [ ] **Analytic validation:** the simulated mean time in system is within ~15% of the M/M/1 formula $W = 1/(\mu - \lambda)$ at each load level, and the student names the stability condition $\rho = \lambda/\mu < 1$.
- [ ] The student explains *why* the time in system rises non-linearly near capacity and what that means for the bank's staffing.
- [ ] Code is readable: events are small, named clearly, and use the engine's `schedule_event` / `sim.state` API correctly — including the `data=` keyword when passing event data.
