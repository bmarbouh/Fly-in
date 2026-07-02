from src.parsing import Parsing

def parser(drone_map):
    parsing = Parsing()
    data = parsing.file_open(drone_map)
    skip = parsing.skip_comment(data)
    prs = parsing.prs(skip)
    print(prs)

def main():
    drone_map = input("Chose Your Map: ")
    
    data = parser(drone_map)





if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")