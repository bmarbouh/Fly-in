from typing import List


class Zone:
    def __init__(self, name, x, y, color="red", max_drones=1, mode="normal"):
        self.name = name
        self.coords = (x, y)
        self.color = color
        self.max_drones = max_drones
        self.mode = mode


class Connections:
    def __init__(self, zone_a, zone_b, max_link_capacity=1):
        self.zone_a = zone_a
        self.zone_b = zone_b
        self.max_link_capacity = max_link_capacity


class DroneMap:
    def __init__(self):
        self.nb_drones = 0
        self.start_hub = None
        self.end_hub = None
        self.zones = {}
        self.connections = []


class Parsing:
    def __init__(self, path):
        self.nb_drones = 0
        self.drone_map = DroneMap()
        self.path = path
        self.data = []

    def open_file(self):
        try:
            with open(self.path, "r") as file:
                self.data = file.read().splitlines()
        except FileNotFoundError:
            raise RuntimeError("[ERROR]: File Not Found")

    def remove_comments(self):
        if not self.data:
            raise RuntimeError("[ERROR]: Maps cannot be empty")

        clean_data = []

        for line in self.data:
            if "#" in line:
                line = line.split("#")[0]
            if not line.strip():
                continue
            clean_data.append(line)
        self.data = clean_data

    def parse_metadata(self, metadata: str, av_meta: List[str]):
        meta_dict = {}
        if not metadata.startswith("["):
            raise RuntimeError("[ERROR]: Invalid metadata format")
        if not metadata.endswith("]"):
            raise RuntimeError("[ERROR]: Invalid metadata format")
        metadata = metadata[1:-1]
        metadata = metadata.split()
        for meta in metadata:
            if "=" not in meta:
                raise RuntimeError("[ERROR]: Invalid metadata format")
            key, value = meta.split("=")
            if key not in av_meta:
                raise RuntimeError(f"[ERROR]: Invalid metadata key: {key}")
            meta_dict[key] = value
        return meta_dict

    def parse_zones(self, line: str):
        zone_name, zone_data = line.split(":", 1)
        zone_data = zone_data.strip()
        zone_data = zone_data.split(' ', 3)
        if len(zone_data) < 3:
            raise RuntimeError("[ERROR]: Invalid zone format")
        try:
            name, x, y = zone_data[0], int(zone_data[1]), int(zone_data[2])
        except ValueError:
            raise RuntimeError("[ERROR]: Invalid zone coordinates")
        if len(zone_data) > 3:
            metadata = self.parse_metadata(
                zone_data[3], ["color", "max_drones", "zone"]
                )

        zone = Zone(
            name,
            x,
            y,
            metadata.get("color", "red"),
            int(metadata.get("max_drones", 1)),
            metadata.get("zone", "normal")
                )

        return zone

    def parse_connections(self, line: str):
        connection_name, connection_data = line.split(":", 1)
        connection_data = connection_data.strip()

        metadata = {}

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

        max_link_capacity = int(metadata.get("max_link_capacity", 1))

        connection = Connections(zone_a, zone_b, max_link_capacity)
        return connection

    def parser(self):
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
                    "start_hub", "end_hub", "hub", "connection"
                        ]:
                    raise RuntimeError(
                        f"[ERROR]: Invalid line type: {line_type}"
                        )
        return self.drone_map
