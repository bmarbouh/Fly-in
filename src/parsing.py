
class Parsing:
    def file_open(self, path):
        with open(path, "r") as file:
            data =  file.read().splitlines()
        if not data:
            raise ValueError("maps cannot be empty")
        return data
    
    def skip_comment(self, data: list[str]):
        new_list = []
        for line in data:
            if not line.startswith("#") and line != "":
                new_list.append(line)
        return new_list
    
    def prs(self, data: list[str]):
        data_dict = {}
        is_first = 1
        connections = []
        for line in data:
            item = line.split(':')
            if is_first and item[0] != "nb_drones":
                raise ValueError(f"{line} not valid must enter nb_drones at first")
            is_first = 0
            
            if item[0] == "nb_drones":
                parts = line.split(":")
                data_dict[parts[0]] = int(parts[1].strip())
                
            elif item[0] in ["hub", "start_hub", "end_hub"]:
                part = item[1].split(' ', 4)
                hub_name = part[1]
                
                data_dict[hub_name] = {
                    "coords": (int(part[2]), int(part[3])),
                    "metadata": {}
                }
                
                if len(part) > 4 and part[4].strip():
                    meta_data = part[4].strip("[]\n ")
                    meta_data = meta_data.split()
                    for m in meta_data:
                        if "=" in m:
                            p = m.split("=")
                            data_dict[hub_name]['metadata'][p[0]] = p[1]
            elif item[0] == "connection":
                conn = item[1].split()
                conn_dic = {"connection":{}, "metadata" : {}}
                if len(conn) > 1:
                    meta_data = conn[1].strip("[]\n ")
                    meta_data = meta_data.split()
                    for m in meta_data:
                        if "=" in m:
                            p = m.split("=")
                        conn_dic["metadata"][p[0]] = p[1]
                conn_dic["connection"] = conn[0]
                connections.append(conn_dic)
            data_dict["connections"] = connections

        return data_dict
