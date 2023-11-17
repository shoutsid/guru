from .utils import BASE_URL, SESSION, requests

def list_channels():
    try:
        url = f"{BASE_URL}/discord_channels.json"
        response = SESSION.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f'Error occurred while listing channels: {e}')
        return None

def get_channel(channel_id):
    try:
        url = f"{BASE_URL}/discord_channels/{channel_id}.json"
        response = SESSION.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f'Error occurred while retrieving a channel: {e}')
        return None

def create_channel(channel_data):
    try:
        url = f"{BASE_URL}/discord_channels.json"
        headers = {"Content-Type": "application/json"}
        response = SESSION.post(url, json=channel_data, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f'Error occurred while creating a channel: {e}')
        return None

def update_channel(channel_id, channel_data):
    try:
        url = f"{BASE_URL}/discord_channels/{channel_id}.json"
        headers = {"Content-Type": "application/json"}
        response = SESSION.put(url, json=channel_data, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f'Error occurred while updating a channel: {e}')
        return None

def delete_channel(channel_id):
    try:
        url = f"{BASE_URL}/discord_channels/{channel_id}.json"
        response = SESSION.delete(url)
        response.raise_for_status()
        return response.status_code
    except requests.exceptions.RequestException as e:
        print(f'Error occurred while deleting a channel: {e}')
        return None
