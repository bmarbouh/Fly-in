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
        
        self.neighbors_visit = [(0, self.start_name)]
        
        heapq.heapify(self.neighbors_visit)
        
        counter = 1
        
        while self.neighbors_visit:
            print(f"Line {counter}: ")
            print(f"neighbors_visit : {self.neighbors_visit}")
            current_dis, current_node = heapq.heappop(self.neighbors_visit)
            
            print(f"distances: {self.distances}")
            print(f"parent: {self.parent}")
            print("----------------------------------------")
            if current_node == self.end_name:
                break
            
            if current_dis > self.distances[current_node]:
                continue
            
            
            for edge in self.graph.adjuncy[current_node]:
                neighbor_name = edge.to_zone.name
                neighbor_cost = edge.to_zone.mode
                
                
                cost = 2 if neighbor_cost == "restricted" else 1
                
                new_dist = cost + current_dis
                
                if new_dist < self.distances[neighbor_name]:
                    self.distances[neighbor_name] = new_dist
                    self.parent[neighbor_name] = current_node
                    heapq.heappush(self.neighbors_visit, (new_dist, neighbor_name ))
        path = []
        curr = self.end_name
        
        while curr is not None:
            path.append(curr)
            curr = self.parent.get(curr)
            
        path.reverse()
        
        if path and path[0] == self.start_name:
            return path
        return []