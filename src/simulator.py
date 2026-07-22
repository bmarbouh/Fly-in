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
        if self.position + 1 >= len(self.path):
            return None
        return self.path[self.position + 1]


class Simulator:
    def __init__(self, graph: Graph, dronemap, path):
        self.graph = graph
        self.total_turns = 0
        self.path = path
        self.drones = [Drone(id=i, path=path) for i in range(dronemap.nb_drones)]
        self.dronemap = dronemap
        self.reserved = {zone:0 for zone in graph}
        self.reserved[dronemap.start_hub.name] = dronemap.nb_drones
    
    def run_sim(self):
        
        end_zone = self.dronemap.end_hub.name
        
        while any(drone.current_zone() != end_zone for drone in self.drones):
            self.total_turns += 1
            
            print(f"======== Turn {self.total_turns} ========")
            
            current_link_occupancy = {}
            
            for drone in self.drones:
                
                if drone.current_zone == end_zone:
                    continue
                
                if drone.wait_turn > 0:
                    drone.wait_turn -= 1
                    continue
                
                next_zone = drone.next_zone
                
                if next_zone is None:
                    continue