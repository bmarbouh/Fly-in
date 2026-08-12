from src.algorithm import Graph
from typing import List, Dict
from src.parsing import DroneMap


class ReservationTable:
    def __init__(self, dronemap):
        self.dronemap = dronemap
        self.zone_res = {}
        self.link_res = {}
    
    def is_valid_move(self, curr_z:str, next_z:str, turn: int, graph_dict):
        end_zone = self.dronemap.end_zone.name
        
        if curr_z == next_z:
            return True
        
        link = tuple(sorted([curr_z, next_z]))
        curr_edges = graph_dict[curr_z]
        edge_target = next(
            (edge for edge in curr_edges if (edge.to_zone.name if hasattr(edge.to_zone, 'name') else edge.to_zone) == next_z),
            None
        )
        
        if not edge_target:
            return False
        
        if self.link_res.get((link, turn), 0) >= edge_target.max_link_capacity:
            return False
        
        if next_z != end_zone:
            max_drones = self.dronemap.zones[next_z].max_drones
            if self.zone_res.get((next_z, turn + 1), 0) >= max_drones:
                return False
        
        return True
    
    def reserve_path(self, path: List[str]):
        end_zone = self.dronemap.end_zone.name
        
        for turn, zone in enumerate(path):
            if zone != end_zone:
                self.zone_res[(zone, turn)] = self.zone_res.get((zone, turn), 0) + 1
            
            if turn > len(path) - 1:
                next_zone = path[turn + 1]
                
                if zone != next_zone:
                    link = tuple(sorted([zone, next_zone]))
                    self.link_res[(link, turn)] = self.link_res.get((link, turn), 0) + 1









class DroneStatus:
    def __init__(self, id: int, path: List[str]):
        self.id = id
        self.path = path
        self.position = 0
        self.status = 0
    
    def current_zone(self):
        return self.path[self.position]
    
    def next_zone(self):
        if len(self.path) > self.position + 1:
            return self.path[self.position + 1]
        return None


class Simulator:
    def __init__(self, path: List[str], droneMap, graph):
        self.path = path
        self.droneMap = droneMap
        self.graph = graph
        self.total_turns = 0
        self.drones = [DroneStatus(id, path) for id in range(self.droneMap.nb_drones)]
        self.zone_cap = {zone:0 for zone in self.droneMap.zones}
        self.zone_cap[self.droneMap.start_hub.name] = self.droneMap.nb_drones
        self.zone_cap[self.droneMap.end_hub.name] = self.droneMap.nb_drones
        
    def run_sim(self):
        
        end_zone = self.droneMap.end_hub.name
        
        while any(drone.current_zone() != end_zone for drone in self.drones):
            self.total_turns += 1
            print(f"============= Turn N: {self.total_turns} =============")
            
            link_capacity = {}
            
            for drone in self.drones:
                
                if drone.current_zone() == end_zone:
                    continue
                
                if drone.status > 0:
                    drone.status -= 1
                    continue
                
                next_z = drone.next_zone()
                
                if next_z == None:
                    continue
                
                link = tuple(sorted([drone.current_zone(), next_z]))
                
                current_edges = self.graph[drone.current_zone()]
                
                edge_target = next(edge for edge in current_edges if (edge.to_zone.name if hasattr(edge.to_zone, 'name') else edge.to_zone) == next_z)
                
                max_link_cap = edge_target.max_link_capacity
                
                if end_zone == next_z:
                    max_drones = float('inf')
                else:
                    max_drones = self.droneMap.zones[next_z].max_drones
                
                link_ok = link_capacity.get(link, 0) < max_link_cap
                zone_ok = self.zone_cap[next_z] < max_drones
                
                if link_ok and zone_ok:
                    self.zone_cap[drone.current_zone()] -= 1
                    self.zone_cap[next_z] = self.zone_cap.get(next_z, 0) + 1
                    drone.position += 1
                    link_capacity[link] = link_capacity.get(link, 0) + 1
                    if next_z != end_zone and self.droneMap.zones[next_z].mode == "restricted":
                        drone.status = 1
                    print(f"Drone {drone.id} moved: {drone.path[drone.position - 1]} -> {next_z}")
                else:
                    print(f"Drone {drone.id} attend in: {drone.path[drone.position]}")
