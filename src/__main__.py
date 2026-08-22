from src.parsing import Parsing
from src.algorithm import Graph, Scheduler
from src.simulator import Simulator, BookTable
import sys
from src.visualizer import Visualizer


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 -m src <map_file>")
        return

    file = sys.argv[1]
    data = Parsing(file)

    dronemap = data.parser()

    graph = Graph(dronemap)

    book_table = BookTable(dronemap)

    scheduler = Scheduler(graph, dronemap, book_table)

    paths = scheduler.scheduler()

    # Simulator(paths, dronemap).run_sim()
    Visualizer(paths, dronemap).run()

if __name__ == "__main__":
    try:
        main()
    except (Exception, KeyboardInterrupt) as e:
        print(e)
