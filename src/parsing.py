"""Parsing module: reads a map file and builds a validated DroneMap."""
from typing import List, Dict, Tuple, Optional


class Zone:
    """A single zone (node) in the map, with type and capacity metadata."""

    def __init__(
        self,
        name: str,
        x: int,
        y: int,
        color: str = "red",
        max_drones: int = 1,
        mode: str = "normal",
    ) -> None:
        """Create a Zone with a name, coordinates, and optional metadata."""
        self.name: str = name
        self.coords: Tuple[int, int] = (x, y)
        self.color: str = color
        self.max_drones: int = max_drones
        self.mode: str = mode


class Connections:
    """A bidirectional connection between two zones."""

    def __init__(
        self, zone_a: str, zone_b: str, max_link_capacity: int = 1
    ) -> None:
        """Create a connection between zone_a and zone_b."""
        self.zone_a: str = zone_a
        self.zone_b: str = zone_b
        self.max_link_capacity: int = max_link_capacity


class DroneMap:
    """Holds the fully parsed map: drone count, zones, and connections."""

    def __init__(self) -> None:
        """Initialize an empty map with no zones or connections yet."""
        self.nb_drones: int = 0
        self.start_hub: Optional[Zone] = None
        self.end_hub: Optional[Zone] = None
        self.zones: Dict[str, Zone] = {}
        self.connections: List[Connections] = []


class Parsing:
    """Reads a map file from disk and builds a validated DroneMap."""

    def __init__(self, path: str) -> None:
        """Store the map file path and prepare empty parsing state."""
        self.nb_drones: int = 0
        self.drone_map: DroneMap = DroneMap()
        self.path: str = path
        self.data: List[str] = []
        self.seen_connections: set = set()

    def open_file(self) -> None:
        """Read the map file into self.data, one line per entry."""
        try:
            with open(self.path, "r") as file:
                self.data = file.read().splitlines()
        except FileNotFoundError:
            raise RuntimeError("[ERROR]: File Not Found")

    def remove_comments(self) -> None:
        """Strip '#' comments and blank lines from self.data."""
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
        """Parse a "[key=value ...]" block into a dictionary."""
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
        """Parse a hub/start_hub/end_hub line into a Zone instance."""
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

        if int(metadata.get("max_drones", "1")) <= 0:
            raise RuntimeError("[ERROR]: Invalid Meta data max drone must > 0")
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
        """Parse a connection line into a Connections instance."""
        connection_name, connection_data = line.split(":", 1)
        connection_data = connection_data.strip()

        parts = connection_data.split(" ", 1)
        connection_data = parts[0]

        metadata: Dict[str, str] = {}
        if len(parts) > 1:
            metadata = self.parse_metadata(
                parts[1].strip(), ["max_link_capacity"]
            )

        if "-" not in connection_data:
            raise RuntimeError(
                "[ERROR]: Invalid connection format (missing '-')"
            )

        zones = connection_data.split("-", 1)
        zone_a = zones[0].strip()
        zone_b = zones[1].strip()

        max_link_capacity = int(metadata.get("max_link_capacity", "1"))
        if max_link_capacity <= 0:
            raise RuntimeError("[ERROR]: Invalid Meta data max drone must > 0")
        connection = Connections(zone_a, zone_b, max_link_capacity)
        return connection

    def _check_all_zones_connected(self) -> None:
        """Raise an error if any zone has no connection at all."""
        connected_names: set[str] = set()
        for conn in self.drone_map.connections:
            connected_names.add(conn.zone_a)
            connected_names.add(conn.zone_b)

        all_names: set[str] = set(self.drone_map.zones.keys())
        if self.drone_map.start_hub is not None:
            all_names.add(self.drone_map.start_hub.name)
        if self.drone_map.end_hub is not None:
            all_names.add(self.drone_map.end_hub.name)

        isolated = sorted(all_names - connected_names)
        if isolated:
            raise RuntimeError(
                f"[ERROR]: The following zone(s) have no connection at all: "
                f"{', '.join(isolated)}"
            )

    def parser(self) -> DroneMap:
        """Parse the whole map file and return the validated DroneMap."""
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
                if self.nb_drones <= 0:
                    raise RuntimeError("[ERROR]: nb_drones must be positive")
                self.drone_map.nb_drones = self.nb_drones
                is_first_line = False
            else:
                line_type, line_data = line.split(":", 1)
                if line_type == "start_hub":
                    if self.drone_map.start_hub is not None:
                        raise RuntimeError(
                            "[ERROR]: Multiple start_hub definitions found"
                                )
                    self.drone_map.start_hub = self.parse_zones(line)
                elif line_type == "end_hub":
                    if self.drone_map.end_hub is not None:
                        raise RuntimeError(
                            "[ERROR]: Multiple end_hub definitions found"
                                )
                    self.drone_map.end_hub = self.parse_zones(line)
                elif line_type == "hub":
                    zone = self.parse_zones(line)
                    if zone.name in self.drone_map.zones:
                        raise RuntimeError(
                            f"[ERROR]: Duplicate zone name '{zone.name}'"
                        )
                    if (
                        self.drone_map.start_hub is not None
                        and zone.name == self.drone_map.start_hub.name
                    ) or (
                        self.drone_map.end_hub is not None
                        and zone.name == self.drone_map.end_hub.name
                    ):
                        raise RuntimeError(
                            f"[ERROR]: Zone '{zone.name}' "
                            "collides with start/end hub name"
                        )
                    self.drone_map.zones[zone.name] = zone
                elif line_type == "connection":
                    connection = self.parse_connections(line)
                    known_names = set(self.drone_map.zones.keys())
                    if self.drone_map.start_hub is not None:
                        known_names.add(self.drone_map.start_hub.name)
                    if self.drone_map.end_hub is not None:
                        known_names.add(self.drone_map.end_hub.name)
                    if connection.zone_a not in known_names:
                        raise RuntimeError(
                            f"[ERROR]: Connection references undefined zone "
                            f"'{connection.zone_a}'"
                        )
                    if connection.zone_b not in known_names:
                        raise RuntimeError(
                            f"[ERROR]: Connection references undefined zone "
                            f"'{connection.zone_b}'"
                        )

                    a, b = sorted([connection.zone_a, connection.zone_b])
                    conn_key = (a, b)
                    if conn_key in self.seen_connections:
                        raise RuntimeError(
                            f"[ERROR]: Duplicate connection between "
                            f"'{connection.zone_a}' and '{connection.zone_b}'"
                        )
                    self.seen_connections.add(conn_key)

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
        self._check_all_zones_connected()
        return self.drone_map
