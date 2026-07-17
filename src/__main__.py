from src.parsing import Parsing
from src.algorithme import Graph, Dijkstra_path_find

    

def main():
    drone_map = input("Chose Your Map: ")
    
    data = Parsing(drone_map)
    dronemap = data.parser()
    print("Parsing Return:\n")
    print(f"nb_drones: {dronemap.nb_drones}")
    print(f"start_hub: {dronemap.start_hub.name} {dronemap.start_hub.coords} {dronemap.start_hub.color} {dronemap.start_hub.max_drones} {dronemap.start_hub.mode}")
    for name, zone in dronemap.zones.items():
        print(f"{name}: {zone.name} {zone.coords} {zone.color} {zone.max_drones} {zone.mode}")
    for conn in dronemap.connections:
        print(f"{conn.zone_a} {conn.zone_b} max {conn.max_link_capacity}")
    graph = Graph(dronemap)
    print("\nGraph Return\n")
    for key, val in graph.adjuncy.items():
        print(f"{key}: {val[0].to_zone.name} {val[0].max_link_capacity}")
    path = Dijkstra_path_find(graph, dronemap.start_hub.name, dronemap.end_hub.name)
    # print(path.path_finder())
    


if __name__ == "__main__":
    try:
        main()
    except (Exception, KeyboardInterrupt) as e:
        print(e)