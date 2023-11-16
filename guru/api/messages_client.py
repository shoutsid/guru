import os
import requests

GURU_API_BASE = os.getenv("GURU_API")

if GURU_API_BASE is None:
    GURU_API_BASE = "http://localhost:3000"

# Define the base URL for the API
BASE_URL = GURU_API_BASE

# Function to list all open_ai_messages for a specific thread
def list_messages(thread_id):
    url = f"{BASE_URL}/threads/{thread_id}/messages.json"
    response = requests.get(url)
    return response.json()

# Function to show a specific open_ai_message by ID within a thread
def get_message(thread_id, message_id):
    url = f"{BASE_URL}/threads/{thread_id}/messages/{message_id}.json"
    response = requests.get(url)
    return response.json()

# Function to create a new open_ai_message within a thread
def create_message(thread_id, message_data):
    url = f"{BASE_URL}/threads/{thread_id}/messages.json"
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=message_data, headers=headers)
    return response.json()

# Function to update an existing open_ai_message by ID within a thread
def update_message(thread_id, message_id, message_data):
    url = f"{BASE_URL}/threads/{thread_id}/messages/{message_id}.json"
    headers = {"Content-Type": "application/json"}
    response = requests.put(url, json=message_data, headers=headers)
    return response.json()

# Function to delete an open_ai_message by ID within a thread
def delete_message(thread_id, message_id):
    url = f"{BASE_URL}/threads/{thread_id}/messages/{message_id}.json"
    response = requests.delete(url)
    return response.status_code  # 204 for success, handle as needed
