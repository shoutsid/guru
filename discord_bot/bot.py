"""
TODO: Add nice discord responses (pages?)
TODO: Send back the audio to the channel along with the text, so that the user can hear the response when not in VC.
TODO: Record stream to text stream, to a_initiate_chat stream, get response and stream text to voice, and then stream that to the voice channel.
"""
import os
import re
import discord
import pyaudio
import wave
import time
from dotenv import load_dotenv

__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import chromadb
from discord.ext import commands, tasks
from langchain.agents import load_tools
from langchain.tools import Tool, ElevenLabsText2SpeechTool
from langchain.vectorstores import Chroma
from autogen import Agent

from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from townhall.agents.teachable_agent import TeachableAgent
from townhall.agents.user_agent import UserAgent
from townhall.managers.group_chat_manager import GroupChatManagerExpanded
from townhall.groups.group_chat import GroupChatExpanded
from discord_bot.utils import INTENTS, logging, load_logger, DEFAULT_SYSTEM_MESSAGE
from discord_bot.audio_to_text import AudioToText
from settings import CONFIG_LIST

load_logger()
load_dotenv()

# Can we create regular db tables in chroma?
# CONVO_DB_CONNECTION.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, content TEXT, author TEXT, channel TEXT, timestamp TEXT)")
CONVO_DB_CONNECTION = chromadb.PersistentClient(path="./.tmp/ai_db/conversations.db")
CONVO_COLLECTION = CONVO_DB_CONNECTION.get_or_create_collection("test_collection")
# Delete a collection and all associated embeddings, documents, and metadata.
# ⚠️ This is destructive and not reversible
# CONVO_DB_CONNECTION.delete_collection(name="test_collection")


DISCORD_BOT = commands.Bot(command_prefix='!', intents=INTENTS)

def extract_file_path(text):
    if text is not str:
        return None
    # Define the pattern to extract the path within markdown links
    pattern = r'\[.*?\]\((sandbox:.*?)\)'
    # Search the text for the pattern and extract the file path
    match = re.search(pattern, text)
    if match:
        # Return the file path if found without the sandbox: prefix
        return match.group(1).replace("sandbox:", "")
    else:
        # Return None if the pattern is not found
        return None

from langchain.tools import WikipediaQueryRun
from langchain.utilities import WikipediaAPIWrapper
def wikipedia(query):
    wikipedia_api_wrapper = WikipediaAPIWrapper()
    wikipedia_query_run = WikipediaQueryRun(wikipedia_api_wrapper=wikipedia_api_wrapper)
    return wikipedia_query_run.run(query=query)

BOT_TOKEN = os.getenv("DISCORD_TOKEN")
FUNCTIONS_MAP = {}
FUNCTIONS_CONFIG = []
TOOL_NAMES = [
    # 'ddg-search', 'requests_all', 'terminal', 'arxiv', 'wikipedia', 'sleep'
]
TOOLS = load_tools(TOOL_NAMES)
# TOOLS += [Tool.from_function(
#     func=on_speak,
#     name="speak_in_discord",
#     description="useful for when you need to speak and communicate with users in discord."
# )]
LLM_CONFIG = {
    "request_timeout": 180,
    "config_list": CONFIG_LIST,
    "use_cache": True,  # Use False to explore LLM non-determinism.
    "retry_wait_time": 0.5,
    "max_retry_period": 360,
}
if TOOL_NAMES.__len__() > 0:
    LLM_CONFIG["functions"] = FUNCTIONS_CONFIG

TEACH_CONFIG={
    "verbosity": 3,  # 0 for basic info, 1 to add memory operations, 2 for analyzer messages, 3 for memo lists.
    "reset_db": False,  # Set to True to start over with an empty database.
    "path_to_db_dir": "./.cache/ai_db",  # Path to the directory where the database will be stored.
    "recall_threshold": 1.5,  # Higher numbers allow more (but less relevant) memos to be recalled.
}
TEACHABLE_AGENT = TeachableAgent(
    name="Assistant",
    llm_config=LLM_CONFIG,
    teach_config=TEACH_CONFIG,
    system_message=DEFAULT_SYSTEM_MESSAGE,
    human_input_mode="NEVER"
)

