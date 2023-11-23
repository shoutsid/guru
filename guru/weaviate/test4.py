import openai
from typing import Any, Callable, Dict, List, get_type_hints
import inspect
from typing import Dict, Any, List
from client import client

from typing import List, Dict, Any


def python_type_to_openai_type(python_type: type) -> str:
    """
    Convert Python type hints to OpenAI API recognized types.

    Args:
        python_type (type): The Python type to be converted.

    Returns:
        str: The corresponding OpenAI API type as a string.
    """
    type_map = {
        int: "integer",
        float: "number",
        str: "string",
        list: "array",
        dict: "object",
        bool: "boolean"
        # Add more mappings as needed
    }
    # Default to "string" if type is not mapped
    return type_map.get(python_type, "string")


def openai_tool_decorator(func: Callable) -> Callable:
    """
    A decorator to automatically generate the 'tools' parameter for OpenAI chat completions.
    """
    tools = {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": func.__doc__,
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }

    signature = inspect.signature(func)
    type_hints = get_type_hints(func)

    for param_name, param in signature.parameters.items():
        param_type = python_type_to_openai_type(
            type_hints.get(param_name, Any))
        tools["function"]["parameters"]["properties"][param_name] = {
            "type": param_type}

        if param.default is inspect.Parameter.empty:
            tools["function"]["parameters"]["required"].append(param_name)

    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    wrapper.tools = tools
    return wrapper


@openai_tool_decorator
def get_data_with_near_text(
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
        single_prompt (str): The single prompt to generate data
        distance (float, optional): The distance threshold for near text search. Defaults to 0.7.
        limit (int, optional): The maximum number of results to retrieve. Defaults to 1.

    Returns:
        List[Dict[str, Any]]: The retrieved data from Weaviate.
    """
    # validate single_prompt is not empty
    if not single_prompt:
        raise Exception("single_prompt can not be empty.")

    response = client.query.get(entity_type, attributes).with_near_text(
        {"concepts": concepts, "distance": distance}
    ).with_limit(limit).with_generate(single_prompt=single_prompt).do()

    return response


def make_chat_completion_request_with_library(messages: List[Dict[str, Any]]) -> openai.ChatCompletion:
    tools_data = get_data_with_near_text.tools

    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        tools=[tools_data],
        tool_choice="auto"
    )

    return response


def do_task(messages):
    chat_completion = make_chat_completion_request_with_library(messages)
    created = chat_completion.created
    model = chat_completion.model
    object = chat_completion.object
    system_fingerprint = chat_completion.system_fingerprint
    usage = chat_completion.usage
    print(
        f"created: {created}\n model: {model}\n object: {object}\n system_fingerprint: {system_fingerprint}\n usage: {usage}\n")
    for choice in chat_completion.choices:
        finish_reason = choice.finish_reason
        print("finish_reason:", finish_reason)
        message = choice.message
        print("message:", message)
        index = choice.index
        print("index:", index)

        if message:
            role = message.role
            print("role:", role)
            content = message.content
            print("content:", content)

            if role == "system":
                print("system content:", content)
            elif role == "user":
                print("user content:", content)
            elif role == "assistant":
                print("assistant content:", content)
            else:
                print("unknown role:", role)

            if message.tool_calls:
                tool_calls = message.tool_calls
                print("tool_calls:", tool_calls)
                try:
                    for tool_call in tool_calls:
                        function_name = tool_call.function.name
                        function_args = tool_call.function.arguments

                        print("function:", function_name)
                        # call the function with the arguments
                        # and get the response. The function is not callable
                        func = globals().get(function_name) or locals().get(function_name)

                        if func and callable(func):
                            # function_args example: '{\n  "entity_type": "DiscordMessage",\n  "attributes": "content",\n  "concepts": "love",\n  "single_prompt": ""\n}'
                            # convert json string to args
                            # catch errors and feedback to llm to fix
                            args = eval(function_args)
                            response = func(**args)
                            print("response:", response)
                        else:
                            print(
                                f"Function {function_name} not found or not callable.")
                except Exception as e:
                    print("error:", e)
                    messages.append({
                        "role": "user",
                        "content": str(e)
                    })
                    do_task(messages)


if __name__ == "__main__":
    messages = []
    system_message = """
    Fetch data from DiscordMessage regarding previous interactions.
    This entity has an attribute called content.
    You can query any concept and prompt you desire.
    The single_prompt can not be empty and if not user context is given assume the change.
    single_prompt is the prompt to generate data, it can be empty so if you want to generate data based on the previous prompt, you can do that.
    """
    messages.append({
        "role": "system",
        "content": system_message
    })
    messages.append({
        "role": "user",
        "content": "I want to see all messages that contain the concept of love."
    })
    messages.append({
        "role": "user",
        "content": 'The prompt is: "Craft a sympathic message for this content: {content}"'
    })

    do_task(messages)
