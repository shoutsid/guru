from typing import Dict, Optional, List, Union
from .agent_base import AgentBase

class Agent(AgentBase, table=True):
    class Config:
        property_set_methods = {"_name": "set_name"}

    _name: str
    system_message: str = None
    openai_id: str = None

    def __init__(
        self,
        name: str,
        system_message: str,
    ):
        super().__init__(name=name)
        self._name = name
        self.system_message = system_message

    def set_name(self, value):
        self.name = value

    def __setattr__(self, key, val):
        method = self.__config__.property_set_methods.get(key)
        if method is None:
            super().__setattr__(key, val)
        else:
            getattr(self, method)(val)

    @property
    def name(self):
        """Get the name of the agent."""
        return self._name

    def send(self, message: Union[Dict, str], recipient: "Agent", request_reply: Optional[bool] = None):
        """(Abstract method) Send a message to another agent."""

    async def a_send(self, message: Union[Dict, str], recipient: "Agent", request_reply: Optional[bool] = None):
        """(Abstract async method) Send a message to another agent."""

    def receive(self, message: Union[Dict, str], sender: "Agent", request_reply: Optional[bool] = None):
        """(Abstract method) Receive a message from another agent."""

    async def a_receive(self, message: Union[Dict, str], sender: "Agent", request_reply: Optional[bool] = None):
        """(Abstract async method) Receive a message from another agent."""

    def reset(self):
        """(Abstract method) Reset the agent."""

    def generate_reply(
        self,
        messages: Optional[List[Dict]] = None,
        sender: Optional["Agent"] = None,
        **kwargs,
    ) -> Union[str, Dict, None]:
        """(Abstract method) Generate a reply based on the received messages.

        Args:
            messages (list[dict]): a list of messages received.
            sender: sender of an Agent instance.
        Returns:
            str or dict or None: the generated reply. If None, no reply is generated.
        """

    async def a_generate_reply(
        self,
        messages: Optional[List[Dict]] = None,
        sender: Optional["Agent"] = None,
        **kwargs,
    ) -> Union[str, Dict, None]:
        """(Abstract async method) Generate a reply based on the received messages.

        Args:
            messages (list[dict]): a list of messages received.
            sender: sender of an Agent instance.
        Returns:
            str or dict or None: the generated reply. If None, no reply is generated.
        """
