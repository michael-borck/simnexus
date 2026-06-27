# Staffing for a Target Wait Time
**Difficulty**: Intermediate
**Time**: ~50 minutes
**Learning Focus**: Queue stability and the stability boundary; Little's Law for capacity planning
**Simulator**: QueueingSimulation (registry `QueueingSystem`)

## Overview
A call centre receives calls at rate $\lambda$ per minute and each agent serves them at rate $\mu$ per minute. How many agents $c$ do you need so that the average waiting time stays below a service target — and what happens if you staff below the stability limit? This project turns the **M/M/c** queue into a staffing tool: sweep the number of servers, check the stability condition $\rho = \lambda/(c\mu) < 1$, and apply **Little's Law** to turn measured queue length into waiting time.

## Setup
```bash
pip install sim-lab matplotlib
```

```python
from sim_lab.core import QueueingSimulation
```

## Instructions
`QueueingSimulation` is an M/M/c queue built on the discrete-event engine. It records the queue length over time and `get_statistics()` returns `avg_queue_length` — the time-average number of customers waiting, $L_q$. We convert that into the average waiting time with **Little's Law** for the queue, $W_q = L_q / \lambda$.

1. **Set the workload.** Calls arrive at $\lambda = 2.5$/min; each agent serves at $\mu = 1.0$/min. With one or two agents the system cannot keep up.

```python
LAMBDA = 2.5        # arrivals per minute
MU = 1.0            # services per minute per agent
TARGET_WAIT = 0.5   # target average waiting time, in minutes
```

2. **Run one configuration.** Compute the load $\rho = \lambda/(c\mu)$, run the simulation, read off $L_q$, and derive $W_q$.

```python
c = 3
sim = QueueingSimulation(
    max_time=4000.0,
    arrival_rate=LAMBDA,
    service_rate=MU,
    num_servers=c,
    random_seed=42,
)
sim.run_simulation()
stats = sim.get_statistics()
rho = LAMBDA / (c * MU)
Lq = stats.get("avg_queue_length", 0.0)
Wq = Lq / LAMBDA                       # Little's Law: waiting time from queue length
print("c=%d  rho=%.3f  Lq=%.3f  Wq=%.3f min" % (c, rho, Lq, Wq))
```

3. **Sweep the staffing level** and apply Little's Law at each point.

```python
def waiting_time(c, seed=42, max_time=4000.0):
    sim = QueueingSimulation(
        max_time=max_time, arrival_rate=LAMBDA, service_rate=MU,
        num_servers=c, random_seed=seed,
    )
    sim.run_simulation()
    Lq = sim.get_statistics().get("avg_queue_length", 0.0)
    return Lq / LAMBDA, LAMBDA / (c * MU)   # Wq, rho

print(f"{'c':>3}{'rho':>8}{'stable':>9}{'Wq (min)':>11}")
for c in range(1, 6):
    Wq, rho = waiting_time(c)
    print(f"{c:>3}{rho:>8.3f}{str(rho < 1):>9}{Wq:>11.3f}")
```

4. **Find the minimum staffing** that meets the target while staying stable.

```python
stable = [c for c in range(1, 10) if LAMBDA / (c * MU) < 1]
target_min = next(c for c in stable if waiting_time(c)[0] <= TARGET_WAIT)
print("Stability needs c > lambda/mu = %.1f  ->  c >= %d" % (LAMBDA / MU, stable[0]))
print("Smallest c with Wq <= %.1f min: %d" % (TARGET_WAIT, target_min))
```

5. **Prove the stability boundary empirically.** For an unstable config ($\rho \ge 1$) the queue has no steady state: the average queue length *grows* the longer you simulate. Re-run an unstable case at increasing horizons and watch $L_q$ climb.

```python
print("c=2 (rho=%.2f, unstable) -- Lq vs horizon:" % (LAMBDA / (2 * MU)))
for T in [1000, 2000, 4000]:
    sim = QueueingSimulation(max_time=float(T), arrival_rate=LAMBDA,
                             service_rate=MU, num_servers=2, random_seed=42)
    sim.run_simulation()
    print("  T=%5d  Lq=%.1f" % (T, sim.get_statistics().get("avg_queue_length", 0.0)))
```

6. **Interpret.** State the rule: the system is stable only when $\rho = \lambda/(c\mu) < 1$, i.e. you need at least $c > \lambda/\mu$ servers. Among the stable configurations the average waiting time falls as you add servers, so you pick the smallest $c$ that both clears the stability bar and meets the wait target.

## Things to explore
- Find the minimum $c$ for your target. Then raise $\lambda$ by 20%: how many *extra* agents does the new arrival rate demand? Is the relationship linear?
- Verify Little's Law directly from a long run: does $L_q / \lambda$ match the waiting time you would expect at that load? Try it at several values of $\rho$.
- Fix $c$ and sweep $\lambda$ from $0.3 c\mu$ up to $0.99 c\mu$. Plot $W_q$ against $\rho$. Does it blow up toward $1/(1-\rho)$?
- Compare two operating points with the *same* $\rho$ but different $c$ (e.g. $c=2, \lambda=1.0$ vs $c=4, \lambda=2.0$). Is $W_q$ the same?

## Extension ideas
- **Service-level target:** instead of *average* wait, target the fraction of callers who wait under 30 seconds. Estimate this by running many simulations and combining the per-run averages. How much more staffing does an 80%-service-level target demand than an average-wait target?
- **Finite queue:** set `max_queue_length`. Now excess calls are *rejected* instead of waiting forever. Trade off waiting time against rejection rate for a fixed $c$.
- **Time-varying arrivals:** model a lunch rush by running two simulations with different $\lambda$ and concatenating the queue-length series. How should staffing track the load?

## Assessment criteria
- [ ] Each run is reproducible (`random_seed=42`); results are reported as $\rho$, $L_q$, and the Little's-Law waiting time $W_q = L_q/\lambda$.
- [ ] **Stability validation:** the student states $\rho = \lambda/(c\mu) < 1$ and demonstrates that for $\rho \ge 1$ the measured $L_q$ grows with the simulation horizon (no steady state).
- [ ] **Monotonicity validation:** among the stable configurations, $W_q$ decreases as $c$ increases.
- [ ] **Staffing answer:** the student reports the smallest $c$ that is both stable and meets the target wait, and checks it against the bound $c > \lambda/\mu$.
- [ ] **Little's Law:** the student uses $W_q = L_q/\lambda$ correctly and can explain what the identity means physically.
- [ ] Code is clean: a small helper runs one configuration, the sweep reuses it, and parameters are named meaningfully.
