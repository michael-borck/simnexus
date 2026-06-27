# Modelling a Production Line
**Difficulty**: Intermediate
**Time**: ~60 minutes
**Learning Focus**: Multi-stage discrete-event systems; bottleneck identification and throughput
**Simulator**: DiscreteEventSimulation (registry `DiscreteEvent`)

## Overview
A factory turns raw parts into finished goods through a series of work stations: cut, assemble, paint. Each stage works on one item at a time and hands its output to the next stage's input buffer. The line's overall speed is not the average of its stages — it is dictated by the **slowest** stage, the *bottleneck*. This project builds a serial production line from discrete events and asks two things: which stage limits the output, and can you predict the line's throughput from the stage times alone?

## Setup
```bash
pip install sim-lab matplotlib
```

```python
from sim_lab.core import DiscreteEventSimulation
import random, statistics
```

## Instructions
Each stage holds at most one item; a finished item moves into the next stage's buffer (unlimited size, so no blocking). A `feed` event keeps raw parts flowing in. As in the bank project, `run_simulation()` resets `sim.state`, so every event re-establishes its keys with `setdefault`.

1. **Build the line model.** `processing[i]` is the time stage `i` needs per item. State holds each stage's input buffer, a busy flag, accumulated busy time, the completed-item count, and running totals of the buffer levels (to find where inventory piles up).

```python
def run_line(processing, feed_interval=1.0, max_time=5000.0, seed=42):
    n = len(processing)

    def prepare(sim):
        sim.state.setdefault("buffers", [[] for _ in range(n)])
        sim.state.setdefault("busy", [False] * n)
        sim.state.setdefault("busy_start", [None] * n)
        sim.state.setdefault("busy_time", [0.0] * n)
        sim.state.setdefault("completed", 0)
        sim.state.setdefault("buf_sum", [0.0] * n)
        sim.state.setdefault("buf_count", 0)

    def record_buffers(sim):
        for i in range(n):
            sim.state["buf_sum"][i] += len(sim.state["buffers"][i])
        sim.state["buf_count"] += 1

    def try_start(sim, i):
        # Start stage i if it is idle and an item is waiting in its buffer.
        if not sim.state["busy"][i] and sim.state["buffers"][i]:
            sim.state["busy"][i] = True
            sim.state["busy_start"][i] = sim.current_time
            sim.state["buffers"][i].pop(0)
            sim.schedule_event(sim.current_time + processing[i],
                               finish_stage, data=i)

    def feed(sim, data):
        prepare(sim)
        record_buffers(sim)
        sim.state["buffers"][0].append(sim.current_time)   # raw part arrives
        try_start(sim, 0)
        nxt = sim.current_time + random.expovariate(1.0 / feed_interval)
        if nxt <= sim.max_time:
            sim.schedule_event(nxt, feed)

    def finish_stage(sim, i):
        prepare(sim)
        record_buffers(sim)
        sim.state["busy_time"][i] += sim.current_time - sim.state["busy_start"][i]
        sim.state["busy"][i] = False
        if i == n - 1:                                     # last stage -> product done
            sim.state["completed"] += 1
        else:                                              # pass to the next stage
            sim.state["buffers"][i + 1].append(sim.current_time)
            try_start(sim, i + 1)
        try_start(sim, i)                                  # pull the next part in

    sim = DiscreteEventSimulation(
        max_time=max_time,
        initial_events=[(0.0, feed, None)],
        time_step=1.0,
        random_seed=seed,
    )
    sim.run_simulation()
    return sim
```

2. **Run a three-stage line and measure throughput.** Stage times `[4, 7, 5]` minutes make the 7-minute step the suspect bottleneck.

```python
PROCESSING = [4.0, 7.0, 5.0]
sim = run_line(PROCESSING)
throughput = sim.state["completed"] / sim.max_time
print("Items completed:", sim.state["completed"])
print("Throughput: %.4f items/min" % throughput)
```

3. **Validate throughput against the bottleneck.** In steady state a line cannot produce faster than its slowest stage, so the theoretical throughput is $1/\max(p_i)$.

```python
bottleneck = PROCESSING.index(max(PROCESSING))
print("Bottleneck stage: index %d (%.1f min)" % (bottleneck, max(PROCESSING)))
print("Theoretical throughput 1/max(p): %.4f items/min" % (1.0 / max(PROCESSING)))
print("Measured / theoretical: %.1f%%" % (100 * throughput / (1.0 / max(PROCESSING))))
```

4. **Find the bottleneck from the inventory pattern.** Work-in-progress piles up *before* a bottleneck (the slow stage cannot keep up) and the buffer *after* it runs empty (downstream stages starve). Compute the average level of each buffer and each stage's utilisation.

```python
counts = sim.state["buf_count"]
for i, p in enumerate(PROCESSING):
    avg_items = sim.state["buf_sum"][i] / counts
    util = sim.state["busy_time"][i] / sim.max_time
    print("buffer before stage %d (p=%.0f): avg items=%7.2f   stage util=%.2f"
          % (i, p, avg_items, util))
```
The buffer before the 7-minute stage should be large while the buffer after it is near zero — the fingerprint of the bottleneck.

5. **Confirm the law with a different line.** Change the stage times (for example `[10, 4, 4]`) and re-check that the throughput still equals $1/\max(p_i)$ and that inventory now piles in front of the *new* slowest stage.

## Things to explore
- Make every stage the same speed, e.g. `[5, 5, 5]`. What is the throughput, and do any buffers pile up?
- Add **randomness**: draw each stage time from an exponential distribution with the same mean. Does the throughput change? Does the bottleneck still stand out?
- Add a fourth stage that is only slightly slower than the rest. How sharply does a small imbalance cut throughput?
- Starve the line: set `feed_interval` larger than the first stage's time. Now the *feed*, not a stage, limits output. Verify the throughput equals the feed rate $1/\text{feed\_interval}$.

## Extension ideas
- **Finite buffers (blocking):** cap each inter-stage buffer. When a buffer is full the upstream stage must halt. How does blocking change the throughput and the location of the bottleneck?
- **Parallel machines:** give the bottleneck stage two identical machines. Does the line's throughput rise to match the next-slowest stage?
- **Balance the line:** choose stage times so every stage has the same rate. Measure how much total work-in-process shrinks compared with the unbalanced line at the same throughput.

## Assessment criteria
- [ ] The simulation is reproducible (`random_seed=42`) and reports a completed-item count and a throughput.
- [ ] **Throughput validation:** the measured throughput is within ~3% of $1/\max(p_i)$ for at least two different stage-time sets.
- [ ] **Bottleneck validation:** the student correctly names the slowest stage and shows inventory piling before it (large upstream buffer) and starvation after it (near-empty downstream buffer).
- [ ] The student explains in their own words *why* the slowest stage caps the whole line's output.
- [ ] Code uses the event engine correctly: stages advance via `schedule_event` with `data=`, buffers are plain lists, and the `reset()` state-wipe is handled.
- [ ] The model generalises — the student verifies the throughput law holds for at least one alternative configuration, not just the worked example.
