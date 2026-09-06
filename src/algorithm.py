"""Graph, time-aware Dijkstra, and multi-drone scheduling logic."""
from src.parsing import DroneMap
from typing import Optional
from src.simulator import BookTable
import heapq
from collections import deque


class Edge:
    """A directed link from one zone to a neighboring zone."""

    def __init__(self, to_zone: str, max_link_capacity: int) -> None:
        """Store the destination zone and this link's capacity."""
        self.to_zone = to_zone
        self.max_link_capacity = max_link_capacity


class Graph:
    """Adjacency-list graph built from a DroneMap's connections."""

    def __init__(self, droneMap: DroneMap) -> None:
        """Store the map and build the adjacency list immediately."""
        self.droneMap = droneMap
        self.graph: dict[str, list[Edge]] = {}
        self.build_graph()

    def check_blocked(self, name: str) -> bool:
        """Return True if the named zone exists and is not blocked."""
        if (
            self.droneMap.start_hub is not None
            and name == self.droneMap.start_hub.name
        ):
            return bool(self.droneMap.start_hub.mode != "blocked")
        if (
            self.droneMap.end_hub is not None
            and name == self.droneMap.end_hub.name
        ):
            return bool(self.droneMap.end_hub.mode != "blocked")

        zone = self.droneMap.zones.get(name)
        if zone is None:
            return False
        return bool(zone.mode != "blocked")

    def build_graph(self) -> dict[str, list[Edge]]:
        """Build and return the adjacency list from all connections."""
        for conn in self.droneMap.connections:
            self.graph[conn.zone_a] = []
            self.graph[conn.zone_b] = []

        for conn in self.droneMap.connections:
            if self.check_blocked(conn.zone_a):
                self.graph[conn.zone_a].append(
                    Edge(conn.zone_b, conn.max_link_capacity)
                )
            if self.check_blocked(conn.zone_b):
                self.graph[conn.zone_b].append(
                    Edge(conn.zone_a, conn.max_link_capacity)
                )

        return self.graph

    def is_reachable(self, start: str, end: str) -> bool:
        """Return True if end is reachable from start, ignoring capacity."""
        if start == end:
            return True
        visited = {start}
        queue = deque([start])
        while queue:
            current = queue.popleft()
            for edge in self.graph.get(current, []):
                if edge.to_zone == end:
                    return True
                if edge.to_zone not in visited:
                    visited.add(edge.to_zone)
                    queue.append(edge.to_zone)
        return False


