from src.parsing import Parsing
import json
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
        main()
