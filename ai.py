"""
TODO: Add a way to save the chat history to a file.
TODO: Add langchain tools https://api.python.langchain.com/en/latest/api_reference.html#module-langchain.tools
"""

import sys
from langchain.agents import load_tools
from townhall.agents.teachable_agent import TeachableAgent
from townhall.agents.python_engineer import PythonEngineer
from townhall.agents.user_agent import UserAgent
from townhall.services.chat_service import ChatService
from settings import CONFIG_LIST

def generate_llm_config(tool):
    """
    Generate a function schema for a LangChain tool.
    """
    function_schema = {
        "name": tool.name.lower().replace (' ', '_'),
        "description": tool.description,
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    }

    if tool.args is not None:
        function_schema["parameters"]["properties"] = tool.args

    return function_schema


# Below can be used to get all of the tools available in LangChain
# from langchain.agents import get_all_tool_names
# all_tools = get_all_tool_names()
# for tool in all_tools:
#     print(tool)
TOOL_NAMES = [
    'ddg-search', 'requests', 'terminal', 'arxiv', 'python_repl', 'wikipedia',
    'eleven_labs_text2speech'
]
TOOLS = load_tools(TOOL_NAMES)

FUNCTIONS_MAP = {}
FUNCTIONS_CONFIG = []
for tool in TOOLS:
    # pylint: disable=protected-access
    FUNCTIONS_MAP[tool.name] = tool._run
    # pylint: enable=protected-access
    FUNCTIONS_CONFIG.append(generate_llm_config(tool))

try:
    from termcolor import colored
except ImportError:

    def colored(x, *args, **kwargs):
        return x

LLM_CONFIG = {
    "request_timeout": 180,
    "config_list": CONFIG_LIST,
    "use_cache": True,  # Use False to explore LLM non-determinism.
    "retry_wait_time": 0.5,
    "max_retry_period": 360,
    "functions": FUNCTIONS_CONFIG
}

TEACH_CONFIG={
    "verbosity": 3,  # 0 for basic info, 1 to add memory operations, 2 for analyzer messages, 3 for memo lists.
    "reset_db": False,  # Set to True to start over with an empty database.
    "path_to_db_dir": "./.cache/ai_db",  # Path to the directory where the database will be stored.
    "recall_threshold": 1.5,  # Higher numbers allow more (but less relevant) memos to be recalled.
}

TEACHABLE_AGENT = TeachableAgent(
    name="Assistant",
    llm_config=LLM_CONFIG,
    teach_config=TEACH_CONFIG,
    code_execution_config={ "work_dir": "agent_workplace" },
    human_input_mode="NEVER"
)
USER_AGENT = UserAgent(
        code_execution_config={ "work_dir": "agent_workplace" },
        max_consecutive_auto_reply=1,
        human_input_mode="ALWAYS",
)


# create function_map that matjches with tools in LangChain

USER_AGENT.register_function(
    function_map=FUNCTIONS_MAP
)
PYTHON_ENGINEER = PythonEngineer(
    system_message="You are a Python Engineer.",
    human_input_mode="NEVER",
    code_execution_config={ "work_dir": "agent_workplace" },
    max_consecutive_auto_reply=10,
)
# ASSISTANTS = [TEACHABLE_AGENT, PYTHON_ENGINEER]
ASSISTANTS = [TEACHABLE_AGENT]
CHAT_SERVICE = ChatService(
    assistants=ASSISTANTS,
    user_proxy=USER_AGENT,
    llm_config=LLM_CONFIG,
)

class Main:
    """
    Main class for the Teachable Agent demo.
    """
    active_agent: bool = True

    def chat(self, txt: str):
        """Chat with the agents."""
        # while self.active_agent:
        if txt == "exit":
            self.active_agent = False
            CHAT_SERVICE.complete()
            sys.exit(0)
        CHAT_SERVICE.initiate_chat(message=txt, clear_history=False)
        CHAT_SERVICE.complete()

_main = Main()
import openai as openai
try:
    # Initial message to the agents.
    text = input(
        """
        Welcome to the Teachable Agent demo.\n
        On exit, the conversations will be reset. But hopefully they will have remembered something from the conversation! \n
        Enter a message to the Agents: \n
        """ \
            "> "
    )
    _main.chat(text)
except openai.error.Timeout:
    print(colored("OpenAI API timeout", "red"))
    _main.chat("We have encountered an OpenAI API timeout. Please try again.")
