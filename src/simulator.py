from typing import List, Dict, Tuple, Optional
from src.parsing import DroneMap


class BookTable:
    def __init__(self, dronemap: DroneMap) -> None:
        self.dronemap: DroneMap = dronemap
        self.zones_res: Dict[Tuple[str, int], int] = {}
        self.conn_res: Dict[Tuple[Tuple[str, str], int], int] = {}
        self.conn_caps: Dict[Tuple[str, str], int] = {}
        for conn in dronemap.connections:
            a, b = sorted([conn.zone_a, conn.zone_b])
            self.conn_caps[(a, b)] = conn.max_link_capacity

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
        a, b = sorted([zone_a, zone_b])
        sorted_pair: Tuple[str, str] = (a, b)

        conn_key: Tuple[Tuple[str, str], int] = (sorted_pair, turn)
        conn_nb: int = self.conn_res.get(conn_key, 0)
        link_cap: int = self.conn_caps.get(sorted_pair, 0)

        return bool(conn_nb < link_cap)

    def reserve_zone(self, zone_name: str, turn: int) -> None:
        key: Tuple[str, int] = (zone_name, turn)
        self.zones_res[key] = self.zones_res.get(key, 0) + 1

    def reserve_conn(self, zone_a: str, zone_b: str, turn: int) -> None:
        a, b = sorted([zone_a, zone_b])
        sorted_pair: Tuple[str, str] = (a, b)

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
    COLORS = [
        "\033[91m",
        "\033[92m",
        "\033[93m",
        "\033[94m",
        "\033[95m",
        "\033[96m",
    ]
    RESET = "\033[0m"
    BOLD = "\033[1m"
    GRAY = "\033[90m"

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
                    color = self.COLORS[drone.id % len(self.COLORS)]
                    m_str = f"{color}D{drone.id + 1}-{curr_zone}{self.RESET}"
                    turn_moves.append(m_str)

            if turn_moves:
                header = f"{self.BOLD}{self.GRAY}[Turn {turn:02d}]{self.RESET}"
                print(f"{header} " + " ".join(turn_moves))
