from .kafka.producer import trigger_to_topic
from .utils import BASE_URL, SESSION, requests

def list_guilds():
    try:
        url = f"{BASE_URL}/discord_guilds.json"
        response = SESSION.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f'Error occurred while listing guilds: {e}')
        return None

def get_guild(guild_id):
    try:
        url = f"{BASE_URL}/discord_guilds/{guild_id}.json"
        response = SESSION.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f'Error occurred while retrieving a guild: {e}')
        return None

@trigger_to_topic('discord_guild')
def create_guild(guild_data):
    return guild_data


@trigger_to_topic('discord_guild')
def update_guild(guild_id, guild_data):
    return guild_data


def delete_guild(guild_id):
    try:
        url = f"{BASE_URL}/discord_guilds/{guild_id}.json"
        response = SESSION.delete(url)
        response.raise_for_status()
        return response.status_code
    except requests.exceptions.RequestException as e:
        print(f'Error occurred while deleting a guild: {e}')
        return None
