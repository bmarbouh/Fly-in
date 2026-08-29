from typing import List, Dict, Tuple, Optional


class Zone:
    def __init__(
        self,
        name: str,
        x: int,
        y: int,
        color: str = "red",
        max_drones: int = 1,
        mode: str = "normal",
    ) -> None:
        self.name: str = name
        self.coords: Tuple[int, int] = (x, y)
        self.color: str = color
        self.max_drones: int = max_drones
        self.mode: str = mode


class Connections:
    def __init__(
        self, zone_a: str, zone_b: str, max_link_capacity: int = 1
    ) -> None:
        self.zone_a: str = zone_a
        self.zone_b: str = zone_b
        self.max_link_capacity: int = max_link_capacity


class DroneMap:
    def __init__(self) -> None:
        self.nb_drones: int = 0
        self.start_hub: Optional[Zone] = None
        self.end_hub: Optional[Zone] = None
        self.zones: Dict[str, Zone] = {}
        self.connections: List[Connections] = []


class Parsing:
    def __init__(self, path: str) -> None:
        self.nb_drones: int = 0
        self.drone_map: DroneMap = DroneMap()
        self.path: str = path
        self.data: List[str] = []

    def open_file(self) -> None:
        try:
            with open(self.path, "r") as file:
                self.data = file.read().splitlines()
        except FileNotFoundError:
            raise RuntimeError("[ERROR]: File Not Found")

    def remove_comments(self) -> None:
        if not self.data:
            raise RuntimeError("[ERROR]: Maps cannot be empty")

        clean_data: List[str] = []

        for line in self.data:
            if "#" in line:
                line = line.split("#")[0]
            if not line.strip():
                continue
            clean_data.append(line)
        self.data = clean_data

    def parse_metadata(
        self, metadata: str, av_meta: List[str]
    ) -> Dict[str, str]:
        meta_dict: Dict[str, str] = {}
        if not metadata.startswith("["):
            raise RuntimeError("[ERROR]: Invalid metadata format")
        if not metadata.endswith("]"):
            raise RuntimeError("[ERROR]: Invalid metadata format")
        metadata = metadata[1:-1]
        metadata_parts: List[str] = metadata.split()
        for meta in metadata_parts:
            if "=" not in meta:
                raise RuntimeError("[ERROR]: Invalid metadata format")
            key, value = meta.split("=")
            if key not in av_meta:
                raise RuntimeError(f"[ERROR]: Invalid metadata key: {key}")
            meta_dict[key] = value
        return meta_dict

    def parse_zones(self, line: str) -> Zone:
        zone_name, zone_data_str = line.split(":", 1)
        zone_data_str = zone_data_str.strip()
        zone_data: List[str] = zone_data_str.split(" ", 3)
        if len(zone_data) < 3:
            raise RuntimeError("[ERROR]: Invalid zone format")
        try:
            name, x, y = zone_data[0], int(zone_data[1]), int(zone_data[2])
        except ValueError:
            raise RuntimeError("[ERROR]: Invalid zone coordinates")

        metadata: Dict[str, str] = {}
        if len(zone_data) > 3:
            metadata = self.parse_metadata(
                zone_data[3], ["color", "max_drones", "zone"]
            )

        zone = Zone(
            name,
            x,
            y,
            metadata.get("color", "red"),
            int(metadata.get("max_drones", "1")),
            metadata.get("zone", "normal"),
        )

        return zone

    def parse_connections(self, line: str) -> Connections:
        connection_name, connection_data = line.split(":", 1)
        connection_data = connection_data.strip()

        metadata: Dict[str, str] = {}

        if "[" in connection_data and connection_data.endswith("]"):
            start_idx = connection_data.index("[")
            meta_str = connection_data[start_idx:]
            connection_data = connection_data[:start_idx].strip()
            metadata = self.parse_metadata(meta_str, ["max_link_capacity"])

        if "-" not in connection_data:
            raise RuntimeError(
                "[ERROR]: Invalid connection format (missing '-')"
            )

        zones = connection_data.split("-", 1)
        zone_a = zones[0].strip()
        zone_b = zones[1].strip()

        max_link_capacity = int(metadata.get("max_link_capacity", "1"))

        connection = Connections(zone_a, zone_b, max_link_capacity)
        return connection

    def parser(self) -> DroneMap:
        self.open_file()
        self.remove_comments()

        is_first_line = True

        for line in self.data:
            if ":" not in line:
                raise RuntimeError("[ERROR]: Invalid line format")
            if is_first_line:
                if not line.startswith("nb_drones"):
                    raise RuntimeError("[ERROR]: First line must be nb_drones")
                self.nb_drones = int(line.split(":")[1])
                self.drone_map.nb_drones = self.nb_drones
                is_first_line = False
            else:
                line_type, line_data = line.split(":", 1)
                if line_type == "start_hub":
                    self.drone_map.start_hub = self.parse_zones(line)
                elif line_type == "end_hub":
                    self.drone_map.end_hub = self.parse_zones(line)
                elif line_type == "hub":
                    zone = self.parse_zones(line)
                    self.drone_map.zones[zone.name] = zone
                elif line_type == "connection":
                    connection = self.parse_connections(line)
                    self.drone_map.connections.append(connection)
                if line_type not in [
                    "start_hub",
                    "end_hub",
                    "hub",
                    "connection",
                ]:
                    raise RuntimeError(
                        f"[ERROR]: Invalid line type: {line_type}"
                    )
        if self.drone_map.end_hub is None:
            raise RuntimeError("[ERROR]: Missing End Hub in this map")
        if self.drone_map.start_hub is None:
            raise RuntimeError("[ERROR]: Missing Start Hub in this map")
        return self.drone_map
