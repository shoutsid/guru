from __future__ import annotations
import json
import time
import logging
from typing import Any, Dict, List, Optional, Tuple, Union
import spacy
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk

nltk.download('vader_lexicon')
nltk.download('punkt')
nltk.download('stopwords')

from autogen import oai

from autogen.agentchat.agent import Agent
from autogen.agentchat.assistant_agent import ConversableAgent
from autogen.agentchat.assistant_agent import AssistantAgent
from typing import Dict, Optional, Union, List, Tuple, Any

logger = logging.getLogger(__name__)

from collections import defaultdict
import os
import sys
from typing import List, Optional, Dict, Callable
import logging
import inspect
from flaml.automl.logger import logger_formatter

from autogen.oai.openai_utils import get_key
from autogen.token_count_utils import count_token

try:
    from openai import OpenAI, APIError
    from openai.types.chat import ChatCompletion
    from openai.types.chat.chat_completion import ChatCompletionMessage, Choice
    from openai.types.completion import Completion
    from openai.types.completion_usage import CompletionUsage
    import diskcache

    ERROR = None
except ImportError:
    ERROR = ImportError("Please install openai>=1 and diskcache to use autogen.OpenAIWrapper.")
    OpenAI = object
logger = logging.getLogger(__name__)
if not logger.handlers:
    # Add the console handler.
    _ch = logging.StreamHandler(stream=sys.stdout)
    _ch.setFormatter(logger_formatter)
    logger.addHandler(_ch)

# from townhall.db.agent import Agent as AgentModel
# from townhall.db.utils import Session, SQL_ENGINE

# session = Session(SQL_ENGINE)

