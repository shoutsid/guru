import autogen
from autogen.agentchat.agent import Agent
from autogen.agentchat.assistant_agent import ConversableAgent, AssistantAgent
from typing import Callable, Dict, Optional, Union, List, Tuple, Any

from guru.weaviate.client import client as weaviate_client
from guru.agents.utils import openai_tool_decorator


system_message = """You are a Discord Assistant, you have the ability to search previous discord messages.
You are able to generate a message based on the previous messages using your functions.
ou can use the get_data_with_near_text function to retrieve data from Weaviate based on the given entity type, attributes, concepts, and single prompt.
Use {PROPERTY_NAME} in the prompt to instuct Weaviate which data to use
"""


class DiscordAgent(ConversableAgent):
    def __init__(
        self,
        name="discord_agent",
        system_message: Optional[str] = system_message,
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
        self.register_reply(Agent, DiscordAgent.respond, 1)

    def respond(
        self,
        messages: Optional[List[Dict]] = None,
        sender: Optional[Agent] = None,
        config: Optional[Any] = None,
    ) -> Tuple[bool, Union[str, Dict, None]]:
        if self.llm_config is False:
            raise ValueError(
                "DiscordAgent requires self.llm_config to be set in its base class.")
        if messages is None:
            messages = self._oai_messages[sender]  # In case of a direct call.
        print("DiscordAgent respond")
        print("messages:")
        print(messages)

        user_proxy = autogen.UserProxyAgent(
            name="discord_agent_user_proxy",
            is_termination_msg=lambda x: x.get("content", "") and x.get(
                "content", "").rstrip().endswith("TERMINATE"),
            human_input_mode="NEVER",
            max_consecutive_auto_reply=5,
            code_execution_config={"work_dir": "agent_workplace"},
        )
        assistant_config = self.llm_config.copy()
        assistant_config["functions"] = [
            DiscordAgent.get_data_with_near_text_and_single_prompt.tools["function"]]
        assistant = AssistantAgent(
            "discord_agent_assistant",
            system_message="For all replies, only use the functions you have been provided with. Reply TERMINATE when the task is done.",
            is_termination_msg=lambda x: x.get(
                "content", "").rstrip().find("TERMINATE") >= 0,
            llm_config=assistant_config
        )
        user_proxy.register_function(
            function_map={
                "get_data_with_near_text_and_single_prompt": DiscordAgent.get_data_with_near_text_and_single_prompt,
            }
        )

        internal_send_message = messages[0].get("content", "")

        user_proxy.initiate_chat(
            assistant, message=internal_send_message)
        response = user_proxy.last_message(assistant)

        # remove the TERMINATE message from the response and unless the only message is TERMINATE
        if response["content"].find("TERMINATE") >= 0 and len(response["content"]) > 10:
            response["content"] = response["content"].replace(
                "TERMINATE", "").strip()

        return True, response

    @openai_tool_decorator
    def get_data_with_near_text_and_single_prompt(
        entity_type: str,
        attributes: List[str],
        concepts: List[str],
        single_prompt: str,
        distance: float = 0.7,
        limit: int = 1,
    ) -> List[Dict[str, Any]]:
        """
        Retrieves data from Weaviate based on the given entity type, attributes, concepts, and single prompt.
        Args:
            entity_type (str): The type of entity to query.
            attributes (List[str]): The list of attributes to retrieve.
            concepts (List[str]): The list of concepts to search for.
            single_prompt (str): The single prompt to generate data and MUST NOT be empty. single_prompt should always include the attribute in question, i.e "Craft a sympathic message for this content: {content}" is a valid single_prompt.
            distance (float, optional): The distance threshold for near text search. Defaults to 0.7.
            limit (int, optional): The maximum number of results to retrieve. Defaults to 1.
        Returns:
            List[Dict[str, Any]]: The retrieved data from Weaviate.
        """
        # validate single_prompt is not empty
        if not single_prompt:
            raise Exception("single_prompt can not be empty.")

        response = weaviate_client.query.get(entity_type, attributes).with_near_text(
            {"concepts": concepts, "distance": distance}
        ).with_limit(limit).with_generate(single_prompt=single_prompt).do()

        print("get_data_with_near_text response")
        print(response)

        return str(response)
