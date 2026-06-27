# M/M/1 vs M/M/c
**Difficulty**: Intermediate
**Time**: ~60 minutes
**Learning Focus**: Server pooling; capacity, mean waiting time, and wait-time variability
**Simulator**: QueueingSimulation (registry `QueueingSystem`)

## Overview
You have $c$ tellers and a stream of customers. Should each teller keep a *separate* line (one M/M/1 queue per teller) or should they all share a *single* line that feeds the first free teller (one M/M/c queue)? Both designs use the same total service capacity $c\mu$ — yet they perform very differently. This is the classic **server-pooling** question, and the answer explains why banks, airports, and supermarkets converged on one shared queue. You will compare the two designs at equal capacity and show that pooling cuts both the *mean* and the *variability* of waiting time.

## Setup
```bash
pip install sim-lab matplotlib
```

```python
from sim_lab.core import QueueingSimulation
import statistics
```

## Instructions
Both designs deploy $c$ servers, each serving at rate $\mu$ — identical total capacity $c\mu$ and identical load $\rho = \lambda/(c\mu)$. They differ only in queue structure:

- **Dedicated (M/M/1 per lane):** the load is split evenly, so each teller runs an independent M/M/1 queue with arrival rate $\lambda/c$. One representative M/M/1 run captures a customer's experience, since all lanes are statistically identical.
- **Pooled (M/M/c):** one shared queue feeds all $c$ servers at the full arrival rate $\lambda$.

Waiting time comes from queue length via Little's Law, $W_q = L_q/\lambda$, using the right $\lambda$ for each design ($\lambda/c$ for dedicated, $\lambda$ for pooled). "Variability" is the spread of that waiting time across repeated independent runs (different seeds) — it reflects how wildly congestion fluctuates.

1. **Set the workload.** Six tellers, each serving at $\mu = 1.0$/min; customers arrive at $\lambda = 4.0$/min (so $\rho = 0.67$, comfortably stable).

```python
LAM = 4.0
MU = 1.0
C = 6
SEEDS = range(40)
```

2. **Measure one design over many seeds.** For each seed, run the queue, read $L_q$, and derive $W_q$. Collect the mean and the spread (standard deviation) of $W_q$ across seeds.

```python
def measure(num_servers, arrival_rate, max_time=3000.0):
    Wqs = []
    for s in SEEDS:
        sim = QueueingSimulation(
            max_time=max_time,
            arrival_rate=arrival_rate,
            service_rate=MU,
            num_servers=num_servers,
            random_seed=s,
        )
        sim.run_simulation()
        Lq = sim.get_statistics().get("avg_queue_length", 0.0)
        Wqs.append(Lq / arrival_rate)         # Little's Law
    return statistics.mean(Wqs), statistics.pstdev(Wqs)
```

3. **Run both designs.** Dedicated: one M/M/1 lane carrying $\lambda/c$ of the load. Pooled: one M/M/c carrying all of $\lambda$. Capacity is $c\mu$ in both cases.

```python
dedicated = measure(num_servers=1, arrival_rate=LAM / C)   # M/M/1, load split
pooled    = measure(num_servers=C, arrival_rate=LAM)       # M/M/c, shared queue

print("Total capacity c*mu = %.1f in both designs" % (C * MU))
print(f"{'design':>10}{'mean Wq':>10}{'std Wq':>10}")
print(f"{'Dedicated':>10}{dedicated[0]:>10.4f}{dedicated[1]:>10.4f}")
print(f"{'Pooled':>10}{pooled[0]:>10.4f}{pooled[1]:>10.4f}")
```

4. **Validate equal capacity and the pooling advantage.** Confirm both designs share the same $\rho = \lambda/(c\mu)$, then check that pooling gives a *lower mean* waiting time **and** a *lower spread*.

```python
rho = LAM / (C * MU)
print("Shared load rho = lambda/(c*mu) = %.3f" % rho)
print("Pooled lower mean wait?      ", pooled[0] < dedicated[0])
print("Pooled lower variability?    ", pooled[1] < dedicated[1])
```

5. **Visualise the difference.** Plot the distribution of $W_q$ across seeds for both designs on the same axes — the dedicated design's spread should sit clearly wider and higher than the pooled design's.

```python
import matplotlib.pyplot as plt

def samples(num_servers, arrival_rate, max_time=3000.0):
    out = []
    for s in SEEDS:
        sim = QueueingSimulation(max_time=max_time, arrival_rate=arrival_rate,
                                 service_rate=MU, num_servers=num_servers, random_seed=s)
        sim.run_simulation()
        out.append(sim.get_statistics().get("avg_queue_length", 0.0) / arrival_rate)
    return out

plt.hist(samples(1, LAM / C), alpha=0.6, label="Dedicated (M/M/1 lanes)")
plt.hist(samples(C, LAM),     alpha=0.6, label="Pooled (M/M/c)")
plt.xlabel("Average waiting time Wq (min)")
plt.ylabel("Runs (out of %d seeds)" % len(SEEDS))
plt.title("Dedicated vs Pooled at equal capacity")
plt.legend()
plt.show()
```

6. **Interpret.** With separate lines, a customer who picks a busy lane is stuck while other tellers sit idle — so waits are long and erratic. The shared queue routes each customer to the *first free* server, smoothing out the bursts. Same capacity, lower mean, lower variance: that is the pooling benefit.

## Things to explore
- Repeat for $c = 2, 3, 4$ tellers (keep $\rho$ near 0.67 by adjusting $\lambda$). Does the pooling advantage grow or shrink as you add servers?
- Hold $c$ fixed and push $\rho$ from 0.5 toward 0.9. Which design's waiting time spreads out faster as the load rises?
- At very light load ($\rho \approx 0.2$), is there still a meaningful difference between the designs? Why or why not?
- How sensitive is the conclusion to the number of seeds? Re-run with 10, 40, and 100 seeds and watch the standard-deviation estimate stabilise.

## Extension ideas
- **Cost model:** assign a cost per minute of customer waiting and a cost per teller. Find the $c$ that minimises total cost for the pooled design, then compare it to the dedicated design's optimum.
- **Reneging:** model impatient customers who leave if they wait too long (approximate by capping `max_queue_length`). How does the pooling advantage change when abandonment is significant?
- **Heterogeneous servers:** approximate one teller being faster than the others by comparing pooled M/M/c runs at different `service_rate`. Does pooling still win when servers are unequal?

## Assessment criteria
- [ ] All runs are reproducible (a fixed `random_seed` per run; the sweep varies it across seeds).
- [ ] **Equal-capacity validation:** the student shows both designs use total capacity $c\mu$ and share the same load $\rho = \lambda/(c\mu)$.
- [ ] **Pooling validation:** the pooled (M/M/c) design produces a *lower mean* waiting time **and** a *lower spread* (standard deviation across seeds) than the dedicated (M/M-1-per-lane) design.
- [ ] **Little's Law:** waiting time is derived correctly as $W_q = L_q/\lambda$, with the right $\lambda$ for each design ($\lambda/c$ for dedicated, $\lambda$ for pooled).
- [ ] The student explains *why* pooling helps (idle servers absorb bursts that would otherwise strand customers in a slow lane).
- [ ] Code is clean: a single `measure` / `samples` helper is reused for both designs, and the comparison is driven by data, not hard-coded numbers.
