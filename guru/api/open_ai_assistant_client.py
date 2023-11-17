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


def create_assistant(assistant_data):
    try:
        url = f"{BASE_URL}/open_ai_assistants.json"
        headers = {"Content-Type": "application/json"}
        response = SESSION.post(url, json=assistant_data, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f'Error occurred while creating an assistant: {e}')
        return None


def update_assistant(assistant_id, assistant_data):
    try:
        url = f"{BASE_URL}/open_ai_assistants/{assistant_id}.json"
        headers = {"Content-Type": "application/json"}
        response = SESSION.put(url, json=assistant_data, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f'Error occurred while updating an assistant: {e}')
        return None


def delete_assistant(assistant_id):
    try:
        url = f"{BASE_URL}/open_ai_assistants/{assistant_id}.json"
        response = SESSION.delete(url)
        response.raise_for_status()
        return response.status_code
    except requests.exceptions.RequestException as e:
        print(f'Error occurred while deleting an assistant: {e}')
        return None
