from .utils import BASE_URL, SESSION, requests


def list_users():
    try:
        url = f"{BASE_URL}/discord_users.json"
        response = SESSION.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f'Error occurred while listing users: {e}')
        return None


def get_user(user_id):
    try:
        url = f"{BASE_URL}/discord_users/{user_id}.json"
        response = SESSION.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f'Error occurred while retrieving a user: {e}')
        return None


def create_user(user_data):
    try:
        url = f"{BASE_URL}/discord_users.json"
        headers = {"Content-Type": "application/json"}
        response = SESSION.post(url, json=user_data, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f'Error occurred while creating a user: {e}')
        return None


def update_user(user_id, user_data):
    try:
        url = f"{BASE_URL}/discord_users/{user_id}.json"
        headers = {"Content-Type": "application/json"}
        response = SESSION.put(url, json=user_data, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f'Error occurred while updating a user: {e}')
        return None


def delete_user(user_id):
    try:
        url = f"{BASE_URL}/discord_users/{user_id}.json"
        response = SESSION.delete(url)
        response.raise_for_status()
        return response.status_code
    except requests.exceptions.RequestException as e:
        print(f'Error occurred while deleting a user: {e}')
        return None
