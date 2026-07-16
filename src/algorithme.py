from src.parsing import DroneMap
from typing import Dict, List



class Edge:
    def __init__(self, to_zone, max_link_capacity):
        self.to_zone = to_zone
        self.max_link_capacity = max_link_capacity

class Graph:
    def __init__(self, dronemap: DroneMap):
        self.dronemap = dronemap
        self.adjuncy: Dict[str, List[Edge]] = {}

        self.build_graph()
    
    def get_zone_by_name(self, name: str):
        if name == self.dronemap.start_hub.name:
            return self.dronemap.start_hub
        if name == self.dronemap.end_hub.name:
            return self.dronemap.end_hub
        
        for zone in self.dronemap.zones:
            if name == zone.name:
                return zone
        
        raise RuntimeError(f"[ERROR]: Zone '{name}' is used in connections but never defined.")
    
    
    
    def build_graph(self):
        if self.dronemap.start_hub:
            self.adjuncy[self.dronemap.start_hub.name] = []
            
        if self.dronemap.end_hub:
            self.adjuncy[self.dronemap.end_hub.name] = []
            
        for zone in self.dronemap.zones:
            self.adjuncy[zone] = []
            
        for conn in self.dronemap.connections:
            zone_obj_a = self.get_zone_by_name(conn.zone_a)
            zone_obj_b = self.get_zone_by_name(conn.zone_b)
            
            if zone_obj_b.mode != "blocked":
                edge_to_b = Edge(to_zone=zone_obj_b, max_link_capacity=conn.max_link_capacity)
                self.adjuncy[zone_obj_a].append(edge_to_b)
            
            if zone_obj_a.mode != "blocked":
                edge_to_a = Edge(to_zone=zone_obj_a, max_link_capacity=conn.max_link_capacity)
                self.adjuncy[zone_obj_b].append(edge_to_a)

