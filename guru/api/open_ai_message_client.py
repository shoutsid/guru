from .utils import BASE_URL, SESSION, requests


def list_messages():
    try:
        url = f"{BASE_URL}/open_ai_messages.json"
        response = SESSION.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f'Error occurred while listing messages: {e}')
        return None


def get_message(message_id):
    try:
        url = f"{BASE_URL}/open_ai_messages/{message_id}.json"
        response = SESSION.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f'Error occurred while retrieving a message: {e}')
        return None


def create_message(message_data):
    try:
        url = f"{BASE_URL}/open_ai_messages.json"
        headers = {"Content-Type": "application/json"}
        response = SESSION.post(url, json=message_data, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f'Error occurred while creating a message: {e}')
        return None


def update_message(message_id, message_data):
    try:
        url = f"{BASE_URL}/open_ai_messages/{message_id}.json"
        headers = {"Content-Type": "application/json"}
        response = SESSION.put(url, json=message_data, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f'Error occurred while updating a message: {e}')
        return None


def delete_message(message_id):
    try:
        url = f"{BASE_URL}/open_ai_messages/{message_id}.json"
        response = SESSION.delete(url)
        response.raise_for_status()
        return response.status_code
    except requests.exceptions.RequestException as e:
        print(f'Error occurred while deleting a message: {e}')
        return None
