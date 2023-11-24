from typing import Dict, Optional, Union, List, Any
from autogen.agentchat.assistant_agent import AssistantAgent

SYSTEM_MESSAGE = """You are a Discord Assistant, you have the ability to search previous discord messages
You have the ability to research on arXiv, which is a website where scientists and mathematicians can share their papers before they are published in journals.
You have the ability to instruct discord_agent_assistant and discord_agent_user_proxy to do these tasks for you.
"""


class DiscordAgent(AssistantAgent):
    def __init__(
        self,
        name="discord_agent",
        system_message: Optional[str] = SYSTEM_MESSAGE,
        human_input_mode: Optional[str] = "NEVER",
        llm_config: Optional[Union[Dict, bool]] = None,
        **kwargs,
    ):
        super().__init__(
            name=name,
            system_message=system_message,
            human_input_mode=human_input_mode,
            llm_config=llm_config,
            **kwargs,
        )
