from src.parsing import Parsing



    

def main():
    drone_map = input("Chose Your Map: ")
    
    data = Parsing(drone_map)
    data_prs = data.Parser()
    

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
