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


def hybrid_search(query, class_name, properties, keyword):
    """
    Perform a hybrid search in Weaviate.

    :param query: The vector search query.
    :param class_name: The Weaviate class to search in.
    :param properties: List of properties to retrieve.
    :param keyword: Keyword for traditional search.
    :return: Search results combining vector and keyword search.
    """
    return client.query.get(class_name, properties)\
        .with_near_text({
            "concepts": [query]
        })\
        .with_where({
            "operator": "Equal",
            "operands": [
                {"path": ["propertyName"],
                 "valueString": keyword},
                {"valueText": query}
            ]
        })\
        .do()
