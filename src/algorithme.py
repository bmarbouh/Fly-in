from src.parsing import DroneMap
from typing import Dict, List
import heapq


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
        
        if name in self.dronemap.zones:
            return self.dronemap.zones[name]
        
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
                self.adjuncy[conn.zone_a].append(edge_to_b)
            
            if zone_obj_a.mode != "blocked":
                edge_to_a = Edge(to_zone=zone_obj_a, max_link_capacity=conn.max_link_capacity)
                self.adjuncy[conn.zone_b].append(edge_to_a)



class Dijkstra_path_find:
    def __init__(self, graph: Graph, start_name, end_name):
        self.graph = graph
        self.start_name = start_name
        self.end_name = end_name
        self.distances = {}
        self.parent = {}
        self.neighbors_visit = []
    
    
    def path_finder(self):
        
        for zone_name in self.graph.adjuncy.keys():
            self.distances[zone_name] = float('inf')
            self.parent[zone_name] = None
        
        self.distances[self.start_name] = 0
        
        self.neighbors_visit[self.start_name] = (0, self.start_name)
        
        heapq.heapify(self.neighbors_visit)
        
        while self.neighbors_visit:
            ...
            