COLLECTION_QUERY_SYSTEM_MESSAGE = """
You are an AI language model trained by OpenAI. Your task is to generate a single, accurate user prompt for searching the message collection, representing all the messages made in this Discord channel.

To generate the query, use the following code snippet as a reference:

collection.query(
    query_texts=["<user prompt>"],
)

Replace <user prompt> with a specific user prompt from the previous conversation that you want to use as the query. Choose a user prompt that accurately captures the context and intent of the search you wish to perform.

Only provide the generated user prompt as the response text, without any clarifications or additional explanations.

Please provide the specific user prompt you want to use as the query.
"""
COLLECTION_QUERY_AGENT = TeachableAgent(
    name="Collection Query Agent",
    llm_config=LLM_CONFIG,
    teach_config=TEACH_CONFIG,
    system_message=DEFAULT_SYSTEM_MESSAGE,
    human_input_mode="NEVER"
)

USER_AGENT = UserAgent(
    name="User",
    max_consecutive_auto_reply=0,
    human_input_mode="NEVER",
)

MESSAGES = []
AGENTS = []
AGENTS.append(USER_AGENT)
# AGENTS.append(COMMAND_EXECUTION_AGENT)
AGENTS.append(TEACHABLE_AGENT)
# GROUP_CHAT = GroupChatExpanded(agents=AGENTS, messages=MESSAGES, max_round=50)
# GROUP_MANAGER = GroupChatManagerExpanded(groupchat=GROUP_CHAT, llm_config=LLM_CONFIG)
MEMBERS = []
CHANNELS = []
CHANNEL_MESSAGES = {}
OAI_CHANNEL_MESSAGES = {}
CONNECTIONS = {}


global IN_VC
IN_VC = False

# START: =========== API Related Functions
def generate_user_agent(name):
    agent = UserAgent(
        name=name,
        max_consecutive_auto_reply=0,
        human_input_mode="NEVER",
    )
    add_agent(agent)
    return agent


def generate_teachable_agent(name):
    agent = TeachableAgent(
        name=name,
        llm_config=LLM_CONFIG,
        teach_config=TEACH_CONFIG,
        system_message=DEFAULT_SYSTEM_MESSAGE,
        human_input_mode="NEVER"
    )
    add_agent(agent)
    return agent
# END: =========== API Related Functions

def find_agent(discord_username: str):
    for agent in AGENTS:
        if agent.name == discord_username:
            return agent
    return None

def add_agent(agent: Agent):
    AGENTS.append(agent)

def generate_llm_config(tool):
    """
    Generate a function schema for a LangChain tool.
    """
    function_schema = {
        "name": tool.name.lower().replace (' ', '_'),
        "description": tool.description,
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    }

    if tool.args is not None:
        function_schema["parameters"]["properties"] = tool.args

    return function_schema

for tool in TOOLS:
    # pylint: disable=protected-access
    FUNCTIONS_MAP[tool.name] = tool._run
    # pylint: enable=protected-access
    FUNCTIONS_CONFIG.append(generate_llm_config(tool))

if FUNCTIONS_MAP.__len__() > 0:
    USER_AGENT.register_function(
        function_map=FUNCTIONS_MAP
    )

def add_function(name, description, func):
    FUNCTIONS_MAP[name] = func
    tool = Tool(name=name, description=description, func=func)
    FUNCTIONS_CONFIG.append(generate_llm_config(tool))

# =========== COMMANDS

@DISCORD_BOT.command(description="use query to search the message collection")
async def query(ctx, query_text):
    # Use the collection query agent to generate a query for the message collection.
    await USER_AGENT.a_initiate_chat(COLLECTION_QUERY_AGENT, message=query_text, clear_history=False)
    refined_query = USER_AGENT.last_message(COLLECTION_QUERY_AGENT)
    results = CONVO_COLLECTION.query(
        query_texts=[str(refined_query)],

    )
    await ctx.send(f"Here are the results for your query: {results}")

@DISCORD_BOT.command(description="Status Check")
async def status(ctx):
    msg = "I am online and ready to go!"
    msg += f"\nIN_VC: {IN_VC}"
    if any(CONNECTIONS):
        msg += "\nI am currently connected to the following channels:"
        for channel in CONNECTIONS:
            msg += f"\n{channel}"
    await ctx.send(msg)

@DISCORD_BOT.command(description="Join Voice")
async def join(ctx):
    global IN_VC, CONNECTIONS
    vc = await ctx.author.voice.channel.connect()
    CONNECTIONS.update({ctx.guild.id: vc})
    IN_VC = True
    logging.info("Joined %s channel", ctx.author.voice.channel.name)

@DISCORD_BOT.command(description="Leave Voice")
async def leave(ctx):
    global IN_VC, CONNECTIONS

    if ctx.guild.id in CONNECTIONS:
        vc = CONNECTIONS[ctx.guild.id]
        if vc.is_playing():
            vc.stop()
        try:
            vc.stop_recording()
        except:
            pass

        del CONNECTIONS[ctx.guild.id]
        await vc.disconnect()
        IN_VC = False
        logging.info("Left %s channel", ctx.author.voice.channel.name)

