"""
TODO: Add nice discord responses (pages?)
TODO: Send back the audio to the channel along with the text, so that the user can hear the response when not in VC.
TODO: Record stream to text stream, to a_initiate_chat stream, get response and stream text to voice, and then stream that to the voice channel.
"""

import autogen
from langchain.utilities.sql_database import SQLDatabase
from datetime import datetime
from openai.types.beta.thread import Thread as OpenAIThreadBase
from guru.api.kafka.producer import trigger_to_topic
import os
import discord
import time
from langchain.agents import load_tools
from langchain.tools import Tool
from discord.ext import commands, tasks
from discord_bot.utils import INTENTS, logging, load_logger, DEFAULT_SYSTEM_MESSAGE, extract_file_path
from discord_bot.message_splitter import send_message_in_paragraphs
from guru.api.discord_guild_client import get_guild, create_guild, update_guild
from guru.api.discord_channel_client import get_channel, create_channel, update_channel
from guru.api.discord_thread_client import get_thread as get_discord_thread, create_thread as create_discord_thread, update_thread as update_discord_thread
from guru.api.discord_message_client import get_message as get_discord_message, create_message as create_discord_message, update_message as update_discord_message
from guru.api.discord_user_client import get_user, create_user, update_user
from guru.api.open_ai_assistant_client import get_assistant, create_assistant, update_assistant, list_assistants
from guru.api.open_ai_thread_client import get_thread as get_open_ai_thread, create_thread as create_open_ai_thread, update_thread as update_open_ai_thread, list_threads as list_open_ai_thread
from guru.api.open_ai_message_client import get_message as get_open_ai_message, create_message as create_open_ai_message, update_message as update_open_ai_message, list_messages as list_open_ai_message
from guru.agents.user_agent import UserAgent
from guru.agents.enhanced_teachable_agent import EnhancedTeachableAgent
from settings import CONFIG_LIST

load_logger()

DISCORD_BOT = commands.Bot(command_prefix='!', intents=INTENTS)

BOT_TOKEN = os.getenv("DISCORD_TOKEN")

# Not able to use these settings across every agent
# Use Cache isn't a thing now?
# "use_cache": True,  # Use False to explore LLM non-determinism.
# "request_timeout": 180,# ????? Why has this all of a sudden not allowed 2023-11-20 01:38:35 TypeError: create() got an unexpected keyword argument 'request_timeout'
# "retry_wait_time": 0.5,
# "max_retry_period": 360,
LLM_CONFIG = {
    "config_list": CONFIG_LIST,
}

# =========== EVENTS

@DISCORD_BOT.event
async def on_update_channel_messages(channel):
    try:
        async for message in channel.history():
            DISCORD_BOT.dispatch("message_update", message)
    except:
        logging.info("No permissions to channel %s", channel)

# ========== GUILD EVENTS ==========

@DISCORD_BOT.event
async def on_guild_update(before, after):
    DISCORD_BOT.dispatch("guild_available", after)

@DISCORD_BOT.event
async def on_guild_join(guild):
    DISCORD_BOT.dispatch("guild_available", guild)

@DISCORD_BOT.event
async def on_guild_available(guild):
    logging.info("Joined %s", guild)
    guild_data = {
        "discord_id": guild.id,
        "name": guild.name,
        "member_count": guild.member_count,
    }
    # find or create guild
    response = get_guild(guild.id)
    if response is None:
        logging.info("No guild found")
        logging.info("Creating a guild")
        guild_data = {
            "discord_id": guild.id,
            "name": guild.name,
            "member_count": guild.member_count,
        }
        create_guild(guild_data)
        logging.info("Sent guild create event")
    else:
        logging.info("Found guild")
        # update guild
        logging.info("Updating guild")
        update_guild(guild.id, guild_data)
        logging.info("Sent guild update event")

    # find or create channels
    for channel in guild.text_channels:
        DISCORD_BOT.dispatch("channel_available", channel)

    # find or create threads
    for thread in guild.threads:
        DISCORD_BOT.dispatch("handle_thread", thread)

    for member in guild.members:
        DISCORD_BOT.dispatch("handle_user", member)

