from src.parsing import Parsing



    

def main():
    drone_map = input("Chose Your Map: ")
    
    data = Parsing(drone_map)
    d = data.parser()
    

if __name__ == "__main__":
    # main()
    try:
        main()
    except Exception as e:
        print(e)