





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
        for line in data:
            if is_first and line.split(':')[0] != "nb_drones":
                raise ValueError(f"{line} not valid must enter nb_drones at first")
            is_first = 0
            parts = line.split(":")
            data_dict[parts[0]] = parts[1]
        return data_dict
