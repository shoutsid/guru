from .kafka.producer import trigger_to_topic
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


@trigger_to_topic('discord_user')
def create_user(user_data):
    user_data["id"] = user_data["discord_id"]
    return user_data


@trigger_to_topic('discord_user')
def update_user(user_id, user_data):
    user_data["id"] = user_id
    return user_data


def delete_user(user_id):
    try:
        url = f"{BASE_URL}/discord_users/{user_id}.json"
        response = SESSION.delete(url)
        response.raise_for_status()
        return response.status_code
    except requests.exceptions.RequestException as e:
        print(f'Error occurred while deleting a user: {e}')
        return None
