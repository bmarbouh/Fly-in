from src.algorithm import Graph

class Drone:
    def __init__(self, id, path):
        self.id = id
        self.position = 0
        self.path = path
        self.wait_turn = 0
    
    def current_zone(self):
        return self.path[self.position]
    
    def next_zone(self):
        if self.position + 1 > len(self.path):
            return None
        return self.path[self.position + 1]


class Simulator:
    def __init__(self, graph: Graph, nb_drones):
        self.graph = graph
        self.total_turns = 0
        self.drones = None
        self.nb_drones = nb_drones
        self.reserved = {zone:0 for zone in graph}
        self.reserved[graph[0]] = self.nb_drones
    
    def run_sim(self):
        ...