@DISCORD_BOT.command(description="Learn from the conversation")
async def learn(ctx):
    DISCORD_BOT.dispatch("learn", ctx)

@DISCORD_BOT.command(description="Join and Start Recording")
async def start(ctx):
    DISCORD_BOT.dispatch("join_channel", ctx)
    time.sleep(1)
    DISCORD_BOT.dispatch("start_recording", ctx)

@DISCORD_BOT.command(description="Start Recording ")
async def record(ctx):
    DISCORD_BOT.dispatch("start_recording", ctx)

@DISCORD_BOT.command(description="Stop Recording the Voice Channel")
async def stop(ctx):
    DISCORD_BOT.dispatch("stop_recording", ctx)

@DISCORD_BOT.command(description="Ask Question to Agent and expect a voice")
async def ask(ctx):
    message = ctx.message.content[5:]
    # Create an embed object
    embed = discord.Embed(
        title="Guru",
        description="I am a Guru, ask me anything.",
        color=discord.Color.blurple()
    )
    embed.add_field(name="Question", value=message, inline=True)
    embed_message = await ctx.send(embed=embed)
    await deal_with_message(ctx=ctx, message=message, embed=embed, embed_message=embed_message)

@DISCORD_BOT.command(description="Ask Question to Agent and expect a voice")
async def play_audio(ctx, file_path):
    if not ctx.message.author.voice:
        await ctx.send("You are not connected to a voice channel.")
        return

    # connect to the voice channel
    channel = ctx.message.author.voice.channel
    if not channel:
        await ctx.send("Error finding a voice channel.")
        return

    if ctx.voice_client is None:
        await channel.connect()

    DISCORD_BOT.dispatch("speak", ctx, file_path)

@DISCORD_BOT.command(description="Send all the member names of the server")
async def print_members_to_console(ctx):
    for member in MEMBERS:
        print(member)

@DISCORD_BOT.command(description="Send all channel names of the server")
async def print_channels_to_console(ctx):
    for channel in ctx.guild.channels:
        print(channel)

@DISCORD_BOT.command(description="Send all the channel messages of the server")
async def print_channel_messages_to_console(ctx):
    for channel in CHANNEL_MESSAGES:
        print(channel, CHANNEL_MESSAGES[channel])

@DISCORD_BOT.command(description="Reset the agents current conversation")
async def reset(ctx):
    TEACHABLE_AGENT.reset()
    USER_AGENT.reset()
    await ctx.send("Reset the agents current conversation.")


# =========== EVENTS

@DISCORD_BOT.event
async def on_update_channel_messages(channel):
    try:
        async for message in channel.history():
            DISCORD_BOT.dispatch("message_update", message)
    except:
        logging.debug("No permissions to channel %s", channel)

@DISCORD_BOT.event
async def on_message(message):
    DISCORD_BOT.dispatch("message_update", message)
    await DISCORD_BOT.process_commands(message)

@DISCORD_BOT.event
async def on_message_update(message):
    if CHANNEL_MESSAGES.get(message.channel) is None:
        CHANNEL_MESSAGES[message.channel] = []

    if message in CHANNEL_MESSAGES[message.channel]:
        logging.debug("Updating message %s in channel %s", message, message.channel)
        CHANNEL_MESSAGES[message.channel][CHANNEL_MESSAGES[message.channel].index(message)] = message
    else:
        logging.debug("Adding message %s to channel %s", message, message.channel)
        CHANNEL_MESSAGES[message.channel].append(message)

    if message.author != DISCORD_BOT.user:
        role = "user"
    else:
        role = "assistant"
    # capitalize the first letter of the role
    header_role = role[0].upper() + role[1:]

    # translate the message, to openai compatability
    header = f"**{header_role}: {message.author.name}**"
    timestamp = message.created_at.strftime('%Y-%m-%d-%H-%M-%S')
    content = message.content
    footer = f"**Timestamp: {timestamp}**"
    all =  f"{header}\n{content}\n{footer}"
    oai_message = {
        "content": all,
        "role": role,
    }

    # Add/Update the message to the vector database
    CONVO_COLLECTION.upsert(
        ids=[str(message.id)],
        documents=[message.content],
        metadatas=[{
            "author": message.author.name,
            "channel": message.channel.name,
            "timestamp": timestamp,
        }]
    )
    # if message is in channel, we need to update it otherwise we add it
    if OAI_CHANNEL_MESSAGES.get(message.channel) is None:
        OAI_CHANNEL_MESSAGES[message.channel] = []
    if oai_message in OAI_CHANNEL_MESSAGES[message.channel]:
        logging.debug("Updating message %s in channel %s", oai_message, message.channel)
        OAI_CHANNEL_MESSAGES[message.channel][OAI_CHANNEL_MESSAGES[message.channel].index(oai_message)] = oai_message
    else:
        logging.debug("Adding message %s to channel %s", oai_message, message.channel)
        OAI_CHANNEL_MESSAGES[message.channel].append(oai_message)

