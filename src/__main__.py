from src.parsing import Parsing
from src.algorithm import Graph, Dijkstra

def main():
    file = input("Chose Your Map: ")
    
    data = Parsing(file)
    dronemap = data.parser()
    # print("Parsing Return:\n")
    # print(f"nb_drones: {dronemap.nb_drones}")
    # print(f"start_hub: {dronemap.start_hub.name} {dronemap.start_hub.coords} {dronemap.start_hub.color} {dronemap.start_hub.max_drones} {dronemap.start_hub.mode}")
    for name, zone in dronemap.zones.items():
        print(f"{name}: {zone.name} {zone.coords} {zone.color} {zone.max_drones} {zone.mode}")
    # for conn in dronemap.connections:
    #     print(f"{conn.zone_a} {conn.zone_b} max {conn.max_link_capacity}")
    # print("\n")
    graph = Graph(dronemap)
    path = Dijkstra(dronemap.start_hub.name, dronemap.end_hub.name, graph, dronemap)
    print(path.path_finding())


if __name__ == "__main__":
    try:
        main()
    except (Exception, KeyboardInterrupt) as e:
        print(e)