class Dijkstra:
    """Time-aware shortest-path search over (zone, turn) states."""

    def __init__(
        self,
        start_name: str,
        end_name: str,
        graph: dict[str, list[Edge]],
        dronemap: DroneMap,
        book_table: BookTable,
        start_turn: int
    ) -> None:
        """Store search inputs and initialize empty search state."""
        self.start_name = start_name
        self.end_name = end_name
        self.graph = graph
        self.dronemap = dronemap
        self.book_table = book_table
        self.start_turn = start_turn
        self.distance: dict[tuple[str, int], int] = {}
        self.parent: dict[tuple[str, int], tuple[str, int]] = {}
        self.queue: list[tuple[int, tuple[str, int]]] = []

    def get_zone_mode(self, zone_name: str) -> str:
        """Return the mode of the named zone (start, end, or regular)."""
        if zone_name == self.dronemap.start_hub.name:
            return str(self.dronemap.start_hub.mode)
        if zone_name == self.dronemap.end_hub.name:
            return str(self.dronemap.end_hub.mode)

        return str(self.dronemap.zones[zone_name].mode)

    def get_cost(self, zone_name: str) -> int:
        """Return the turn cost of moving into the named zone."""
        status = self.get_zone_mode(zone_name)
        if status == "restricted":
            return 2
        return 1

    def path_finder(
        self
    ) -> Optional[list[tuple[str, int]]]:
        """Find the earliest conflict-free path from start to end."""
        start_state = (self.start_name, self.start_turn)
        self.distance[start_state] = self.start_turn

        heapq.heappush(
            self.queue,
            (self.start_turn, start_state)
        )

        final_state: Optional[tuple[str, int]] = None

        while self.queue:
            current_cost, current_state = heapq.heappop(self.queue)
            current_zone, current_turn = current_state

            if current_cost > self.distance.get(
                current_state,
                float("inf")
            ):
                continue

            if current_zone == self.end_name:
                final_state = current_state
                break

            for edge in self.graph.get(current_zone, []):
                next_zone = edge.to_zone
                next_zone_cost = self.get_cost(next_zone)
                arrival_turn = next_zone_cost + current_turn

                is_conn_available = self.book_table.is_conn_available(
                    current_zone,
                    next_zone,
                    current_turn + 1
                )

                is_zone_available = self.book_table.is_zone_available(
                    next_zone,
                    arrival_turn
                )

                if not is_zone_available or not is_conn_available:
                    continue

                new_state = (next_zone, arrival_turn)

                if arrival_turn < self.distance.get(
                    new_state,
                    float("inf")
                ):
                    self.distance[new_state] = arrival_turn
                    self.parent[new_state] = current_state

                    heapq.heappush(
                        self.queue,
                        (arrival_turn, new_state)
                    )

            wait_turn = current_turn + 1

            is_zone_available = self.book_table.is_zone_available(
                current_zone,
                wait_turn
            )

            if is_zone_available:
                wait_state = (current_zone, wait_turn)

                if wait_turn < self.distance.get(
                    wait_state,
                    float("inf")
                ):
                    self.distance[wait_state] = wait_turn
                    self.parent[wait_state] = current_state

                    heapq.heappush(
                        self.queue,
                        (wait_turn, wait_state)
                    )

        if final_state is None:
            return None

        path: list[tuple[str, int]] = []
        current_state = final_state
        start_state = (self.start_name, self.start_turn)

        while current_state != start_state:
            path.append(current_state)
            current_state = self.parent[current_state]

        path.append(start_state)
        path.reverse()

        return path


class Scheduler:
    """Plans a conflict-free path for every drone, one at a time."""

    def __init__(
        self,
        graph: Graph,
        dronemap: DroneMap,
        book_table: BookTable
    ) -> None:
        """Store the graph, map, and shared reservation table."""
        self.graph = graph
        self.dronemap = dronemap
        self.book_table = book_table
        self.paths: dict[int, list[tuple[str, int]]] = {}

    def scheduler(self) -> dict[int, list[tuple[str, int]]]:
        """Schedule every drone and return each one's final path."""
        start_name = self.dronemap.start_hub.name
        end_name = self.dronemap.end_hub.name
        if not self.graph.is_reachable(
            self.dronemap.start_hub.name, self.dronemap.end_hub.name
                ):
            raise RuntimeError(
                f"[ERROR]: No path exists from "
                f"'{start_name}' to "
                f"'{end_name}' — check for "
                f"missing connections in the map."
            )
        for drone_id in range(self.dronemap.nb_drones):
            start_turn = 0

            dijkstra = Dijkstra(
                self.dronemap.start_hub.name,
                self.dronemap.end_hub.name,
                self.graph.graph,
                self.dronemap,
                self.book_table,
                start_turn,
            )

            path = dijkstra.path_finder()

            if path is None:
                raise RuntimeError(
                    f"Could not find path for drone {drone_id}"
                )

            self.paths[drone_id] = path

            for zone, turn in path:
                self.book_table.reserve_zone(zone, turn)

            for i in range(len(path) - 1):
                current_zone, current_turn = path[i]
                next_zone, next_turn = path[i + 1]

                connection_turn = current_turn + 1

                if current_zone != next_zone:
                    self.book_table.reserve_conn(
                        current_zone,
                        next_zone,
                        connection_turn
                    )

        return self.paths
