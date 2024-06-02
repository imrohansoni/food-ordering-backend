import json
from json import JSONDecodeError


def get_variables():
    try:
        with open('output.json', 'r') as json_file:
            json_data = json_file.read()
            data = json.loads(json_data)
            return data
    except FileNotFoundError:
        with open("output.json", 'w'):
            return {}
    except JSONDecodeError:
        return {}


def set_variables(data):
    variables = {
        **get_variables(),
        **data
    }

    json_data = json.dumps(variables, indent=2)

    with open("output.json", "w") as json_file:
        json_file.write(json_data)
