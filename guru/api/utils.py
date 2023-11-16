import os
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

GURU_API_BASE = os.getenv("GURU_API")

if GURU_API_BASE is None:
    GURU_API_BASE = "http://localhost:3000"

# Define the base URL for the API
BASE_URL = GURU_API_BASE

# Create a session
SESSION = requests.Session()

# Define the maximum number of retries and backoff factor
max_retries = 3
backoff_factor = 5

# Create a Retry object with the desired settings
retry = Retry(
    total=max_retries,
    backoff_factor=backoff_factor,
    status_forcelist=[500, 502, 503, 504],  # HTTP status codes to retry on
)

# Create an HTTPAdapter with the Retry object
ADAPTER = HTTPAdapter(max_retries=retry)
# Mount the adapter to the session for all requests
SESSION.mount('http://', ADAPTER)
SESSION.mount('https://', ADAPTER)