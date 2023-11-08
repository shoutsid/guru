
import sys
from typing import List, Optional, Union, Dict
from autogen import AssistantAgent, GroupChat, ConversableAgent, Agent
from townhall.groups.group_chat import GroupChatExpanded
from townhall.agents.utils import colored


SYSTEM_MESSAGE = """
You are a Group chat manager, you're responsible for managing the group chat.
"""

class GroupChatManagerExpanded(ConversableAgent):
    def __init__ (
        self,
        groupchat: GroupChatExpanded,
        name: Optional[str] = "chat_manager",
        # unlimited consecutive auto reply by default
        max_consecutive_auto_reply: Optional[int] = sys.maxsize,
        human_input_mode: Optional[str] = "NEVER",
        system_message: Optional[str] = SYSTEM_MESSAGE,
        **kwargs,
    ):
        self.groupchat = groupchat
        super().__init__(
            name=name,
            max_consecutive_auto_reply=max_consecutive_auto_reply,
            human_input_mode=human_input_mode,
            system_message=system_message,
            **kwargs,
        )
        self.register_reply(Agent, GroupChatManagerExpanded.run_chat, config=groupchat, reset_config=GroupChatExpanded.reset)

    # def complete(self):
    #     """Complete the chat."""
    #     self.groupchat.learn_from_messages()

    def run_chat(
        self,
        messages: Optional[List[Dict]] = None,
        sender: Optional[Agent] = None,
        config: Optional[GroupChat] = None,
    ) -> Union[str, Dict, None]:
        """Run a group chat."""
        if messages is None:
            messages = self._oai_messages[sender]
        message = messages[-1]
        speaker = sender
        groupchat = config
        for i in range(groupchat.max_round):

            # Assigning role function or participant
            # set the name to speaker's name if the role is not function
            if message["role"] != "function":
                message["name"] = speaker.name
            groupchat.messages.append(message)

            # Broadcasting the message to all agents except the speaker.
            # This does not request a reply from the agents and is silent.
            for agent in groupchat.agents:
                if agent != speaker:
                    self.send(message, agent, request_reply=False, silent=True)
            if i == groupchat.max_round - 1:
                # the last round
                break

            try:
                # select the next speaker
                speaker = groupchat.select_speaker(speaker, self)
                # let the speaker speak
                reply = speaker.generate_reply(sender=self)

            except KeyboardInterrupt:
                # let the admin agent speak if interrupted
                if groupchat.admin_name in groupchat.agent_names:
                    # admin agent is one of the participants
                    speaker = groupchat.agent_by_name(groupchat.admin_name)
                    reply = speaker.generate_reply(sender=self)
                else:
                    # admin agent is not found in the participants
                    raise

            if reply is None:
                break
            # The speaker sends the message without requesting a reply
            speaker.send(reply, self, request_reply=False)
            message = self.last_message(speaker)
        return True, None


