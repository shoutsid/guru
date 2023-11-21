from client import client


def vector_search(query, class_name, properties):
    """
    Perform a vector search in Weaviate.

    :param query: The search query.
    :param class_name: The Weaviate class to search in.
    :param properties: List of properties to retrieve.
    :return: Search results.
    """
    return client.query.get(class_name, properties)\
        .with_near_text({
            "concepts": [query]
        })\
        .do()


def generative_search(query, class_name, properties, prompt_template):
    """
    Perform a generative search in Weaviate.

    :param query: The search query.
    :param class_name: The Weaviate class to search in.
    :param properties: List of properties to retrieve.
    :param prompt_template: Template for the generative prompt.
    :return: Search results with generated content.
    """
    result = client.query.get(class_name, properties)\
        .with_near_text({
            "concepts": [query]
        })\
        .with_generate(prompt_template)\
        .do()
    return result


def search_discord_messages(query, class_name, limit=1):
    prompt = "Generate a message similar to the following message: {content}"
    result = (
        client.query
        .get(class_name, ["content"])
        .with_near_text({"concepts": [query], "distance": 0.7})
        .with_limit(limit)
        .with_generate(single_prompt=prompt)
        .do()
    )

    # Check for errors
    if ("errors" in result):
        print("\033[91mYou probably have run out of OpenAI API calls for the current minute – the limit is set at 60 per minute.")
        raise Exception(result["errors"][0]['message'])

    return result["data"]["Get"][class_name]


def search_discord_messages2():
    properties = [
        "content",
        "_additional { answer { hasAnswer property result startPosition endPosition } distance }"
    ]

    ask = {
        "question": "Who is Sid?",
        "properties": ["summary"]
    }

    result = (
        client.query
        .get('DiscordMessage', properties)
        .with_ask(ask)
        .with_limit(1)
        .do()
    )
    # Check for errors
    if ("errors" in result):
        raise Exception(result["errors"][0]['message'])

    return result["data"]["Get"]['DiscordMessage']


if __name__ == "__main__":
    print(search_discord_messages2())
