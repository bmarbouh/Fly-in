
from src.parsing import DroneMap
from src.parsing import DroneMap
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
        for name , zone in self.droneMap.zones.items():
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
                self.graph[conn.zone_a].append(Edge(conn.zone_b, conn.max_link_capacity))
            
            if self.check_blocked(conn.zone_b):
                self.graph[conn.zone_b].append(Edge(conn.zone_a, conn.max_link_capacity))
            
        # print(self.graph)


class Dijkstra:
    def __init__(self, start_name, end_name, graph, dronemap: DroneMap):
        self.start_name = start_name
        self.end_name = end_name
        self.graph = graph
        self.dronemap = dronemap
        self.distance = {}
        self.parent = {}
        self.queue = []
        
    def path_finding(self):
        
        # for zone in self.dronemap.zones:
        #     print(zone)
        
        while self.queue:
            ...