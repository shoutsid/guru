import os
from dotenv import load_dotenv

load_dotenv()

# Validate essential environment variables
if "OPENAI_API_KEY" not in os.environ:
    raise EnvironmentError("Missing essential environment variable: OPENAI_API_KEY")

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
GPT3_5_TURBO_1106 = "gpt-3.5-turbo-1106"
GPT4 = "gpt-4-1106-preview"
VICUNA_7B_V1_5 = "vicuna-7b-v1.5"
MISTRAL = "OpenHermes-2.5-Mistral-7B"

if "GPT4" in os.environ:
    CONFIG_LIST = [
        {
            "model": GPT4,
            "api_key": OPENAI_API_KEY,
        }
    ]
elif "LOCAL" in os.environ:
    CONFIG_LIST = [
        {
            "model": MISTRAL,
            "base_url": "http://localhost:8000/v1",
            "api_key": "None",
        }
    ]
elif "HUGGINGFACE" in os.environ:
    CONFIG_LIST = [
        {
            "model": "teknium/OpenHermes-2.5-Mistral-7B",
            "base_url": "https://v1tkumrhi125vaeb.eu-west-1.aws.endpoints.huggingface.cloud",
            "api_key": OPENAI_API_KEY,
        }
    ]
else:
    CONFIG_LIST = [
        {
            "model": GPT4,
            "api_key": OPENAI_API_KEY,
        }
    ]

LLM_CONFIG = {
    "config_list": CONFIG_LIST,
    "temperature": 0
}
