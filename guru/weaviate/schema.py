import json
from client import client


def create_weaviate_class(client, class_name, properties):
    class_schema = {
        "class": class_name,
        "properties": properties,
        "vectorizer": "text2vec-openai"
    }
    client.schema.create_class(class_schema)


def infer_data_type(value):
    """ Infer the Weaviate data type from a Python data type. """
    if isinstance(value, int):
        return "int"
    elif isinstance(value, float):
        return "number"
    elif isinstance(value, bool):
        return "boolean"
    else:
        return "string"


def generate_properties_from_json(json_file):
    """ Generate a list of properties for a Weaviate class based on a JSON file. """
    properties = []
    with open(json_file, 'r') as file:
        data = json.load(file)
        if data:
            # Analyzing the first record to infer schema
            first_record = data[0]
            for key, value in first_record.items():
                data_type = infer_data_type(value)
                properties.append({"name": key, "dataType": [data_type]})
    return properties


# # Assuming 'client' is already defined and connected to Weaviate
# class_name = "Agent"  # Example class name
# properties = generate_properties_from_json('path_to/agent_data.json')
# create_weaviate_class(client, class_name, properties)
