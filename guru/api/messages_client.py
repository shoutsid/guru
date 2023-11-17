from .utils import BASE_URL, SESSION, requests

# Function to list all open_ai_messages for a specific thread
def list_messages(thread_id):
    try:
        url = f"{BASE_URL}/threads/{thread_id}/messages.json"
        response = SESSION.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        # Handle exceptions or log errors here
        print(f'Error occurred while listing messages: {e}')
        return None  # You can choose to return None or handle the error as needed

# Function to show a specific open_ai_message by ID within a thread
def get_message(thread_id, message_id):
    try:
        url = f"{BASE_URL}/threads/{thread_id}/messages/{message_id}.json"
        response = SESSION.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        # Handle exceptions or log errors here
        print(f'Error occurred while retrieving a message: {e}')
        return None  # You can choose to return None or handle the error as needed

# Function to create a new open_ai_message within a thread
def create_message(thread_id, message_data):
    try:
        url = f"{BASE_URL}/threads/{thread_id}/messages.json"
        headers = {"Content-Type": "application/json"}
        response = SESSION.post(url, json=message_data, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        # Handle exceptions or log errors here
        print(f'Error occurred while creating a message: {e}')
        return None  # You can choose to return None or handle the error as needed

# Function to update an existing open_ai_message by ID within a thread
def update_message(thread_id, message_id, message_data):
    try:
        url = f"{BASE_URL}/threads/{thread_id}/messages/{message_id}.json"
        headers = {"Content-Type": "application/json"}
        response = SESSION.put(url, json=message_data, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        # Handle exceptions or log errors here
        print(f'Error occurred while updating a message: {e}')
        return None  # You can choose to return None or handle the error as needed

# Function to delete an open_ai_message by ID within a thread
def delete_message(thread_id, message_id):
    try:
        url = f"{BASE_URL}/threads/{thread_id}/messages/{message_id}.json"
        response = SESSION.delete(url)
        response.raise_for_status()
        return response.status_code  # 204 for success, handle as needed
    except requests.exceptions.RequestException as e:
        # Handle exceptions or log errors here
        print(f'Error occurred while deleting a message: {e}')
        return None  # You can choose to return None or handle the error as needed
