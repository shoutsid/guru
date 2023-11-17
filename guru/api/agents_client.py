from .utils import BASE_URL, SESSION, requests

# Function to list all agents
def list_agents():
    try:
        url = f"{BASE_URL}/agents.json"
        response = SESSION.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        # Handle exceptions or log errors here
        print(f'Error occurred while listing agents: {e}')
        return None  # You can choose to return None or handle the error as needed

# Function to show a specific agent by ID
def get_agent(agent_id):
    try:
        url = f"{BASE_URL}/agents/{agent_id}.json"
        response = SESSION.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        # Handle exceptions or log errors here
        print(f'Error occurred while retrieving an agent: {e}')
        return None  # You can choose to return None or handle the error as needed

# Function to create a new agent
def create_agent(agent_data):
    try:
        url = f"{BASE_URL}/agents.json"
        headers = {"Content-Type": "application/json"}
        response = SESSION.post(url, json=agent_data, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        # Handle exceptions or log errors here
        print(f'Error occurred while creating an agent: {e}')
        return None  # You can choose to return None or handle the error as needed

# Function to update an existing agent by ID
def update_agent(agent_id, agent_data):
    try:
        url = f"{BASE_URL}/agents/{agent_id}.json"
        headers = {"Content-Type": "application/json"}
        response = SESSION.put(url, json=agent_data, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        # Handle exceptions or log errors here
        print(f'Error occurred while updating an agent: {e}')
        return None  # You can choose to return None or handle the error as needed

# Function to delete an agent by ID
def delete_agent(agent_id):
    try:
        url = f"{BASE_URL}/agents/{agent_id}.json"
        response = SESSION.delete(url)
        response.raise_for_status()
        return response.status_code  # 204 for success, handle as needed
    except requests.exceptions.RequestException as e:
        # Handle exceptions or log errors here
        print(f'Error occurred while deleting an agent: {e}')
        return None  # You can choose to return None or handle the error as needed
