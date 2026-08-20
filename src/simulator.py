# from src.algorithm import Graph
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
        
        if zone_name in (self.dronemap.start_hub.name, self.dronemap.end_hub.name):
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
    def __init__(self, drone_id: int, schedule: List[Tuple[str, int]]):
        self.id = drone_id
        self.schedule = schedule
        self.timeline = {turn: zone for zone, turn in schedule}

    def get_zone_at(self, turn: int) -> str:
        """Returns the zone the drone is in at a specific turn."""
        return self.timeline.get(turn)


class Simulator:
    def __init__(self, schedules: Dict[int, List[Tuple[str, int]]], droneMap):
        self.schedules = schedules
        self.droneMap = droneMap
        self.drones = [
            DroneStatus(drone_id, path) 
            for drone_id, path in schedules.items()
        ]
        
        self.total_turns = max(
            path[-1][1] for path in schedules.values() if path
        ) if schedules else 0

    def run_sim(self):
        end_zone = self.droneMap.end_hub.name

        for turn in range(1, self.total_turns + 1):
            print(f"============= Turn N: {turn} =============")
            
            for drone in self.drones:
                prev_zone = drone.get_zone_at(turn - 1)
                curr_zone = drone.get_zone_at(turn)

                if not curr_zone:
                    continue

                if curr_zone != prev_zone:
                    print(f"Drone {drone.id} moved: {prev_zone} -> {curr_zone}")

                elif curr_zone != end_zone:
                    pass