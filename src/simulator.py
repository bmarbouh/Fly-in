from typing import List, Dict, Tuple
from src.parsing import DroneMap


class BookTable:
    def __init__(self, dronemap: DroneMap):
        self.dronemap = dronemap
        self.zones_res = {}
        self.conn_res = {}
        self.conn_caps = {
            tuple(sorted([conn.zone_a, conn.zone_b])): conn.max_link_capacity
            for conn in dronemap.connections
        }

    def is_zone_available(self, zone_name, turn) -> bool:
        start_name = self.dronemap.start_hub.name
        end_name = self.dronemap.end_hub.name
        if zone_name in (start_name, end_name):
            return True

        zone_nb = self.zones_res.get((zone_name, turn), 0)

        zone_cap = self.dronemap.zones[zone_name].max_drones

        if zone_nb >= zone_cap:
            return False
        return True

    def is_conn_available(self, zone_a: str, zone_b: str, turn: int) -> bool:
        sorted_pair = tuple(sorted([zone_a, zone_b]))

        conn_key = (sorted_pair, turn)
        conn_nb = self.conn_res.get(conn_key, 0)

        link_cap = self.conn_caps.get(sorted_pair, 0)

        return conn_nb < link_cap

    def reserve_zone(self, zone_name: str, turn: int) -> None:
        key = (zone_name, turn)
        self.zones_res[key] = self.zones_res.get(key, 0) + 1

    def reserve_conn(self, zone_a: str, zone_b: str, turn: int) -> None:
        conn_key = (tuple(sorted([zone_a, zone_b])), turn)
        self.conn_res[conn_key] = self.conn_res.get(conn_key, 0) + 1


class DroneStatus:
    def __init__(self, drone_id: int, path: List[Tuple[str, int]]):
        self.id = drone_id
        self.schedule = path
        self.timeline: dict = {}

        first_zone, first_turn = path[0]
        self.timeline[first_turn] = first_zone

        for i in range(len(path) - 1):
            zone_a, turn_a = path[i]
            zone_b, turn_b = path[i + 1]
            gap = turn_b - turn_a

            if gap == 2:
                self.timeline[turn_a + 1] = f"{zone_a}-{zone_b}"

            self.timeline[turn_b] = zone_b

    def get_zone_at(self, turn: int):
        return self.timeline.get(turn)


class Simulator:
    def __init__(self, paths: Dict[int, List[Tuple[str, int]]], droneMap):
        self.paths = paths
        self.droneMap = droneMap
        self.drones = [
            DroneStatus(drone_id, path)
            for drone_id, path in paths.items()
        ]

        self.total_turns = max(
            path[-1][1] for path in paths.values() if path
        ) if paths else 0

    def run_sim(self):
        for turn in range(1, self.total_turns + 1):
            turn_moves = []

            for drone in self.drones:
                prev_zone = drone.get_zone_at(turn - 1)
                curr_zone = drone.get_zone_at(turn)

                if not curr_zone:
                    continue

                if curr_zone != prev_zone:
                    turn_moves.append(f"D{drone.id + 1}-{curr_zone}")

            if turn_moves:
                print(" ".join(turn_moves))