# ========== CHANNEL EVENTS ==========

@DISCORD_BOT.event
async def on_update_channel(channel):
    DISCORD_BOT.dispatch("channel_available", channel)

@DISCORD_BOT.event
async def on_channel_available(channel):
    logging.info("Channel available: %s", channel)
    channel_data = {
        "discord_id": channel.id,
        "name": channel.name,
        "type": str(channel.type),
        "guild_id": channel.guild.id,
        "position": channel.position,
        "topic": channel.topic,
    }
    response = get_channel(channel.id)

    if response is None:
        logging.info("No channel found, creating a channel")
        create_channel(channel_data)
        logging.info("Sent Channel Creation Event")
    else:
        logging.info("Found channel, updating it")
        update_channel(channel.id, channel_data)
        logging.info("Sent Channel Update Event")

    # find or create messages
    async for message in channel.history():
        DISCORD_BOT.dispatch("handle_message", message)

# ========== DISCORD THREAD EVENTS ==========

THREADS = []

@DISCORD_BOT.event
async def on_thread_update(before, after):
    DISCORD_BOT.dispatch("handle_thread", after)

@DISCORD_BOT.event
async def on_handle_thread(thread):
    logging.info("Processing thread: %s", thread)
    thread_data = {
        "discord_id": thread.id,
        "name": thread.name,
        "type": str(thread.type),
        "owner_id": thread.owner_id,
        "parent_id": thread.parent_id,
        "archived": thread.archived,
        "auto_archive_duration": thread.auto_archive_duration,
    }

    response = get_discord_thread(thread.id)

    if response is None:
        logging.info("No thread found, creating a thread")
        response = create_discord_thread(thread_data)
        logging.info("Created thread: %s", response)
        THREADS.append(response)
    else:
        logging.info("Found thread, updating it")
        response = update_discord_thread(thread.id, thread_data)
        logging.info("Updated thread: %s", response)
        THREADS.append(response)

    # find or create messages
    async for message in thread.history():
        DISCORD_BOT.dispatch("handle_message", message)

# ========== DISCORD MESSAGE EVENTS ==========

MESSAGES = {}

@DISCORD_BOT.event
async def on_message_edit(before, after):
    DISCORD_BOT.dispatch("handle_message", after)

@DISCORD_BOT.event
async def on_handle_message(message):
    logging.info("Processing message: %s", message)
    guild_id = None
    if hasattr(message.guild, 'id'):
        guild_id = message.guild.id
    else:
        logging.info("No guild found for message %s", message)

    message_data = {
        "discord_id": message.id,
        "content": message.content,
        "author_id": message.author.id,
        "channel_id": message.channel.id,
        "guild_id": guild_id,
    }
    response = get_discord_message(message.id)

    if response is None:
        logging.info("No message found, creating a message")
        response = create_discord_message(message_data)
        logging.info("Created message: %s", response)
        MESSAGES[message.channel.id] = response
    else:
        logging.info("Found message, updating it")
        response = update_discord_message(message.id, message_data)
        logging.info("Updated message: %s", response)
        MESSAGES[message.channel.id] = response

OPEN_AI_ASSISTANTS = []
OPEN_AI_THREADS = []


@DISCORD_BOT.event
async def on_handle_openai_thread(thread_data):
    logging.info("Processing OpenAI Thread: %s",
                 thread_data.get("external_id"))
    thread_id = thread_data.get("external_id")

    response = get_open_ai_thread(thread_id)

    if response is None:
        logging.info("No thread found, creating a new one")
        response = create_open_ai_thread(thread_data)
        logging.info("Created OpenAI Thread: %s", response)
        OPEN_AI_THREADS.append(response)
    else:
        logging.info("Found thread, updating it")
        response = update_open_ai_thread(thread_id, thread_data)
        logging.info("Updated OpenAI Thread: %s", response)
        OPEN_AI_THREADS.append(response)


