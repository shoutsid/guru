"""
A module that contains the ChatService class,
which represents a chat service between a user and an assistant agent.
"""

from typing import List
from autogen import AssistantAgent
from guru.agents.user_agent import UserAgent
from guru.agents.utils import is_termination_msg
from guru.managers.group_chat_manager import GroupChatManagerExpanded
from guru.groups.group_chat import GroupChatExpanded
from settings import CONFIG_LIST, LLM_CONFIG

class ChatService:
    """
    A class that represents a chat service between a user and an assistant agent.

    Attributes:
      assistant (AssistantAgent): The assistant agent used in the chat service.
      user_proxy (UserAgent): The user agent used in the chat service.
    """

    def __init__(
            self,
            config_list: dict = None,
            assistants: List = None,
            user_proxy: UserAgent = None,
            llm_config: dict = None,
    ):
        if config_list is None:
            self.config_list = CONFIG_LIST.copy() # now not used, use LLM_CONFIG instead
        else:
            self.config_list = config_list

        if llm_config is None:
            self.llm_config = LLM_CONFIG.copy()
        else:
            self.llm_config = llm_config

        if assistants is None:
            self.assistants = [
                AssistantAgent(
                    name="assistant",
                    system_message="""
                        For coding tasks, only use the functions you have been provided with.
                        Your argument should follow json format. Reply TERMINATE when the task is done.
                    """,
                    llm_config=self.llm_config
                )
            ]
        else:
            self.assistants = assistants

        if user_proxy is None:
            self.user_proxy = UserAgent(
                name="user_proxy",
                is_termination_msg=is_termination_msg,
                max_consecutive_auto_reply=10,
                llm_config=self.llm_config,
            )
        else:
            self.user_proxy = user_proxy

        self.messages: List = []

        # Setup group chat and manager
        self.chat = GroupChatExpanded(
            agents=[user_proxy, *self.assistants], messages=self.messages, max_round=50)
        self.manager = GroupChatManagerExpanded(groupchat=self.chat, llm_config=self.llm_config)

    def initiate_chat(self, message, clear_history: bool | None = True):
        """
        Initiates a chat session between the user and the assistant.

        Args:
          message (str): The initial message from the user.

        Returns:
          None
        """
        if len(self.assistants) == 0:
            raise ValueError("No assistant agent is available.")

        if len(self.assistants) == 1:
            return self.user_proxy.initiate_chat(
                self.assistants[0], message=message, clear_history=clear_history)

        # below message/problem depending on the user_proxy agent that is used
        self.user_proxy.initiate_chat(self.manager, message=message, clear_history=clear_history)
        # self.user_proxy.initiate_chat(self.manager, problem=message, clear_history=clear_history)

    def complete(self):
        """
        Completes the chat session between the user and the assistant.
        This will initiate the learning process for the assistant agent.

        Returns:
          None
        """
        pass
        # self.manager.complete()
