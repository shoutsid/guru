from collections import defaultdict
import numpy as np
import weaviate
from typing import List, Dict
from client import client


def retrieve_vectorized_discord_messages(client: weaviate.Client) -> List[Dict]:
    """
    Retrieve vectorized DiscordMessage entries from the Weaviate database.

    :param client: An instance of the Weaviate client.
    :return: A list of dictionaries, each containing the content, vector, and metadata of a DiscordMessage.
    """
    query = """
    {
        Get {
            DiscordMessage {
                content
                author_id
                channel_id
                guild_id
                _additional {
                    id
                    vector
                }
            }
        }
    }
    """
    try:
        result = client.query.raw(query)
        print(result)
        messages = result['data']['Get']['DiscordMessage']
        return messages
    except Exception as e:
        print(f"Error retrieving messages: {e}")
        return []


def aggregate_to_user_profiles(messages: List[Dict]) -> Dict[int, np.ndarray]:
    """
    Aggregate message vectors to create user profiles.

    :param messages: A list of dictionaries, each containing message data and vector.
    :return: A dictionary where keys are author_ids and values are averaged vectors.
    """
    user_vectors = defaultdict(list)
    for message in messages:
        author_id = message.get('author_id')
        vector = message['_additional'].get('vector')
        # Filter out messages with no author_id or vector
        if author_id is not None and vector is not None:
            user_vectors[author_id].append(vector)

    # Calculate average vector for each user
    user_profiles = {author_id: np.mean(
        np.array(vectors), axis=0) for author_id, vectors in user_vectors.items()}
    return user_profiles


def create_user_profile_class(client: weaviate.Client):
    """
    Create a 'UserProfile' class in Weaviate to store user profiles.

    :param client: An instance of the Weaviate client.
    """
    schema = {
        "classes": [
            {
                "class": "UserProfile",
                "description": "A profile of a user based on their message history",
                "properties": [
                    {
                        "name": "author_id",
                        "dataType": ["int"],
                        "description": "The ID of the author"
                    },
                    {
                        "name": "vector",
                        "dataType": ["number[]"],
                        "description": "The aggregated vector representing the user's profile"
                    }
                ]
            }
        ]
    }

    client.schema.create(schema)


def store_user_profiles(client: weaviate.Client, user_profiles: Dict[int, np.ndarray]):
    """
    Store the aggregated user profiles in Weaviate.

    :param client: An instance of the Weaviate client.
    :param user_profiles: A dictionary of user profiles with author_id as key and vector as value.
    """
    for author_id, vector in user_profiles.items():
        user_profile_data = {
            "author_id": author_id,
            "vector": vector.tolist()  # Converting numpy array to list for storage
        }
        client.data_object.create(
            data_object=user_profile_data, class_name="UserProfile")


def retrieve_user_profile(client: weaviate.Client, author_id: int) -> np.ndarray:
    """
    Retrieve a user's profile vector from Weaviate.

    :param client: An instance of the Weaviate client.
    :param author_id: The author ID of the user.
    :return: The user's profile vector as a numpy array.
    """
    query = f"""
    {{
        Get {{
            UserProfile(
                where: {{
                    path: ["author_id"]
                    operator: Equal
                    valueInt: {author_id}
                }}
            ) {{
                author_id
                vector
            }}
        }}
    }}
    """
    try:
        result = client.query.raw(query)
        vector_data = result['data']['Get']['UserProfile']
        if vector_data:
            vector = np.array(vector_data[0]['vector'])
            return vector
        else:
            return None
    except Exception as e:
        print(f"Error retrieving user profile: {e}")
        return None

# Analyze a user's profile vector


def analyze_user_profile(user_profile: dict) -> dict:
    """
    Analyze a user's profile vector to infer characteristics.

    :param user_profile: A dictionary containing the user's profile data.
    :return: A dictionary with inferred characteristics.
    """
    # Placeholder for actual analysis logic
    # The analysis would depend on how the vectors were created and what they represent
    characteristics = {}

    # Example: infer some characteristics based on vector analysis
    # This is a simplified representation and should be replaced with actual analysis
    vector = user_profile.get('vector', [])
    if len(vector) > 0:
        # Perform analysis to infer characteristics
        characteristics['interest'] = "Sample Interest"  # Example placeholder

    return characteristics


if __name__ == "__main__":
    messages = retrieve_vectorized_discord_messages(client)
    # print(messages)
    user_profiles = aggregate_to_user_profiles(messages)
    print(user_profiles)

    # create_user_profile_class(client)
    # print("Created user profile class in Weaviate")

    store_user_profiles(client, user_profiles)
    print("Stored user profiles in Weaviate")

    # user_vector = retrieve_user_profile(client, author_id)
    # print(user_vector)  # This will print the user's profile vector.
