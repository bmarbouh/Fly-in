*This project has been created as part of the 42 curriculum by bmarbouh.*

# Fly-in

## Description

Fly-in routes a fleet of drones from a shared start zone to a shared end
zone across a network of connected zones, respecting per-zone and
per-connection capacity limits and per-zone movement costs. Instead of
giving every drone the same path, each drone is planned individually and
scheduled to avoid conflicts with drones planned before it, minimizing the
total number of turns needed to deliver the whole fleet.

## Instructions

```bash
make install
make run map=maps/easy/01_linear_path.txt
```

Other targets: `make debug`, `make lint`, `make clean`.

## Algorithm Explanation

Pathfinding is a time-aware Dijkstra: instead of searching over plain zone
names, it searches over `(zone, turn)` states, so being at a zone at turn 3
and being there at turn 4 are treated as different situations. From each
state, a drone can either move to a neighbor (1 turn for normal/priority,
2 turns for restricted, based on the destination's type) or wait one turn
in place. A shared `BookTable` tracks, for every zone and connection, which
turns are already reserved.

Drones are scheduled one at a time: each drone's search checks its moves
against the current `BookTable`, and once a path is found it is
immediately reserved before the next drone is planned. This means later
drones automatically route around earlier drones — either via an
alternate path or a short wait — without any conflict ever being explicit.
Before scheduling starts, a BFS reachability check confirms a path exists
at all between start and end, so an unsolvable map fails immediately with
a clear error instead of hanging.

## Visual Representation

The terminal output prints one line per turn, colorizing each `D<ID>`
token consistently per drone and showing restricted-zone in-transit turns
as `D<ID>-zoneA-zoneB`, so a drone's full journey — including multi-turn
moves — is visible at a glance instead of just a flat move list.

## Example

Map `maps/easy/01_linear_path.txt` (2 drones, straight line to the goal):

```
[Turn 01] D1-waypoint1
[Turn 02] D1-waypoint2 D2-waypoint1
[Turn 03] D1-goal D2-waypoint2
[Turn 04] D2-goal
```

## Resources

- [Dijkstra's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
- [Python `heapq` documentation](https://docs.python.org/3/library/heapq.html)
- [mypy documentation](https://mypy.readthedocs.io/)

**AI usage**: I used AI to get guidance on my project's design.