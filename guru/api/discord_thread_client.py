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

def create_thread(thread_data):
    try:
        url = f"{BASE_URL}/discord_threads.json"
        headers = {"Content-Type": "application/json"}
        response = SESSION.post(url, json=thread_data, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f'Error occurred while creating a thread: {e}')
        return None

def update_thread(thread_id, thread_data):
    try:
        url = f"{BASE_URL}/discord_threads/{thread_id}.json"
        headers = {"Content-Type": "application/json"}
        response = SESSION.put(url, json=thread_data, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f'Error occurred while updating a thread: {e}')
        return None

def delete_thread(thread_id):
    try:
        url = f"{BASE_URL}/discord_threads/{thread_id}.json"
        response = SESSION.delete(url)
        response.raise_for_status()
        return response.status_code
    except requests.exceptions.RequestException as e:
        print(f'Error occurred while deleting a thread: {e}')
        return None
