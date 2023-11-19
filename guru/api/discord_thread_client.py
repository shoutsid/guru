from .kafka.producer import trigger_to_topic
from .utils import BASE_URL, SESSION, requests

def list_threads():
    try:
        url = f"{BASE_URL}/discord_threads.json"
        response = SESSION.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f'Error occurred while listing threads: {e}')
        return None

def get_thread(thread_id):
    try:
        url = f"{BASE_URL}/discord_threads/{thread_id}.json"
        response = SESSION.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f'Error occurred while retrieving a thread: {e}')
        return None


@trigger_to_topic('discord_thread')
def create_thread(thread_data):
    thread_data["id"] = thread_data["discord_id"]
    return thread_data


@trigger_to_topic('discord_thread')
def update_thread(thread_id, thread_data):
    thread_data["id"] = thread_id
    return thread_data

def delete_thread(thread_id):
    try:
        url = f"{BASE_URL}/discord_threads/{thread_id}.json"
        response = SESSION.delete(url)
        response.raise_for_status()
        return response.status_code
    except requests.exceptions.RequestException as e:
        print(f'Error occurred while deleting a thread: {e}')
        return None
