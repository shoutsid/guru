import os
import requests

GURU_API_BASE = os.getenv("GURU_API")

if GURU_API_BASE is None:
    GURU_API_BASE = "http://localhost:3000"

# Define the base URL for the API
BASE_URL = GURU_API_BASE

# Function to list all open_ai_threads
def list_threads(discord = False, discord_channel=None):
    url = f"{BASE_URL}/threads.json"
    params = []
    if discord:
        params.append("discord=true")
    if discord_channel is not None:
        params.append(f"discord_channel={discord_channel}")
    if len(params) > 0:
        url = f"{url}?{'&'.join(params)}"
    response = requests.get(url)
    return response.json()

# Function to show a specific open_ai_thread by ID
def get_thread(thread_id):
    url = f"{BASE_URL}/threads/{thread_id}.json"
    response = requests.get(url)
    return response.json()

def get_thread(thread_id):
    url = f"{BASE_URL}/threads/{thread_id}.json"
    response = requests.get(url)
    return response.json()

# Function to create a new open_ai_thread
def create_thread(thread_data):
    url = f"{BASE_URL}/threads.json"
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=thread_data, headers=headers)
    return response.json()

# Function to update an existing open_ai_thread by ID
def update_thread(thread_id, thread_data):
    url = f"{BASE_URL}/threads/{thread_id}.json"
    headers = {"Content-Type": "application/json"}
    response = requests.put(url, json=thread_data, headers=headers)
    return response.json()

# Function to delete an open_ai_thread by ID
def delete_thread(thread_id):
    url = f"{BASE_URL}/threads/{thread_id}.json"
    response = requests.delete(url)
    return response.status_code  # 204 for success, handle as needed
