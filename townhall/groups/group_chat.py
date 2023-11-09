import random
from dataclasses import dataclass
from typing import Dict, List
from autogen import Agent
from autogen import ConversableAgent
import logging

logger = logging.getLogger(__name__)


@dataclass
class GroupChatExpanded:
    """A group chat class that contains the following data fields:
    - agents: a list of participating agents.
    - messages: a list of messages in the group chat.
    - max_round: the maximum number of rounds.
    - admin_name: the name of the admin agent if there is one. Default is "Admin".
        KeyBoardInterrupt will make the admin agent take over.
    - func_call_filter: whether to enforce function call filter. Default is True.
        When set to True and when a message is a function call suggestion,
        the next speaker will be chosen from an agent which contains the corresponding function name
        in its `function_map`.
    """

    agents: List[Agent]
    messages: List[Dict]
    max_round: int = 10
    admin_name: str = "User"
    func_call_filter: bool = True
    previous_speaker: Agent = None  # Keep track of the previous speaker


    @property
    def agent_names(self) -> List[str]:
        """Return the names of the agents in the group chat."""
        return [agent.name for agent in self.agents]

    # def learn_from_messages(self):
    #     """Learn from messages."""
    #     for agent in self.agents:
    #         if hasattr(agent, "learn_from_user_feedback"):
    #             agent.learn_from_user_feedback()
    #             agent.close_db()

    def reset(self):
        """Reset the group chat."""
        self.messages.clear()

    def agent_by_name(self, name: str) -> Agent:
        """Find the next speaker based on the message."""
        return self.agents[self.agent_names.index(name)]

    def next_agent(self, agent: Agent, agents: List[Agent]) -> Agent:
        """Return the next agent in the list."""
        if agents == self.agents:
            return agents[(self.agent_names.index(agent.name) + 1) % len(agents)]
        else:
            offset = self.agent_names.index(agent.name) + 1
            for i in range(len(self.agents)):
                if self.agents[(offset + i) % len(self.agents)] in agents:
                    return self.agents[(offset + i) % len(self.agents)]

    def select_speaker_msg(self, agents: List[Agent]):
        """Return the message for selecting the next speaker."""
        return f"""You are in a role play game. The following roles are available:
{self._participant_roles()}.

Read the following conversation.
Then select the next role from {[agent.name for agent in agents]} to play. Only return the role."""

    # def select_speaker(self, last_speaker: Agent, selector: ConversableAgent):
    #     """Select the next speaker."""
    #     if self.func_call_filter and self.messages and "function_call" in self.messages[-1]:
    #         # find agents with the right function_map which contains the function name
    #         agents = [
    #             agent for agent in self.agents if agent.can_execute_function(self.messages[-1]["function_call"]["name"])
    #         ]
    #         if len(agents) == 1:
    #             # only one agent can execute the function
    #             return agents[0]
    #         elif not agents:
    #             # find all the agents with function_map
    #             agents = [agent for agent in self.agents if agent.function_map]
    #             if len(agents) == 1:
    #                 return agents[0]
    #             elif not agents:
    #                 raise ValueError(
    #                     f"No agent can execute the function {self.messages[-1]['name']}. "
    #                     "Please check the function_map of the agents."
    #                 )
    #     else:
    #         agents = self.agents
    #         # Warn if GroupChat is underpopulated
    #         n_agents = len(agents)
    #         if n_agents < 3:
    #             logger.warning(
    #                 f"GroupChat is underpopulated with {n_agents} agents. Direct communication would be more efficient."
    #             )
    #     selector.update_system_message(self.select_speaker_msg(agents))
    #     final, name = selector.generate_oai_reply(
    #         self.messages
    #         + [
    #             {
    #                 "role": "system",
    #                 "content": f"Read the above conversation. Then select the next role from {[agent.name for agent in agents]} to play. Only return the role.",
    #             }
    #         ]
    #     )
    #     if not final:
    #         # i = self._random.randint(0, len(self._agent_names) - 1)  # randomly pick an id
    #         return self.next_agent(last_speaker, agents)
    #     try:
    #         return self.agent_by_name(name)
    #     except ValueError:
    #         return self.next_agent(last_speaker, agents)


    def select_speaker(self, last_speaker: Agent, selector: ConversableAgent):
        # Check if last message suggests a next speaker or termination
        last_message = self.messages[-1] if self.messages else None
        if last_message:
            if 'NEXT:' in last_message['content']:
                suggested_next = last_message['content'].split('NEXT: ')[-1].strip()
                print(f'Extracted suggested_next = {suggested_next}')
                try:
                    return self.agent_by_name(suggested_next)
                except ValueError:
                    pass  # If agent name is not valid, continue with normal selection
            elif 'TERMINATE' in last_message['content']:
                try:
                    return self.agent_by_name('User_proxy')
                except ValueError:
                    pass  # If 'User_proxy' is not a valid name, continue with normal selection

        team_leader_names = [agent.name for agent in self.agents if agent.name.endswith('1')]

        if last_speaker.name in team_leader_names:
            team_letter = last_speaker.name[0]
            possible_next_speakers = [
                agent for agent in self.agents if (agent.name.startswith(team_letter) or agent.name in team_leader_names)
                and agent != last_speaker and agent != self.previous_speaker
            ]
        else:
            team_letter = last_speaker.name[0]
            possible_next_speakers = [
                agent for agent in self.agents if agent.name.startswith(team_letter)
                and agent != last_speaker and agent != self.previous_speaker
            ]

        self.previous_speaker = last_speaker

        if possible_next_speakers:
            next_speaker = random.choice(possible_next_speakers)
            return next_speaker
        else:
            return None


    def _participant_roles(self):
        return "\n".join([f"{agent.name}: {agent.system_message}" for agent in self.agents])