@DISCORD_BOT.event
async def on_member_join(member):
    logging.info("Member %s joined", member)
    MEMBERS.append(member)

@DISCORD_BOT.event
async def on_stop_recording(ctx):
    ctx.guild.voice_client.stop_recording()
    logging.info("Stopped recording in %s channel", ctx.author.voice.channel.name)

@DISCORD_BOT.event
async def on_start_recording(ctx):
    ctx.guild.voice_client.start_recording(discord.sinks.MP3Sink(), finished_callback, ctx)
    logging.info("Started recording in %s channel", ctx.author.voice.channel.name)

@DISCORD_BOT.event
async def on_join_channel(ctx):
    await ctx.author.voice.channel.connect()
    logging.info("Joined %s channel", ctx.author.voice.channel.name)

@DISCORD_BOT.event
async def on_learn(ctx):
    TEACHABLE_AGENT.learn_from_user_feedback()
    await ctx.send("Learned from the conversation, this does not mean I remember everything!")
    logging.info("Learned from the conversation")

@DISCORD_BOT.event
async def on_speak(ctx, audio_file_path: str):
    await play_audio_to_voice_channel(ctx, file_path=audio_file_path)

@DISCORD_BOT.event
async def on_update_channel(channel):
    logging.info("Updating channel %s", channel)
    if channel not in CHANNELS:
        print("Adding channel", channel)
        CHANNELS.append(channel)

    if isinstance(channel, discord.TextChannel):
        DISCORD_BOT.dispatch("update_channel_messages", channel)

# ======= COGS & LOOPS =======

@tasks.loop(seconds=10.0)
async def heartbeat():
    CONVO_DB_CONNECTION.heartbeat()

@tasks.loop(seconds=5.0, count=1)
async def start_task():
    global MEMBERS
    await DISCORD_BOT.wait_until_ready()
    print("Primary Loop, %s members" % len(MEMBERS))
    # Check and update members list
    for member in DISCORD_BOT.get_all_members():
        if member not in MEMBERS:
            print("Adding member", member)
            MEMBERS.append(member)

    for channel in DISCORD_BOT.get_all_channels():
        DISCORD_BOT.dispatch("update_channel", channel)

# TODO: Check if the bot is in a voice channel
# Constantly listen for activation words
# if activation words are found, start recording

# ======= HELPERS =======

async def process_audio(ctx, sink, audio, files, timestamp, user_id):
    logging.info("Processing audio of %s", user_id)
    # create folders
    folder = os.path.join(os.getcwd(), "recordings")
    if not os.path.exists(folder):
        os.mkdir(folder)
    folder = os.path.join(folder, f"{timestamp}")
    if not os.path.exists(folder):
        os.mkdir(folder)

    discord_file = discord.File(audio.file, f"{folder}/{user_id}.{sink.encoding}")
    files.append(discord_file)
    # save audio to file
    audio_filename = f"{folder}/{user_id}.{sink.encoding}"
    with open(audio_filename, "wb") as f:
        f.write(audio.file.read())
        f.close()
    logging.info("Saved audio of %s to %s", user_id, audio_filename)
    audio_to_text = AudioToText(audio_filename, f"{folder}/{user_id}.txt")
    transcription = audio_to_text.transcribe()
    logging.info("Transcribed audio of %s to %s", user_id, transcription)

    logging.info("Initiating chat with the agents")
    await deal_with_message(ctx, transcription)