@DISCORD_BOT.event
async def on_handle_openai_message(message_data):
    logging.info("Processing OpenAI Message: %s",
                 message_data.get("external_id"))
    message_id = message_data.get("external_id")

    response = get_open_ai_message(message_id)

    if response is None:
        logging.info("No message found, creating a new one")
        response = create_open_ai_message(message_data)
        logging.info("Created OpenAI Message: %s", response)
        # Add additional logic as needed
    else:
        logging.info("Found message, updating it")
        response = update_open_ai_message(message_id, message_data)
        logging.info("Updated OpenAI Message: %s", response)


def run_postgres_query(query):
    database_uri = "postgresql://guru_api:@db/guru_api_production"
    postgres_db = SQLDatabase.from_uri(database_uri)
    return postgres_db.run(query)



def find_or_create_agents(author):
    user_agent_name = f"discord_member_{author.id}"
    teachable_agent_name = f"discord_assistant_{author.id}"
    current_message = DEFAULT_SYSTEM_MESSAGE
    config = LLM_CONFIG.copy()

    user_agent = generate_user_agent(name=user_agent_name, llm_config=config)
    user_execution_agent = generate_user_agent(
        name=f"{user_agent_name}_execution", llm_config=config, code_execution=True)

    assistants = list_assistants() or []

    for assistant in assistants:
        if assistant["name"] == teachable_agent_name:
            config["assistant_id"] = assistant["external_id"]
            break

    teachable_agent = EnhancedTeachableAgent(
        name=teachable_agent_name,
        llm_config=config,
        instructions=current_message
    )

    groupchat = autogen.GroupChat(
        agents=[user_agent, teachable_agent, user_execution_agent], messages=[], max_round=10)
    manager = autogen.GroupChatManager(
        groupchat=groupchat, llm_config=LLM_CONFIG)

    return manager, groupchat, user_agent, user_execution_agent, teachable_agent


def handle_role_message(role, teachable_agent, user_agent, oai_message):
    if role == 'assistant':
        teachable_agent._oai_messages[teachable_agent].append(oai_message)
        user_agent._oai_messages[teachable_agent].append(oai_message)
    else:
        oai_message['role'] = 'user'
        teachable_agent._oai_messages[user_agent].append(oai_message)
        user_agent._oai_messages[user_agent].append(oai_message)

def find_open_ai_thread(user):
    # find thread based on concept origins
    thread = None
    threads = list_open_ai_thread()
    logging.info("Threads: %s", threads)
    logging.info("Finding OpenAI Thread for %s", user.id)
    found_threads = []
    for t in threads:

        logging.info("Thread: %s", t)
        for origin in t["concept_origins"]:
            logging.info("Origin: %s", origin)

            if str(origin["originable_id"]) == str(user.id) and str(origin["originable_type"]) == str("DiscordUser"):
                logging.info("Found thread %s", t)
                found_threads.append(t)
                break

    # sort found_threads by created_at, grab the latest one
    if len(found_threads) > 0:
        found_threads.sort(key=lambda x: x["created_at"], reverse=True)
        thread = found_threads[0]

        # Convert the datetime object to a Unix timestamp required by openai
        # Parse the string to a datetime object from guru/rails
        dt = datetime.strptime(
            t["created_at"], '%Y-%m-%dT%H:%M:%S.%fZ')
        timestamp = int(time.mktime(dt.timetuple()))
        thread_data = {
            "id": thread["external_id"],
            "metadata": thread["metadata"],
            "created_at": timestamp,
            "object": "thread"
        }
        logging.info("Thread Data: %s", thread_data)
        thread = OpenAIThreadBase(**thread_data)

    return thread

# START: =========== AI Related Functions


def generate_user_agent(name, llm_config=None, code_execution=False):
    if code_execution:
        agent = UserAgent(
            name=name,
            system_message="You take code other assistants or agents and execute it.",
            max_consecutive_auto_reply=1,
            human_input_mode="NEVER",
            llm_config=llm_config,
            is_termination_msg=lambda msg: "TERMINATE" in msg["content"],
            code_execution_config={
                "work_dir": "agent_workspace",
                "use_docker": True,
            }
        )
    else:
        agent = UserAgent(
            name=name,
            system_message="You are the user.",
            max_consecutive_auto_reply=0,
            human_input_mode="NEVER",
            llm_config=llm_config,
            is_termination_msg=lambda msg: "TERMINATE" in msg["content"],
        )
    return agent


