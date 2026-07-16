from src.parsing import Parsing
from src.algorithme import Graph


    

def main():
    drone_map = input("Chose Your Map: ")
    
    data = Parsing(drone_map)
    dronemap = data.parser()
    graph = Graph(dronemap)
    
    for key in graph:
        print(key)

if __name__ == "__main__":
    try:
        main()
    except (Exception, KeyboardInterrupt) as e:
        print(e)