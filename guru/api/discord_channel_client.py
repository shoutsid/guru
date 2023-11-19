from .kafka.producer import trigger_to_topic
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


@trigger_to_topic('discord_channel')
def create_channel(channel_data):
    channel_data["id"] = channel_data["discord_id"]
    return channel_data


@trigger_to_topic('discord_channel')
def update_channel(channel_id, channel_data):
    channel_data['id'] = channel_id
    return channel_data

def delete_channel(channel_id):
    try:
        url = f"{BASE_URL}/discord_channels/{channel_id}.json"
        response = SESSION.delete(url)
        response.raise_for_status()
        return response.status_code
    except requests.exceptions.RequestException as e:
        print(f'Error occurred while deleting a channel: {e}')
        return None