def generate_teachable_agent(name):
    agent = EnhancedTeachableAgent(
        name=name,
        llm_config=LLM_CONFIG,
        instructions=DEFAULT_SYSTEM_MESSAGE,
    )
    return agent


# END: =========== AI Related Functions


# create concept origin assosication
@trigger_to_topic('concept_origin')
def associate_concept_origin(concept_class: str, origin_class: str, conceptable_id: int, originable_id: int):
    data = {}
    data["conceptable_class"] = concept_class
    data["originable_class"] = origin_class
    data["conceptable_id"] = conceptable_id
    data["originable_id"] = originable_id
    return data


MAX_MESSAGES = 30
USER_MESSAGE_COUNT = {}

@DISCORD_BOT.event
async def on_message(message):
    # Record the message
    DISCORD_BOT.dispatch("handle_message", message)
    NEW_THREAD = False

    # Stop cyclic messages
    if message.author == DISCORD_BOT.user:
        return

    # Deal with ! commands
    if message.content.startswith("!newthread") and isinstance(message.channel, discord.DMChannel):
        logging.info("!newthread command received, setting NEW_THREAD to True")
        NEW_THREAD = True
    elif message.content.startswith("!"):
        logging.info("Received a command, processing it")
        await DISCORD_BOT.process_commands(message)
        return

    if isinstance(message.channel, discord.DMChannel):
        logging.info("Received a DM from %s", message.author)
        logging.info("Creating agent for %s", message.author)

        USER_MESSAGE_COUNT[message.author.id] = USER_MESSAGE_COUNT.get(
            message.author.id, 0) + 1
        if USER_MESSAGE_COUNT[message.author.id] < MAX_MESSAGES:
            logging.info("Max messages not reached, using existing thread.")
            thread = find_open_ai_thread(message.author)
        else:
            text = f"Max messages reached ({MAX_MESSAGES}). We must create a new thread for money purposes. Please use !newthread to continue. We will improve this moving forward."
            await message.channel.send(text)
            return

        if NEW_THREAD is True:
            logging.info("NEW_THREAD is True, this should create new thread")
            thread = None
            await message.channel.send("Creating a new thread for you.")

        manager, groupchat, user_agent, user_execution_agent, teachable_agent = find_or_create_agents(
            message.author)

        if thread is not None:
            logging.info("Found thread for %s", message.author)
            teachable_agent._openai_threads[manager] = thread
        else:
            logging.info("No thread found for %s", message.author)

        # sending typing notification
        await message.channel.trigger_typing()
        user_agent.initiate_chat(
            manager, message=message.content, clear_history=False)
        last_message = manager.last_message(user_agent)

        # ensure we can pickup the thread on next on_message invocation
        # the teachable will have a thread back to the manager, so we grab that as the concept origin
        associate_concept_origin(concept_class="OpenAiThread", origin_class="DiscordUser",
                                 conceptable_id=teachable_agent._openai_threads[manager].id, originable_id=message.author.id)

        await send_message_in_paragraphs(message, last_message["content"])

# ========== USER/MEMBER EVENTS ==========

@DISCORD_BOT.event
async def on_handle_user(user):
    logging.info("Processing user: %s", user)
    user_data = {
        "discord_id": user.id,
        "name": user.name,
        "discriminator": user.discriminator,
        "avatar": str(user.avatar),
        "bot": user.bot,
        "system": user.system if hasattr(user, 'system') else False
    }

    response = get_user(user.id)

    if response is None:
        logging.info("No user found, creating a user")
        create_user(user_data)
        logging.info("Created user")
    else:
        logging.info("Found user, updating it")
        update_user(user.id, user_data)
        logging.info("Updated user")

@DISCORD_BOT.event
async def on_member_join(member):
    logging.info("Member %s joined", member)
    DISCORD_BOT.dispatch("handle_user", member)

DISCORD_BOT.run(BOT_TOKEN)