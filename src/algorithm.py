
from src.parsing import DroneMap
from src.parsing import DroneMap
import heapq

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
            
        return self.graph


class Dijkstra:
    def __init__(self, start_name, end_name, graph, dronemap: DroneMap):
        self.start_name = start_name
        self.end_name = end_name
        self.graph = graph
        self.dronemap = dronemap
        self.distance = {item:float('inf') for item in self.graph}
        self.parent = {item:None for item in self.graph}
        self.queue = []
    
    
    def get_cost(self, edge):
        zone_name = edge.to_zone
        
        if zone_name == self.dronemap.end_hub.name:
            mode = self.dronemap.end_hub.mode
        
        if zone_name == self.dronemap.start_hub.name:
            mode = self.dronemap.start_hub.mode
        
        for name, zone in self.dronemap.zones.items():
            if zone_name == name:
                mode = zone.mode
        if mode in ["normal", "priority"]:
            return 1
        elif mode == "restricted":
            return 2
    
    def path_finding(self):
        
        self.distance[self.dronemap.start_hub.name] = 0
        self.queue.append((0, 'start'))
        heapq.heapify(self.queue)
        
        while self.queue:
            current_dis, current_zone = heapq.heappop(self.queue)
            
            if current_dis > self.distance[current_zone]:
                continue
            
            if current_zone == self.dronemap.end_hub.name:
                break
            
            for edges in self.graph[current_zone]:
                edge_cost = self.get_cost(edges)
                new_dis = current_dis + edge_cost
                
                if new_dis < self.distance[edges.to_zone]:
                    self.distance[edges.to_zone] = new_dis
                    self.parent[edges.to_zone] = current_zone
                    heapq.heappush(self.queue, (new_dis, edges.to_zone))
                # print(f"queue : {self.queue}")
                # print(f"Distance : {self.distance}")
                # print(f"Parent : {self.parent}")
                # print("="  * 10)
        
        
        path = []
        
        curr = self.end_name
        while curr is not None:
            path.append(curr)
            curr = self.parent[curr]
        
        path.reverse()
        return path

# maps/easy/01_linear_path.txt