class OpenAIWrapper:
    """A wrapper class for openai client."""

    cache_path_root: str = ".cache"
    extra_kwargs = {"cache_seed", "filter_func", "allow_format_str_template", "context", "api_version"}
    openai_kwargs = set(inspect.getfullargspec(OpenAI.__init__).kwonlyargs)

    def __init__(self, *, config_list: List[Dict] = None, **base_config):
        """
        Args:
            config_list: a list of config dicts to override the base_config.
                They can contain additional kwargs as allowed in the [create](/docs/reference/oai/client#create) method. E.g.,

        ```python
        config_list=[
            {
                "model": "gpt-4",
                "api_key": os.environ.get("AZURE_OPENAI_API_KEY"),
                "api_type": "azure",
                "base_url": os.environ.get("AZURE_OPENAI_API_BASE"),
                "api_version": "2023-03-15-preview",
            },
            {
                "model": "gpt-3.5-turbo",
                "api_key": os.environ.get("OPENAI_API_KEY"),
                "api_type": "open_ai",
                "base_url": "https://api.openai.com/v1",
            },
            {
                "model": "llama-7B",
                "base_url": "http://127.0.0.1:8080",
                "api_type": "open_ai",
            }
        ]
        ```

            base_config: base config. It can contain both keyword arguments for openai client
                and additional kwargs.
        """
        openai_config, extra_kwargs = self._separate_openai_config(base_config)
        if type(config_list) is list and len(config_list) == 0:
            logger.warning("openai client was provided with an empty config_list, which may not be intended.")
        if config_list:
            config_list = [config.copy() for config in config_list]  # make a copy before modifying
            self._clients = [self._client(config, openai_config) for config in config_list]  # could modify the config
            self._config_list = [
                {**extra_kwargs, **{k: v for k, v in config.items() if k not in self.openai_kwargs}}
                for config in config_list
            ]
        else:
            self._clients = [self._client(extra_kwargs, openai_config)]
            self._config_list = [extra_kwargs]

    def _process_for_azure(self, config: Dict, extra_kwargs: Dict, segment: str = "default"):
        # deal with api_version
        query_segment = f"{segment}_query"
        headers_segment = f"{segment}_headers"
        api_version = extra_kwargs.get("api_version")
        if api_version is not None and query_segment not in config:
            config[query_segment] = {"api-version": api_version}
            if segment == "default":
                # remove the api_version from extra_kwargs
                extra_kwargs.pop("api_version")
        if segment == "extra":
            return
        # deal with api_type
        api_type = extra_kwargs.get("api_type")
        if api_type is not None and api_type.startswith("azure") and headers_segment not in config:
            api_key = config.get("api_key", os.environ.get("AZURE_OPENAI_API_KEY"))
            config[headers_segment] = {"api-key": api_key}
            # remove the api_type from extra_kwargs
            extra_kwargs.pop("api_type")
            # deal with model
            model = extra_kwargs.get("model")
            if model is None:
                return
            if "gpt-3.5" in model:
                # hack for azure gpt-3.5
                extra_kwargs["model"] = model = model.replace("gpt-3.5", "gpt-35")
            base_url = config.get("base_url")
            if base_url is None:
                raise ValueError("to use azure openai api, base_url must be specified.")
            suffix = f"/openai/deployments/{model}"
            if not base_url.endswith(suffix):
                config["base_url"] += suffix[1:] if base_url.endswith("/") else suffix

    def _separate_openai_config(self, config):
        """Separate the config into openai_config and extra_kwargs."""
        openai_config = {k: v for k, v in config.items() if k in self.openai_kwargs}
        extra_kwargs = {k: v for k, v in config.items() if k not in self.openai_kwargs}
        self._process_for_azure(openai_config, extra_kwargs)
        return openai_config, extra_kwargs

    def _separate_create_config(self, config):
        """Separate the config into create_config and extra_kwargs."""
        create_config = {k: v for k, v in config.items() if k not in self.extra_kwargs}
        extra_kwargs = {k: v for k, v in config.items() if k in self.extra_kwargs}
        return create_config, extra_kwargs

    def _client(self, config, openai_config):
        """Create a client with the given config to overrdie openai_config,
        after removing extra kwargs.
        """
        openai_config = {**openai_config, **{k: v for k, v in config.items() if k in self.openai_kwargs}}
        self._process_for_azure(openai_config, config)
        client = OpenAI(**openai_config)
        return client

    @classmethod
    def instantiate(
        cls,
        template: str | Callable | None,
        context: Optional[Dict] = None,
        allow_format_str_template: Optional[bool] = False,
    ):
        if not context or template is None:
            return template
        if isinstance(template, str):
            return template.format(**context) if allow_format_str_template else template
        return template(context)

    def _construct_create_params(self, create_config: Dict, extra_kwargs: Dict) -> Dict:
        """Prime the create_config with additional_kwargs."""
        # Validate the config
        prompt = create_config.get("prompt")
        messages = create_config.get("messages")
        if (prompt is None) == (messages is None):
            raise ValueError("Either prompt or messages should be in create config but not both.")
        context = extra_kwargs.get("context")
        if context is None:
            # No need to instantiate if no context is provided.
            return create_config
        # Instantiate the prompt or messages
        allow_format_str_template = extra_kwargs.get("allow_format_str_template", False)
        # Make a copy of the config
        params = create_config.copy()
        if prompt is not None:
            # Instantiate the prompt
            params["prompt"] = self.instantiate(prompt, context, allow_format_str_template)
        elif context:
            # Instantiate the messages
            params["messages"] = [
                {
                    **m,
                    "content": self.instantiate(m["content"], context, allow_format_str_template),
                }
                if m.get("content")
                else m
                for m in messages
            ]
        return params

    def create(self, **config):
        """Make a completion for a given config using openai's clients.
        Besides the kwargs allowed in openai's client, we allow the following additional kwargs.
        The config in each client will be overriden by the config.

        Args:
            - context (Dict | None): The context to instantiate the prompt or messages. Default to None.
                It needs to contain keys that are used by the prompt template or the filter function.
                E.g., `prompt="Complete the following sentence: {prefix}, context={"prefix": "Today I feel"}`.
                The actual prompt will be:
                "Complete the following sentence: Today I feel".
                More examples can be found at [templating](/docs/Use-Cases/enhanced_inference#templating).
            - `cache_seed` (int | None) for the cache. Default to 41.
                An integer cache_seed is useful when implementing "controlled randomness" for the completion.
                None for no caching.
            - filter_func (Callable | None): A function that takes in the context and the response
                and returns a boolean to indicate whether the response is valid. E.g.,

        ```python
        def yes_or_no_filter(context, response):
            return context.get("yes_or_no_choice", False) is False or any(
                text in ["Yes.", "No."] for text in client.extract_text_or_function_call(response)
            )
        ```

            - allow_format_str_template (bool | None): Whether to allow format string template in the config. Default to false.
            - api_version (str | None): The api version. Default to None. E.g., "2023-08-01-preview".
        """
        if ERROR:
            raise ERROR
        last = len(self._clients) - 1
        for i, client in enumerate(self._clients):
            # merge the input config with the i-th config in the config list
            full_config = {**config, **self._config_list[i]}
            # separate the config into create_config and extra_kwargs
            create_config, extra_kwargs = self._separate_create_config(full_config)
            # process for azure
            self._process_for_azure(create_config, extra_kwargs, "extra")
            # construct the create params
            params = self._construct_create_params(create_config, extra_kwargs)
            # get the cache_seed, filter_func and context
            cache_seed = extra_kwargs.get("cache_seed", 41)
            filter_func = extra_kwargs.get("filter_func")
            context = extra_kwargs.get("context")
            with diskcache.Cache(f"{self.cache_path_root}/{cache_seed}") as cache:
                if cache_seed is not None:
                    # Try to get the response from cache
                    key = get_key(params)
                    response = cache.get(key, None)
                    if response is not None:
                        # check the filter
                        pass_filter = filter_func is None or filter_func(context=context, response=response)
                        if pass_filter or i == last:
                            # Return the response if it passes the filter or it is the last client
                            response.config_id = i
                            response.pass_filter = pass_filter
                            # TODO: add response.cost
                            return response
                try:
                    response = self._completions_create(client, params)
                except APIError:
                    logger.debug(f"config {i} failed", exc_info=1)
                    if i == last:
                        raise
                else:
                    if cache_seed is not None:
                        # Cache the response
                        cache.set(key, response)
                    return response

    def _completions_create(self, client, params):
        completions = client.chat.completions if "messages" in params else client.completions
        # If streaming is enabled, has messages, and does not have functions, then
        # iterate over the chunks of the response
        if params.get("stream", False) and "messages" in params and "functions" not in params:
            response_contents = [""] * params.get("n", 1)
            finish_reasons = [""] * params.get("n", 1)
            completion_tokens = 0

            # Set the terminal text color to green
            print("\033[32m", end="")

            # Send the chat completion request to OpenAI's API and process the response in chunks
            for chunk in completions.create(**params):
                if chunk.choices:
                    for choice in chunk.choices:
                        content = choice.delta.content
                        finish_reasons[choice.index] = choice.finish_reason
                        # If content is present, print it to the terminal and update response variables
                        if content is not None:
                            print(content, end="", flush=True)
                            response_contents[choice.index] += content
                            completion_tokens += 1
                        else:
                            print()

            # Reset the terminal text color
            print("\033[0m\n")

            # Prepare the final ChatCompletion object based on the accumulated data
            model = chunk.model.replace("gpt-35", "gpt-3.5")  # hack for Azure API
            prompt_tokens = count_token(params["messages"], model)
            response = ChatCompletion(
                id=chunk.id,
                model=chunk.model,
                created=chunk.created,
                object="chat.completion",
                choices=[],
                usage=CompletionUsage(
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=prompt_tokens + completion_tokens,
                ),
            )
            for i in range(len(response_contents)):
                response.choices.append(
                    Choice(
                        index=i,
                        finish_reason=finish_reasons[i],
                        message=ChatCompletionMessage(
                            role="assistant", content=response_contents[i], function_call=None
                        ),
                    )
                )
        else:
            # If streaming is not enabled or using functions, send a regular chat completion request
            # Functions are not supported, so ensure streaming is disabled
            params = params.copy()
            params["stream"] = False
            response = completions.create(**params)
        return response

    @classmethod
    def extract_text_or_function_call(cls, response: ChatCompletion | Completion) -> List[str]:
        """Extract the text or function calls from a completion or chat response.

        Args:
            response (ChatCompletion | Completion): The response from openai.

        Returns:
            A list of text or function calls in the responses.
        """
        choices = response.choices
        if isinstance(response, Completion):
            return [choice.text for choice in choices]
        return [
            choice.message if choice.message.function_call is not None else choice.message.content for choice in choices
        ]


