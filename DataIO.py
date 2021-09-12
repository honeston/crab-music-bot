import json


def save(data,name = "default"):
    file_path = "./savedata.json"
    json_data = {}
    with open(file_path, "r") as json_file:
        json_data = json.load(json_file)

    json_data['musiclist'][name] = data

    with open(file_path, 'w') as outfile:
        json.dump(json_data, outfile, indent=4)

def load(name = "default"):
    file_path = "./savedata.json"
    with open(file_path, "r") as json_file:
        json_data = json.load(json_file)
        if name in json_data["musiclist"]:
            return json_data["musiclist"][name]
        return {}
