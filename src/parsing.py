from typing import List, Dict, Optional


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
        self.path = path
        self.drone_map = DroneMap()
    
    def skip_comments(self, line: str):
        if "#" in line:
            line = line.split("#")[0]
        return line
    
    def parse_metadata(self, meta_str :str):
        metadata: Dict[str ,str] = {}
        clean_meta = meta_str.strip("[]")
        for item in clean_meta.split():
            k, v = item.split("=", 1)
            metadata[k.strip()] = v.strip()
        return metadata
    
    def Parser(self):
        try:
            with open(self.path, "r") as file:
                data: List[str] = file.read().splitlines()
        except Exception:
            raise ValueError("[ERROR]: while opening file")
        
        if not data:
            raise ValueError("[ERROR]: file cannot be empty")
        
        is_first = True
        
        for line in data:
            line = self.skip_comments(line)
            
            if not line:
                continue
            
            if is_first:
                if not line.startswith("nb_drones"):
                    raise ValueError("[ERROR]: Lines must be start with nb_drones")
                try:
                    self.drone_map.nb_drones = int(line.split(":")[1].strip())
                    is_first = False
                except Exception:
                    raise ValueError(f"[ERROR]: Invalid Syntax {line}")
                continue
            
            if ":" not in line:
                raise ValueError(f"[ERROR]: Invalid Syntax {line}")
            
            prefex, content = line.split(":", 1)
            prefex = prefex.strip()
            content: str = content.strip()
            
            if prefex in ["hub", "start_hub", "end_hub"]:
                meta_str = ""
                
                if "[" in content and content.endswith("]"):
                    start_idx = content.index("[")
                    meta_str = content[start_idx:]
                    content = content[:start_idx]
                
                parts = content.split()
                
                if len(parts) < 3:
                    raise ValueError("[ERROR]: Incompleted Data")
                
                name, x_str, y_str = parts[0], parts[1], parts[2]
                
                meta_dict = self.parse_metadata(meta_str) if meta_str else {}
                
                z_type = meta_dict.get("zone", "normal")
                color = meta_dict.get("color", "none")
                
                if prefex in ["start_hub", "end_hub"]:
                    max_dr = 1
                else:
                    max_dr = int(meta_dict.get("max_drones", 1))
                
                zone_obj = Zone(name, int(x_str), int(y_str), color, max_dr, z_type)
                
                self.drone_map.zones[name] = zone_obj
                
                if prefex == "start_hub":
                    if self.drone_map.start_hub is not None:
                        raise ValueError("[ERROR]: must write start_hub just one time")
                    self.drone_map.start_hub = zone_obj
                elif prefex == "end_hub":
                    if self.drone_map.end_hub is not None:
                        raise ValueError("[ERROR]: must write end_hub just one time")
                    self.drone_map.end_hub = zone_obj
                
            elif prefex == "connection":
                meta_str = ""
                if "[" in content and content.endswith("]"):
                    start_idx = content.index("[")
                    meta_str = content[start_idx:]
                    content = content[:start_idx]
                
                if "-" not in content:
                    raise ValueError("[ERROR]: Invalid Connection")
                
                zone_a, zone_b = content.split("-", 1)
                zone_a, zone_b = zone_a.strip(), zone_b.strip()
                
                meta_dict = self.parse_metadata(meta_str) if meta_str else {}
                max_link_capacity = meta_dict.get("max_link_capacity", 1)
                
                for conn in self.drone_map.connections:
                    if (conn.zone_a == zone_a and conn.zone_b == zone_b) or (conn.zone_a == zone_b and conn.zone_b == zone_a):
                        raise ValueError("[ERROR]: Connection are duplicated")
                self.drone_map.connections.append(Connections(zone_a, zone_b, max_link_capacity))
        if not self.drone_map.end_hub or not self.drone_map.start_hub:
            raise ValueError("[ERROR]: You must include start_hub and end_hub")
        return self.drone_map