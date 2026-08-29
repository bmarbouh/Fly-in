from typing import List, Dict, Tuple, Optional
from src.parsing import DroneMap


class BookTable:
    def __init__(self, dronemap: DroneMap) -> None:
        self.dronemap: DroneMap = dronemap
        self.zones_res: Dict[Tuple[str, int], int] = {}
        self.conn_res: Dict[Tuple[Tuple[str, str], int], int] = {}
        self.conn_caps: Dict[Tuple[str, str], int] = {
            (
                conn.zone_a if conn.zone_a < conn.zone_b else conn.zone_b,
                conn.zone_b if conn.zone_a < conn.zone_b else conn.zone_a,
            ): conn.max_link_capacity
            for conn in dronemap.connections
        }

    def is_zone_available(self, zone_name: str, turn: int) -> bool:
        if (
            self.dronemap.start_hub is None
            or self.dronemap.end_hub is None
        ):
            return True

        start_name: str = self.dronemap.start_hub.name
        end_name: str = self.dronemap.end_hub.name
        if zone_name in (start_name, end_name):
            return True

        zone_nb: int = self.zones_res.get((zone_name, turn), 0)
        zone_cap: int = self.dronemap.zones[zone_name].max_drones

        if zone_nb >= zone_cap:
            return False
        return True

    def is_conn_available(self, zone_a: str, zone_b: str, turn: int) -> bool:
        sorted_pair: Tuple[str, str] = (
            (zone_a, zone_b) if zone_a < zone_b else (zone_b, zone_a)
        )

        conn_key: Tuple[Tuple[str, str], int] = (sorted_pair, turn)
        conn_nb: int = self.conn_res.get(conn_key, 0)
        link_cap: int = self.conn_caps.get(sorted_pair, 0)

        return bool(conn_nb < link_cap)

    def reserve_zone(self, zone_name: str, turn: int) -> None:
        key: Tuple[str, int] = (zone_name, turn)
        self.zones_res[key] = self.zones_res.get(key, 0) + 1

    def reserve_conn(self, zone_a: str, zone_b: str, turn: int) -> None:
        sorted_pair: Tuple[str, str] = (
            (zone_a, zone_b) if zone_a < zone_b else (zone_b, zone_a)
        )
        conn_key: Tuple[Tuple[str, str], int] = (sorted_pair, turn)
        self.conn_res[conn_key] = self.conn_res.get(conn_key, 0) + 1


class DroneStatus:
    def __init__(self, drone_id: int, path: List[Tuple[str, int]]) -> None:
        self.id: int = drone_id
        self.schedule: List[Tuple[str, int]] = path
        self.timeline: Dict[int, str] = {}

        first_zone, first_turn = path[0]
        self.timeline[first_turn] = first_zone

        for i in range(len(path) - 1):
            zone_a, turn_a = path[i]
            zone_b, turn_b = path[i + 1]
            gap = turn_b - turn_a

            if gap == 2:
                self.timeline[turn_a + 1] = f"{zone_a}-{zone_b}"

            self.timeline[turn_b] = zone_b

    def get_zone_at(self, turn: int) -> Optional[str]:
        return self.timeline.get(turn)


class Simulator:
    def __init__(
        self, paths: Dict[int, List[Tuple[str, int]]], droneMap: DroneMap
    ) -> None:
        self.paths: Dict[int, List[Tuple[str, int]]] = paths
        self.droneMap: DroneMap = droneMap
        self.drones: List[DroneStatus] = [
            DroneStatus(drone_id, path)
            for drone_id, path in paths.items()
        ]

        self.total_turns: int = (
            max(path[-1][1] for path in paths.values() if path)
            if paths
            else 0
        )

    def run_sim(self) -> None:
        for turn in range(1, self.total_turns + 1):
            turn_moves: List[str] = []

            for drone in self.drones:
                prev_zone = drone.get_zone_at(turn - 1)
                curr_zone = drone.get_zone_at(turn)

                if not curr_zone:
                    continue

                if curr_zone != prev_zone:
                    turn_moves.append(f"D{drone.id + 1}-{curr_zone}")

            if turn_moves:
                print(" ".join(turn_moves))
