
class Drone:
    def __init__(self, id, path):
        self.id = id
        self.path = path
        self.position = 0
        self.wait_turn = None
    
    @property
    def current_zone(self):
        return self.path[self.position]
    
    @property
    def next_zone(self):
        if self.position + 1 < len(self.path):
            return self.path[self.position + 1]
        return  None

class Simulator:
    def __init__(self, graph, nb_drones, path):
        self.graph = graph
        self.nb_drones = nb_drones
        self.path = path
        self.drones = [Drone(i + 1, path=path) for i in range(nb_drones)]
        
        self.occupancy = {}
        
        for zone_name in graph.adjuncy.keys():
            self.occupancy[zone_name] = 0
        
        self.occupancy[path[0]] = nb_drones
        
        self.total_turns = 0
        
    def run_simulation(self):
        for drone in self.drones:
            drone.wait_turn = 0
        
        end_zone = self.path[-1]
        
        while any(drone.current_zone != end_zone for drone in self.drones):
            
            self.total_turns += 1
            
            current_link_occupancy = {}
            
            for drone in self.drones:
                if drone.current_zone == end_zone:
                    continue
            
            if drone.wait_turn > 0:
                drone.wait_turn -= 1
                print(f"Drone {drone.id} is waiting inside {drone.current_zone} ({drone.wait_turns} turns left)")
                continue
            
            next_zone_name = drone.next_zone
            
            if next_zone_name is None:
                continue
            
            current_edges = self.graph.adjuncy[drone.current_zone]
            
            for edge in current_edges:
                if edge.to_zone.name == next_zone_name:
                    target_edge = edge
                    break
            
            if not target_edge:
                continue
            
            