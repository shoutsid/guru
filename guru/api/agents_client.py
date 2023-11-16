import os
import requests

GURU_API_BASE = os.getenv("GURU_API")

if GURU_API_BASE is None:
    GURU_API_BASE = "http://localhost:3000"

# Define the base URL for the API
BASE_URL = GURU_API_BASE

# Function to list all agents
def list_agents():
    url = f"{BASE_URL}/agents.json"
    response = requests.get(url)
    return response.json()

# Function to show a specific agent by ID
def get_agent(agent_id):
    url = f"{BASE_URL}/agents/{agent_id}.json"
    response = requests.get(url)
    return response.json()

# Function to create a new agent
def create_agent(agent_data):
    url = f"{BASE_URL}/agents.json"
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=agent_data, headers=headers)
    return response.json()

# Function to update an existing agent by ID
def update_agent(agent_id, agent_data):
    url = f"{BASE_URL}/agents/{agent_id}.json"
    headers = {"Content-Type": "application/json"}
    response = requests.put(url, json=agent_data, headers=headers)
    return response.json()

# Function to delete an agent by ID
def delete_agent(agent_id):
    url = f"{BASE_URL}/agents/{agent_id}.json"
    response = requests.delete(url)
    return response.status_code  # 204 for success, handle as needed
