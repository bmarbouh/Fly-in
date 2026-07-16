from src.parsing import Parsing
from src.algorithme import Graph, Dijkstra_path_find

    

def main():
    drone_map = input("Chose Your Map: ")
    
    data = Parsing(drone_map)
    dronemap = data.parser()
    graph = Graph(dronemap)
    path = Dijkstra_path_find(graph, dronemap.start_hub.name, dronemap.end_hub.name)

if __name__ == "__main__":
    main()
    # try:
    #     main()
    # except (Exception, KeyboardInterrupt) as e:
    #     print(e)