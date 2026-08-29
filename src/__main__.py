import argparse
from src.parsing import Parsing
from src.algorithm import Graph, Scheduler
from src.simulator import Simulator, BookTable


def main() -> None:
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        "--map",
        type=str,
        default="maps/easy/01_linear_path.txt",
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
