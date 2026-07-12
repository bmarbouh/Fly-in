from src.parsing import Parsing



    

def main():
    drone_map = input("Chose Your Map: ")
    
    data = Parsing(drone_map)
    dronemap = data.parser()
    

if __name__ == "__main__":
    try:
        main()
    except (Exception, KeyboardInterrupt) as e:
        print(e)