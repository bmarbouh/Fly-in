from src.parsing import Parsing
from src.algorithm import Graph, Dijkstra
from src.simulator import Simulator
import sys

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 -m src <map_file>")
        return
    file = sys.argv[1]
    data = Parsing(file)
    dronemap = data.parser()
    # print("Parsing Return:\n")
    # print(f"nb_drones: {dronemap.nb_drones}")
    # print(f"start_hub: {dronemap.start_hub.name} {dronemap.start_hub.coords} {dronemap.start_hub.color} {dronemap.start_hub.max_drones} {dronemap.start_hub.mode}")
    # for name, zone in dronemap.zones.items():
    #     print(f"{name}: {zone.name} {zone.coords} {zone.color} {zone.max_drones} {zone.mode}")
    # for conn in dronemap.connections:
    #     print(f"{conn.zone_a} {conn.zone_b} max {conn.max_link_capacity}")
    # print("\n")
    graph = Graph(dronemap).build_graph()
    # print(graph)
    path = Dijkstra(dronemap.start_hub.name,
                    dronemap.end_hub.name, graph, dronemap).path_finding()
    print(path)
    # simulation = Simulator(path)


if __name__ == "__main__":
    try:
        main()
    except (Exception, KeyboardInterrupt) as e:
        print(e)