from .utils import BASE_URL, SESSION, requests

# Function to list all open_ai_threads
def list_threads(discord=False, discord_channel=None):
    try:
        url = f"{BASE_URL}/threads.json"
        params = []
        if discord:
            params.append("discord=true")
        if discord_channel is not None:
            params.append(f"discord_channel={discord_channel}")
        if params:
            url += "?" + "&".join(params)

        response = SESSION.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        # Handle exceptions or log errors here
        print(f'Error occurred while listing threads: {e}')
        return None  # You can choose to return None or handle the error as needed

# Function to show a specific open_ai_thread by ID
def get_thread(thread_id):
    try:
        url = f"{BASE_URL}/threads/{thread_id}.json"
        response = SESSION.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        # Handle exceptions or log errors here
        print(f'Error occurred while retrieving a thread: {e}')
        return None  # You can choose to return None or handle the error as needed

# Function to create a new open_ai_thread
def create_thread(thread_data):
    try:
        url = f"{BASE_URL}/threads.json"
        headers = {"Content-Type": "application/json"}
        response = SESSION.post(url, json=thread_data, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        # Handle exceptions or log errors here
        print(f'Error occurred while creating a thread: {e}')
        return None  # You can choose to return None or handle the error as needed

# Function to update an existing open_ai_thread by ID
def update_thread(thread_id, thread_data):
    try:
        url = f"{BASE_URL}/threads/{thread_id}.json"
        headers = {"Content-Type": "application/json"}
        response = SESSION.put(url, json=thread_data, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        # Handle exceptions or log errors here
        print(f'Error occurred while updating a thread: {e}')
        return None  # You can choose to return None or handle the error as needed

# Function to delete an open_ai_thread by ID
def delete_thread(thread_id):
    try:
        url = f"{BASE_URL}/threads/{thread_id}.json"
        response = SESSION.delete(url)
        response.raise_for_status()
        return response.status_code  # 204 for success, handle as needed
    except requests.exceptions.RequestException as e:
        # Handle exceptions or log errors here
        print(f'Error occurred while deleting a thread: {e}')
        return None  # You can choose to return None or handle the error as needed