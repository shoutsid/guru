from .utils import openai_tool_decorator
from .discord_agent import DiscordAgent

from typing import Dict, List, Any
import arxiv
from autogen.agentchat.agent import Agent
from autogen.agentchat.conversable_agent import ConversableAgent
from autogen.agentchat.groupchat import GroupChat, GroupChatManager
from autogen.agentchat.user_proxy_agent import UserProxyAgent
from autogen.agentchat.assistant_agent import AssistantAgent
from autogen.agentchat.contrib.text_analyzer_agent import TextAnalyzerAgent
from settings import CONFIG_LIST
from guru.weaviate.client import client as weaviate_client

LLM_CONFIG = {
    "config_list": CONFIG_LIST,
}


class GuruGroupChat(GroupChat):
    speaker_selection_method = "auto"
    max_round = 1

    def __init__(self, *args, **kwargs):
        self.user_proxy_config = LLM_CONFIG.copy()
        self.user_proxy = UserProxyAgent(
            name="discord_agent_user_proxy",
            system_message="You are a discord_agent_user_proxy",
            is_termination_msg=lambda x: x.get("content", "") and x.get(
                "content", "").rstrip().endswith("TERMINATE"),
            human_input_mode="NEVER",
            max_consecutive_auto_reply=2,
            code_execution_config={
                "work_dir": "agent_workplace", "last_n_messages": 2},
            llm_config=self.user_proxy_config,
        )
        self.assistant_config = LLM_CONFIG.copy()
        self.assistant_config["functions"] = [
            GuruGroupChat.get_data_with_near_text_and_single_prompt.tools["function"],
            GuruGroupChat.get_data_with_near_text_and_grouped_task.tools["function"],
            GuruGroupChat.get_data_with_ask.tools["function"],
            GuruGroupChat.search_arxiv.tools["function"],
        ]
        self.discord_assistant = AssistantAgent(
            "discord_agent_assistant",
            system_message="Determine whether or not the users request can be achieved with the functions provided to you. Reply TERMINATE when the task is done.",
            is_termination_msg=lambda x: x.get("content", "") and x.get(
                "content", "").rstrip().endswith("TERMINATE"),
            llm_config=self.assistant_config
        )
        merged_function_map = {
            "get_data_with_near_text_and_single_prompt": GuruGroupChat.get_data_with_near_text_and_single_prompt,
            "get_data_with_near_text_and_grouped_task": GuruGroupChat.get_data_with_near_text_and_grouped_task,
            "get_data_with_ask": GuruGroupChat.get_data_with_ask,
            "search_arxiv": GuruGroupChat.search_arxiv,
        }
        # give our user_proxy the ability to execute the function choices provided by the assistant
        self.user_proxy.register_function(
            function_map=merged_function_map
        )
        self.analyzer_config = LLM_CONFIG.copy()
        self.analyzer = AssistantAgent(
            name="discord_agent_analyzer",
            max_consecutive_auto_reply=0,
            system_message="YOU ALWAYS FINALLY SUMMARISE the conversation ensuring that the original user request is met. If there is a failure or you're unable to fulfil the task, explain why.", llm_config=self.analyzer_config)

        self.agents = [
            self.discord_assistant, self.user_proxy, self.analyzer
        ]
        super().__init__(agents=self.agents, *args, **kwargs)

    def reset(self):
        super().reset()
        self.analyzer.reset()  # Clear the analyzer's list of messages.

    def agent_by_name(self, name: str) -> Agent:
        return super().agent_by_name(name)

    def next_agent(self, agent: Agent, agents: List[Agent]) -> Agent:
        return super().next_agent(agent, agents)

    def select_speaker_msg(self, agents: List[Agent]):
        return super().select_speaker_msg(agents)

    def manual_select_speaker(self, agents: List[Agent]) -> Agent:
        return super().manual_select_speaker(agents)

    def select_speaker(self, last_speaker: Agent, selector: ConversableAgent):
        return super().select_speaker(last_speaker, selector)

    # prune: bool = True,
    # max_chunk_results: int = 100,
    @openai_tool_decorator
    def search_arxiv(
        query: str,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Searches arxiv for papers based on the given query.
        Args:
            query (str): The search query.
            max_results (int, optional): The maximum number of results to retrieve. Defaults to 10.
        Returns:
            List[Dict[str, Any]]: A list of dictionaries representing the search results.
        """
        client = arxiv.Client()
        search = arxiv.Search(
            query=query,
            max_results=max_results
        )
        return [r for r in client.results(search)]

    @openai_tool_decorator
    def get_data_with_ask(
        entity_type: str,
        attributes: List[str],
        ask: List[str],
        limit: int = 1,
    ) -> List[Dict[str, Any]]:
        """
        Retrieves data from Weaviate based on the given entity type, attributes, and ask.
        Args:
            entity_type (str): The type of entity to query.
            attributes (List[str]): The list of attributes to retrieve. i.e ["content"] is valid.
            ask (str): The ask to generate data and MUST NOT be empty. i.e "What are aliens?" is valid.
            limit (int, optional): The maximum number of results to retrieve. Defaults to 1.
        Returns:
            List[Dict[str, Any]]: The retrieved data from Weaviate.
        """
        # validate ask is not empty
        if not ask:
            raise Exception("ask can not be empty.")

        # if attributes does not contain the string
        if not any("_additional" in s for s in attributes):
            required_attributes = [
                "_additional {answer {hasAnswer property result startPosition endPosition} }"]
            attributes = attributes + required_attributes

        response = weaviate_client.query.get(
            entity_type, attributes).with_ask(ask).with_limit(limit).do()

        print("get_data_with_ask response")
        print(response)

        return str(response)

    @openai_tool_decorator
    def get_data_with_near_text_and_grouped_task(
        entity_type: str,
        attributes: List[str],
        concepts: List[str],
        grouped_task: str,
        distance: float = 0.7,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Retrieves data from Weaviate based on the given entity type, attributes, concepts, and grouped task.
        Args:
            entity_type (str): The type of entity to query.
            attributes (List[str]): The list of attributes to retrieve.
            concepts (List[str]): The list of concepts to search for.
            grouped_task(str): The single prompt to generate data and MUST NOT be empty. i.e "Explain why these DiscordMessage's are about aliens" is valid.
            distance (float, optional): The distance threshold for near text search. Defaults to 0.7.
            limit (int, optional): The maximum number of results to retrieve. Defaults to 1.
        Returns:
            List[Dict[str, Any]]: The retrieved data from Weaviate.
        """
        # validate single_prompt is not empty
        if not grouped_task:
            raise Exception("grouped_task can not be empty.")

        response = weaviate_client.query.get(entity_type, attributes).with_near_text(
            {"concepts": concepts, "distance": distance}
        ).with_limit(limit).with_generate(grouped_task=grouped_task).do()

        print("get_data_with_near_text_and_grouped_task response")
        print(response)

        return str(response)

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
            single_prompt (str): The single prompt to generate data and MUST NOT be empty. single_prompt should always include the attribute in question, i.e "Craft a sympathic message for this content: {content}" is valid single_prompt.
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


class GuruGroupChatManager(GroupChatManager):
    def __init__(self, groupchat: GuruGroupChat, **kwargs):
        super().__init__(groupchat, **kwargs)

    def run_chat(self, messages: List[Dict] = None, sender: Agent = None, config: GroupChat = None) -> str | Dict:
        return super().run_chat(messages, sender, config)

    def a_run_chat(self, messages: List[Dict] = None, sender: Agent = None, config: GroupChat = None):
        return super().a_run_chat(messages, sender, config)
