import argparse
from src.parsing import Parsing
from src.algorithm import Graph, Scheduler
from src.simulator import Simulator, BookTable


def main() -> None:
    """
    Reads the map file given via --map, builds the graph and reservation
    table, schedules every drone's path through the Scheduler, then hands
    the resulting paths to the Simulator to print the turn-by-turn output.
    """
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        "--map",
        type=str,
        default="maps/challenger/01_the_impossible_dream.txt",
        help="Path to the map file"
    )

    args = arg_parser.parse_args()

    file = args.map

    data = Parsing(file)
    dronemap = data.parser()

    graph = Graph(dronemap)
    book_table = BookTable(dronemap)

    scheduler = Scheduler(graph, dronemap, book_table)
    paths = scheduler.scheduler()

    Simulator(paths, dronemap).run_sim()


if __name__ == "__main__":
    try:
        main()
    except (Exception, KeyboardInterrupt) as e:
        print(e)