class GPTAssistantAgent(ConversableAgent):
    """
    An experimental AutoGen agent class that leverages the OpenAI Assistant API for conversational capabilities.
    This agent is unique in its reliance on the OpenAI Assistant for state management, differing from other agents like ConversableAgent.
    """

    def __init__(
        self,
        name="GPT Assistant",
        instructions: Optional[str] = None,
        llm_config: Optional[Union[Dict, bool]] = None,
        overwrite_instructions: bool = False,
        db_agent_id: Optional[Any] = None,
    ):
        """
        Args:
            name (str): name of the agent.
            instructions (str): instructions for the OpenAI assistant configuration.
            When instructions is not None, the system message of the agent will be
            set to the provided instructions and used in the assistant run, irrespective
            of the overwrite_instructions flag. But when instructions is None,
            and the assistant does not exist, the system message will be set to
            AssistantAgent.DEFAULT_SYSTEM_MESSAGE. If the assistant exists, the
            system message will be set to the existing assistant instructions.
            llm_config (dict or False): llm inference configuration.
                - assistant_id: ID of the assistant to use. If None, a new assistant will be created.
                - model: Model to use for the assistant (gpt-4-1106-preview, gpt-3.5-turbo-1106).
                - check_every_ms: check thread run status interval
                - tools: Give Assistants access to OpenAI-hosted tools like Code Interpreter and Knowledge Retrieval,
                        or build your own tools using Function calling. ref https://platform.openai.com/docs/assistants/tools
                - file_ids: files used by retrieval in run
            overwrite_instructions (bool): whether to overwrite the instructions of an existing assistant.
        """
        # Use AutoGen OpenAIWrapper to create a client
        oai_wrapper = OpenAIWrapper(**llm_config)
        if len(oai_wrapper._clients) > 1:
            logger.warning("GPT Assistant only supports one OpenAI client. Using the first client in the list.")
        self._openai_client = oai_wrapper._clients[0]

        # retrieve an existing agent
        # db_agent = session.get(AgentModel, db_agent_id)
        # if db_agent is None:
        #     raise ValueError(f"Agent with id {db_agent_id} does not exist.")

        openai_assistant_id = llm_config.get("assistant_id", None)
        # openai_assistant_id = db_agent.openai_id if db_agent else None

        if openai_assistant_id is None:
            # create a new assistant
            if instructions is None:
                logger.warning(
                    "No instructions were provided for new assistant. Using default instructions from AssistantAgent.DEFAULT_SYSTEM_MESSAGE."
                )
                instructions = AssistantAgent.DEFAULT_SYSTEM_MESSAGE
            self._openai_assistant = self._openai_client.beta.assistants.create(
                name=name,
                instructions=instructions,
                tools=llm_config.get("tools", [{"type": "code_interpreter"}, {"type": "retrieval"}]),
                model=llm_config.get("model", "gpt-4-1106-preview"),
            )
            # update the agent with the assistant id
            # db_agent.openai_id = self._openai_assistant.id
            # session.commit()
            # session.refresh(db_agent)
        else:
            # retrieve an existing assistant
            self._openai_assistant = self._openai_client.beta.assistants.retrieve(openai_assistant_id)
            # if no instructions are provided, set the instructions to the existing instructions
            if instructions is None:
                logger.warning(
                    "No instructions were provided for given assistant. Using existing instructions from assistant API."
                )
                instructions = self.get_assistant_instructions()
            elif overwrite_instructions is True:
                logger.warning(
                    "overwrite_instructions is True. Provided instructions will be used and will modify the assistant in the API"
                )
                self._openai_assistant = self._openai_client.beta.assistants.update(
                    assistant_id=openai_assistant_id,
                    instructions=instructions,
                )
            else:
                logger.warning(
                    "overwrite_instructions is False. Provided instructions will be used without permanently modifying the assistant in the API."
                )

        super().__init__(
            name=name,
            system_message=instructions,
            human_input_mode="NEVER",
            llm_config=llm_config,
        )

        # lazly create thread
        self._openai_threads = {}
        self._unread_index = defaultdict(int)
        self.register_reply(Agent, GPTAssistantAgent._invoke_assistant)

    def _invoke_assistant(
        self,
        messages: Optional[List[Dict]] = None,
        sender: Optional[Agent] = None,
        config: Optional[Any] = None,
    ) -> Tuple[bool, Union[str, Dict, None]]:
        """
        Invokes the OpenAI assistant to generate a reply based on the given messages.

        Args:
            messages: A list of messages in the conversation history with the sender.
            sender: The agent instance that sent the message.
            config: Optional configuration for message processing.

        Returns:
            A tuple containing a boolean indicating success and the assistant's reply.
        """

        if messages is None:
            messages = self._oai_messages[sender]
        unread_index = self._unread_index[sender] or 0
        pending_messages = messages[unread_index:]

        # Check and initiate a new thread if necessary
        if self._openai_threads.get(sender, None) is None:
            self._openai_threads[sender] = self._openai_client.beta.threads.create(
                messages=[],
            )
        assistant_thread = self._openai_threads[sender]
        # Process each unread message
        for message in pending_messages:
            self._openai_client.beta.threads.messages.create(
                thread_id=assistant_thread.id,
                content=message["content"],
                role=message["role"],
            )

        # Create a new run to get responses from the assistant
        run = self._openai_client.beta.threads.runs.create(
            thread_id=assistant_thread.id,
            assistant_id=self._openai_assistant.id,
            # pass the latest system message as instructions
            instructions=self.system_message,
        )

        run_response_messages = self._get_run_response(assistant_thread, run)
        assert len(run_response_messages) > 0, "No response from the assistant."

        response = {
            "role": run_response_messages[-1]["role"],
            "content": "",
        }
        for message in run_response_messages:
            # just logging or do something with the intermediate messages?
            # if current response is not empty and there is more, append new lines
            if len(response["content"]) > 0:
                response["content"] += "\n\n"
            response["content"] += message["content"]

        self._unread_index[sender] = len(self._oai_messages[sender]) + 1
        return True, response

    def analyze_conversation(self, agent: Optional[Agent] = None):
        nlp = spacy.load("en_core_web_sm")
        analyzer = SentimentIntensityAnalyzer()

        messages = self._oai_messages.get(agent, [])
        conversation_analysis = {
            "topics": {},
            "entities": {},
            "opinions": {}
        }

        for message in messages:
            # NLP processing
            doc = nlp(message["content"])

            # Named Entity Recognition
            for ent in doc.ents:
                conversation_analysis["entities"][ent.text] = ent.label_

            # Opinion Mining and Sentiment Analysis
            for sent in doc.sents:
                sentiment_score = analyzer.polarity_scores(sent.text)["compound"]
                conversation_analysis["opinions"][sent.text] = sentiment_score

        return conversation_analysis


    def _get_run_response(self, thread, run):
        """
        Waits for and processes the response of a run from the OpenAI assistant.

        Args:
            run: The run object initiated with the OpenAI assistant.

        Returns:
            Updated run object, status of the run, and response messages.
        """
        while True:
            run = self._wait_for_run(run.id, thread.id)
            if run.status == "completed":
                response_messages = self._openai_client.beta.threads.messages.list(thread.id, order="asc")

                new_messages = []
                for msg in response_messages:
                    if msg.run_id == run.id:
                        for content in msg.content:
                            if content.type == "text":
                                new_messages.append(
                                    {"role": msg.role, "content": self._format_assistant_message(content.text)}
                                )
                            elif content.type == "image_file":
                                new_messages.append(
                                    {
                                        "role": msg.role,
                                        "content": f"Recieved file id={content.image_file.file_id}",
                                    }
                                )
                return new_messages
            elif run.status == "requires_action":
                actions = []
                for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                    function = tool_call.function
                    is_exec_success, tool_response = self.execute_function(function.dict())
                    tool_response["metadata"] = {
                        "tool_call_id": tool_call.id,
                        "run_id": run.id,
                        "thread_id": thread.id,
                    }

                    logger.info(
                        "Intermediate executing(%s, Sucess: %s) : %s",
                        tool_response["name"],
                        is_exec_success,
                        tool_response["content"],
                    )
                    actions.append(tool_response)

                submit_tool_outputs = {
                    "tool_outputs": [
                        {"output": action["content"], "tool_call_id": action["metadata"]["tool_call_id"]}
                        for action in actions
                    ],
                    "run_id": run.id,
                    "thread_id": thread.id,
                }

                run = self._openai_client.beta.threads.runs.submit_tool_outputs(**submit_tool_outputs)
            else:
                run_info = json.dumps(run.dict(), indent=2)
                raise ValueError(f"Unexpected run status: {run.status}. Full run info:\n\n{run_info})")

    def _wait_for_run(self, run_id: str, thread_id: str) -> Any:
        """
        Waits for a run to complete or reach a final state.

        Args:
            run_id: The ID of the run.
            thread_id: The ID of the thread associated with the run.

        Returns:
            The updated run object after completion or reaching a final state.
        """
        in_progress = True
        while in_progress:
            run = self._openai_client.beta.threads.runs.retrieve(run_id, thread_id=thread_id)
            in_progress = run.status in ("in_progress", "queued")
            if in_progress:
                time.sleep(self.llm_config.get("check_every_ms", 1000) / 1000)
        return run

    def _format_assistant_message(self, message_content):
        """
        Formats the assistant's message to include annotations and citations.
        """

        annotations = message_content.annotations
        citations = []

        # Iterate over the annotations and add footnotes
        for index, annotation in enumerate(annotations):
            # Replace the text with a footnote
            message_content.value = message_content.value.replace(annotation.text, f" [{index}]")

            # Gather citations based on annotation attributes
            if file_citation := getattr(annotation, "file_citation", None):
                try:
                    cited_file = self._openai_client.files.retrieve(file_citation.file_id)
                    citations.append(f"[{index}] {cited_file.filename}: {file_citation.quote}")
                except Exception as e:
                    logger.error(f"Error retrieving file citation: {e}")
            elif file_path := getattr(annotation, "file_path", None):
                try:
                    cited_file = self._openai_client.files.retrieve(file_path.file_id)
                    citations.append(f"[{index}] Click <here> to download {cited_file.filename}")
                except Exception as e:
                    logger.error(f"Error retrieving file citation: {e}")
                # Note: File download functionality not implemented above for brevity

        # Add footnotes to the end of the message before displaying to user
        message_content.value += "\n" + "\n".join(citations)
        return message_content.value

    def can_execute_function(self, name: str) -> bool:
        """Whether the agent can execute the function."""
        return False

    def reset(self):
        """
        Resets the agent, clearing any existing conversation thread and unread message indices.
        """
        super().reset()
        for thread in self._openai_threads.values():
            # Delete the existing thread to start fresh in the next conversation
            self._openai_client.beta.threads.delete(thread.id)
        self._openai_threads = {}
        # Clear the record of unread messages
        self._unread_index.clear()

    def clear_history(self, agent: Optional[Agent] = None):
        """Clear the chat history of the agent.

        Args:
            agent: the agent with whom the chat history to clear. If None, clear the chat history with all agents.
        """
        super().clear_history(agent)
        if self._openai_threads.get(agent, None) is not None:
            # Delete the existing thread to start fresh in the next conversation
            thread = self._openai_threads[agent]
            logger.info("Clearing thread %s", thread.id)
            self._openai_client.beta.threads.delete(thread.id)
            self._openai_threads.pop(agent)
            self._unread_index[agent] = 0

    def pretty_print_thread(self, thread):
        """Pretty print the thread."""
        if thread is None:
            print("No thread to print")
            return
        # NOTE: that list may not be in order, sorting by created_at is important
        messages = self._openai_client.beta.threads.messages.list(
            thread_id=thread.id,
        )
        messages = sorted(messages.data, key=lambda x: x.created_at)
        print("~~~~~~~THREAD CONTENTS~~~~~~~")
        for message in messages:
            content_types = [content.type for content in message.content]
            print(f"[{message.created_at}]", message.role, ": [", ", ".join(content_types), "]")
            for content in message.content:
                content_type = content.type
                if content_type == "text":
                    print(content.type, ": ", content.text.value)
                elif content_type == "image_file":
                    print(content.type, ": ", content.image_file.file_id)
                else:
                    print(content.type, ": ", content)
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

    @property
    def oai_threads(self) -> Dict[Agent, Any]:
        """Return the threads of the agent."""
        return self._openai_threads

    @property
    def assistant_id(self):
        """Return the assistant id"""
        return self._openai_assistant.id

    def get_assistant_instructions(self):
        """Return the assistant instructions from OAI assistant API"""
        return self._openai_assistant.instructions

    def delete_assistant(self):
        """Delete the assistant from OAI assistant API"""
        self._openai_client.beta.assistants.delete(self.assistant_id)

class EnhancedTeachableAgent(GPTAssistantAgent):
    pass
