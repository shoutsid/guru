import logging
import os
import weaviate

logging.basicConfig(level=logging.DEBUG)

# auth_client_secret=weaviate.auth.AuthApiKey(
#     api_key="<YOUR-WEAVIATE-API-KEY>"),
# additional_headers={
#     "X-OpenAI-Api-Key": os.getenv("OPENAI_API_KEY")
# }

WEAVIATE_API_BASE = os.getenv("WEAVIATE_API")

if WEAVIATE_API_BASE is None:
    WEAVIATE_API_BASE = "http://localhost:8080"

client = weaviate.Client(
    url=WEAVIATE_API_BASE,
)

# Check if your instance is live and ready
# This should return `True`
if client.is_ready():
    print("Weaviate Client is live! ✅")
    logging.debug("Weaviate Client is live! ✅")
else:
    print("Weaviate Client is not live! ❌")
    logging.debug("Weaviate Client is not live! ❌")
