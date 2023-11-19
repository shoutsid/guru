import logging
from .kafka.producer import trigger_to_topic
from .utils import BASE_URL, SESSION, requests

def list_assistants():
    try:
        url = f"{BASE_URL}/open_ai_assistants.json"
        response = SESSION.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f'Error occurred while listing assistants: {e}')
        return None


def get_assistant(assistant_id):
    try:
        url = f"{BASE_URL}/open_ai_assistants/{assistant_id}.json"
        response = SESSION.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f'Error occurred while retrieving an assistant: {e}')
        return None


@trigger_to_topic('open_ai_assistant')
def create_assistant(assistant_data):
    logging.info(f"123assistant_data: {assistant_data}")
    return assistant_data


@trigger_to_topic('open_ai_assistant')
def update_assistant(assistant_id, assistant_data):
    logging.info(f"123assistant_data: {assistant_data}")
    return assistant_data


def delete_assistant(assistant_id):
    try:
        url = f"{BASE_URL}/open_ai_assistants/{assistant_id}.json"
        response = SESSION.delete(url)
        response.raise_for_status()
        return response.status_code
    except requests.exceptions.RequestException as e:
        print(f'Error occurred while deleting an assistant: {e}')
        return None
