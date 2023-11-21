import json

from client import client


def import_data(json_file, class_name):
    with open(json_file, 'r') as file:
        data = json.load(file)
        for record in data:
            client.data_object.create(
                data_object=record, class_name=class_name)

# Example of importing data for the 'Agent' class
# import_data('agent_data.json', 'Agent')
