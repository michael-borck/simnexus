# Game of Life Oscillator Zoo

**Difficulty**: Beginner
**Time**: ~30 minutes
**Learning Focus**: periodic attractors, pattern placement and period detection
**Simulator**: `GameOfLifeSimulation` (registry `"GameOfLife"`)

## Overview

Some Game of Life patterns never grow and never die — they fall into a cycle,
returning to the same shape every fixed number of generations. These are
**oscillators**, the "clocks" of the cellular-automaton world. In this project
you will place each classic oscillator onto its own grid, let it run, and use the
engine's `detect_stable_pattern()` to read off its period. The central question:
*does the simulator recover the textbook periods — blinker at 2, pulsar at 3?*

## Setup

`pip install sim-lab matplotlib`, then import the simulator and the pattern
helpers. `place_pattern(pattern, grid_size, offset)` stamps a 0/1 array onto a
zeroed grid; `PATTERNS` is the name → array catalogue, and `GameOfLifeSimulation`
is a thin wrapper that calls `place_pattern(PATTERNS[pattern], grid_size, offset)`
for you when you pass `pattern=` and `offset=`:

```python
import numpy as np
from sim_lab.core import GameOfLifeSimulation, place_pattern, PATTERNS
```

## Instructions

1. **Place a blinker and read its period.** A blinker is a row of three live
   cells. Run it long enough for the cycle to be detectable, then ask the engine
   for the cycle length (`detect_stable_pattern()` returns `0` for a still life,
   the period `L` for an oscillator, or `None`):

   ```python
   sim = GameOfLifeSimulation(
       grid_size=(15, 15),
       pattern="blinker",
       offset=(7, 6),
       days=20,
       boundary="periodic",
       random_seed=42,
   )
   sim.run_simulation()
   print("blinker period:", sim.detect_stable_pattern())   # -> 2
   ```

2. **See how `offset` maps to `place_pattern`.** Confirm the simulator's grid
   matches a manual placement, so you understand the helper it wraps:

   ```python
   manual = place_pattern(PATTERNS["blinker"], (15, 15), offset=(7, 6))
   print("matches GameOfLife placement?", np.array_equal(
       manual, sim.get_state_at_day(0)))
   ```

3. **Catalogue the oscillators.** Loop over the named patterns, run each on its
   own grid, and record `detect_stable_pattern()` plus the live-cell count (an
   oscillator's population is constant across its cycle — a handy invariant):

   ```python
   zoo = ["block", "beehive", "blinker", "toad", "beacon", "pulsar"]
   for name in zoo:
       s = GameOfLifeSimulation(
           grid_size=(20, 20), pattern=name, offset=(3, 3),
           days=30, boundary="periodic", random_seed=42,
       )
       live = s.run_simulation()
       period = s.detect_stable_pattern()
       kind = "still life" if period == 0 else f"oscillator (period {period})"
       print(f"{name:9s} cells={int(live[-1]):2d}  {kind}")
   ```

4. **Validate against the textbook.** Confirm the engine recovers the known
   periods exactly:

   ```python
   def period_of(name):
       s = GameOfLifeSimulation(
           grid_size=(20, 20), pattern=name, offset=(3, 3),
           days=30, boundary="periodic", random_seed=42,
       )
       s.run_simulation()
       return s.detect_stable_pattern()

   assert period_of("blinker") == 2, "blinker must be period 2"
   assert period_of("toad")    == 2, "toad must be period 2"
   assert period_of("beacon")  == 2, "beacon must be period 2"
   assert period_of("pulsar")  == 3, "pulsar must be period 3"
   assert period_of("block")   == 0, "block is a still life"
   assert period_of("beehive") == 0, "beehive is a still life"
   print("All oscillator periods match theory.")
   ```

5. **Animate one cycle of the pulsar.** Grab its 4 key frames
   (`get_state_at_day(0..3)`) and display them side by side to *see* the period-3
   rhythm. The pulsar always holds 48 live cells — confirm the count is constant
   across the cycle.

## Things to explore

- **Boundary effect.** Re-run the `beacon` with `boundary="fixed"` pushed into a
  corner. Does it still read period 2, or do edge cells break the cycle?
- **Custom period.** Use `place_pattern` to build the pulsar at a non-centred
  offset; does the period survive a translation?
- **Two oscillators.** Stamp a blinker *and* a toad onto one grid by calling
   `place_pattern` twice (adding arrays) and feeding the result to
   `CellularAutomatonSimulation(rule="game_of_life", initial_state=...)`. Do they
   interfere, and what does `detect_stable_pattern()` report then?
- **Bigger clocks.** Look up the `pentadecathlon` shape, build it as an array,
   and verify its period-15 cycle (raise `max_cycle_length`).

## Extension ideas

- **Spaceships.** Run the `glider` and `lwss` patterns on a torus and show their
  live-cell count is constant while the shape translates — a "period" in space
  rather than time.
- **Random soup survivors.** Seed a large random grid and, after it settles, use
  `detect_stable_pattern()` and visual inspection to identify which oscillators
  the debris has left behind.
- **Period scanner.** Generalise the cataloguing loop to estimate the period of
  an arbitrary grid by comparing `get_all_states()` pairwise.

## Assessment criteria

- **Reproducibility** — `random_seed=42` is set on every run; periods are
  identical on re-run.
- **Validation** — the asserts pass: blinker/toad/beacon = period 2, pulsar =
  period 3, block/beehive = still life (0); the manual `place_pattern` grid
  matches the simulator's initial grid.
- **Analysis** — distinguishes still lifes from oscillators, explains *why* an
  oscillator's live-cell count is constant, and notes any boundary effect.
- **Code quality** — uses a loop over named patterns rather than copy-pasted
  blocks; the period check is data-driven via `detect_stable_pattern()`.
