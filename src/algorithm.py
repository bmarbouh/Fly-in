
from src.parsing import DroneMap
import heapq
from src.simulator import BookTable


class Edge:
    def __init__(self, to_zone, max_link_capacity):
        self.to_zone = to_zone
        self.max_link_capacity = max_link_capacity


class Graph:
    def __init__(self, droneMap: DroneMap):
        self.droneMap = droneMap
        self.graph = {}

        self.build_graph()

    def check_blocked(self, name):
        for name, zone in self.droneMap.zones.items():
            if name == zone.name:
                if zone.mode != "blocked":
                    return 1
        return 0

    def build_graph(self):

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


class Dijkstra:
    def __init__(
        self,
        start_name,
        end_name,
        graph,
        dronemap: DroneMap,
        book_table: BookTable,
        start_turn: int
            ):
        self.start_name = start_name
        self.end_name = end_name
        self.graph = graph
        self.dronemap = dronemap
        self.book_table = book_table
        self.start_turn = start_turn
        self.distance = {}
        self.parent = {}
        self.queue = []

    def get_zone_mode(self, zone_name: str):
        if zone_name == self.dronemap.start_hub.name:
            return self.dronemap.start_hub.mode
        if zone_name == self.dronemap.end_hub.name:
            return self.dronemap.end_hub.mode

        return self.dronemap.zones[zone_name].mode

    def get_cost(self, zone_name: str):
        status = self.get_zone_mode(zone_name)
        if status == "restricted":
            return 2
        return 1

    def path_finder(self):
        start_state = (self.start_name, self.start_turn)
        self.distance[start_state] = self.start_turn

        heapq.heappush(self.queue, (self.start_turn, start_state))

        final_state = None

        while self.queue:
            current_cost, current_state = heapq.heappop(self.queue)
            current_zone, current_turn = current_state

            if current_cost > self.distance.get(current_state, float('inf')):
                continue

            if current_zone == self.end_name:
                final_state = current_state
                break

            for edge in self.graph.get(current_zone, []):
                next_zone = edge.to_zone
                next_zone_cost = self.get_cost(next_zone)
                arrival_turn = next_zone_cost + current_turn

                is_conn_available = self.book_table.is_conn_available(
                    current_zone, next_zone, current_turn + 1
                    )
                is_zone_available = self.book_table.is_zone_available(
                    next_zone, arrival_turn
                    )

                if not is_zone_available or not is_conn_available:
                    continue

                new_state = (next_zone, arrival_turn)

                if arrival_turn < self.distance.get(new_state, float('inf')):
                    self.distance[new_state] = arrival_turn
                    self.parent[new_state] = current_state
                    heapq.heappush(self.queue, (arrival_turn, new_state))

            wait_turn = current_turn + 1
            is_zone_available = self.book_table.is_zone_available(
                current_zone, wait_turn
                )

            if is_zone_available:
                wait_state = (current_zone, wait_turn)

                if wait_turn < self.distance.get(wait_state, float('inf')):
                    self.distance[wait_state] = wait_turn
                    self.parent[wait_state] = current_state
                    heapq.heappush(self.queue, (wait_turn, wait_state))

        if final_state is None:
            return None

        path = []
        current_state = final_state
        start_state = (self.start_name, self.start_turn)

        while current_state != start_state:
            path.append(current_state)
            current_state = self.parent[current_state]

        path.append(start_state)
        path.reverse()
        return path


class Scheduler:
    def __init__(
        self,
        graph: Graph,
        dronemap: DroneMap,
        book_table: BookTable
            ):
        self.graph = graph
        self.dronemap = dronemap
        self.book_table = book_table
        self.paths = {}

    def scheduler(self):
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