async def deal_with_message(ctx, message, embed=discord.Embed(), embed_message=None):
    timestamp = ctx.message.created_at.strftime("%Y-%m-%d-%H-%M-%S")
    message = f"{timestamp}: {message}"

    # TODO: Add env variable to reset the agents
    # reset the agents convos etc
    # TEACHABLE_AGENT.reset()
    # USER_AGENT.reset()

    await USER_AGENT.a_initiate_chat(TEACHABLE_AGENT, message=message, clear_history=False)
    last_message = TEACHABLE_AGENT.last_message(USER_AGENT)
    # if last message is a function call, ignore it
    if last_message is None:
        logging.info("No reply from")
        return

    # check if this reply contains a file
    file_path = extract_file_path(last_message["content"])
    if file_path is not None:
        logging.info("Found file path %s in reply", file_path)

        if embed_message is not None:
            embed.add_field(name=f"Reply", value=last_message["content"], inline=False)
            embed_message.edit(embed=embed)

        if IN_VC:
            file = discord.File(file_path)
            embed.add_field(name="Audio File", value=file_path, inline=True)
            await embed_message.edit(embed=embed, file=file)
            await play_audio_to_voice_channel(ctx, file_path=file_path)
        return

    # TODO: Put this through processing agent which will convert the text
    # into human-like text which can be spoken well. Also
    # This will chunk correctly, without major cutoffs.
    #
    # Current Functionality:
    # send text back to channel
    # must not be more than 1024 characters - character restrictions on discord + tts
    # if so split up into multiple messages

    if len(last_message["content"]) > 1024:
        logging.info("Found text %s in reply", last_message["content"])
        for i in range(0, len(last_message["content"]), 1024):
            msg = last_message["content"][i:i+1024]
            if embed_message is not None:
                embed.add_field(name=f"Reply pt.{i}", value=msg, inline=False)
                await embed_message.edit(embed=embed)

        for i in range(0, len(last_message["content"]), 1024):
            msg = last_message["content"][i:i+1024]
            if IN_VC:
                await do_tts(ctx, msg, embed=embed, embed_message=embed_message)
        return

    if embed_message is not None:
        embed.add_field(name="Reply", value=last_message["content"], inline=False)
        await embed_message.edit(embed=embed)

    if IN_VC:
        await do_tts(ctx, text=last_message["content"], embed=embed, embed_message=embed_message)
    return

async def do_tts(ctx, text, embed=discord.Embed(), embed_message=None):
    # If the message is pure text, we can use ElevenLabsText2SpeechTool to convert it to speech
    # Then we can play the audio in the voice channel
    logging.debug("Converting text to speech")
    tts = ElevenLabsText2SpeechTool()
    file_path = tts.run(text)
    time.sleep(5) # allow for the file to be created
    file = discord.File(file_path)
    embed.add_field(name="Audio File", value=file_path, inline=True)
    await embed_message.edit(embed=embed, file=file)
    await play_audio_to_voice_channel(ctx, file_path=file_path)

# Primary talking loop
async def play_audio_to_voice_channel(ctx, file_path):
    if not ctx.message.author.voice:
        await ctx.send("You are not connected to a voice channel.")
        return

    channel = ctx.message.author.voice.channel

    if not channel:
        await ctx.send("Error finding a voice channel.")
        return

    if ctx.voice_client is None:
        voice_client = await channel.connect()
        ctx.voice_client = voice_client
    else:
        voice_client = ctx.voice_client

    audio_source = discord.FFmpegOpusAudio(source=file_path)
    if not voice_client.is_playing():
        voice_client.play(audio_source)

async def finished_callback(sink, ctx):
    recorded_users = [
        f"<@{user_id}>"
        for user_id, audio in sink.audio_data.items()
    ]
    logging.info("Callback started! I have successfully recorded the Audio of %s", 'and '.join(recorded_users))
    files = []
    timestamp = ctx.message.created_at.strftime("%Y-%m-%d-%H-%M-%S")
    for user_id, audio in sink.audio_data.items():
        await process_audio(ctx, sink, audio, files, timestamp, user_id)
    logging.info("Finished recording in %s channel", ctx.author.voice.channel.name)

# CHUNK = 1024
# FORMAT = pyaudio.paInt16
# AUDIO_CHANNELS = 2
# RATE = 44100
# RECORD_SECONDS = 10  # Adjust the recording duration as needed
# FILENAME = "recorded_audio.wav"  # Output file name

# def save_audio(frames):
#     p = pyaudio.PyAudio()
#     wf = wave.open(FILENAME, 'wb')
#     wf.setnchannels(AUDIO_CHANNELS)
#     wf.setsampwidth(p.get_sample_size(FORMAT))
#     wf.setframerate(RATE)
#     wf.writeframes(b''.join(frames))
#     wf.close()

# @DISCORD_BOT.command(description="Record audio from the voice channel")
# async def record_audio(ctx):
#     if ctx.voice_client is None:
#         await ctx.send("Not connected to a voice channel.")
#         return
#     audio_stream = ctx.voice_client.client._connection._get_voice_pipeline().listen(discord.AudioReceiveStream)
#     frames = []
#     for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
#         data = await audio_stream.read()
#         frames.append(data)
#     save_audio(frames)

if __name__ == "__main__":
    start_task.start()
    DISCORD_BOT.run(BOT_TOKEN)