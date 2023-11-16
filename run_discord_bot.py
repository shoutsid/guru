"""
TODO: Add nice discord responses (pages?)
TODO: Send back the audio to the channel along with the text, so that the user can hear the response when not in VC.
TODO: Record stream to text stream, to a_initiate_chat stream, get response and stream text to voice, and then stream that to the voice channel.
"""

from guru.api.threads_client import list_threads, create_thread
from guru.agents.user_agent import UserAgent
from guru.agents.enhanced_teachable_agent import EnhancedTeachableAgent
import os
import asyncio
import discord
import time
# from dotenv import load_dotenv

__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

from discord.ext import commands, tasks
from langchain.agents import load_tools
from langchain.tools import Tool, ElevenLabsText2SpeechTool
from autogen import Agent

from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from discord_bot.utils import INTENTS, logging, load_logger, DEFAULT_SYSTEM_MESSAGE, extract_file_path
from guru.db.agent import Agent as AgentModel
from discord_bot.audio_to_text import AudioToText
from settings import CONFIG_LIST

load_logger()

# Connection to existing Rails DB.
# TODO: switch all interactions with API calls to guru_api.
from sqlmodel import Session, create_engine, SQLModel, select
sqlite_file_name = "guru_api/storage/development.sqlite3"
sqlite_url = f"sqlite:///{sqlite_file_name}"
connect_args = {"check_same_thread": False}
SQL_ENGINE = create_engine(sqlite_url, echo=True, connect_args=connect_args)
SQL_DB_SESSION = Session(SQL_ENGINE)
SQLModel.metadata.create_all(SQL_ENGINE)

DISCORD_BOT = commands.Bot(command_prefix='!', intents=INTENTS)

BOT_TOKEN = os.getenv("DISCORD_TOKEN")

TOOL_NAMES = []
TOOLS = load_tools(TOOL_NAMES)
FUNCTIONS_MAP = {}
FUNCTIONS_CONFIG = []
# 'ddg-search', 'requests_all', 'terminal', 'arxiv', 'wikipedia', 'sleep'
LLM_CONFIG = {
    "request_timeout": 180,
    "config_list": CONFIG_LIST,
    "use_cache": True,  # Use False to explore LLM non-determinism.
    "retry_wait_time": 0.5,
    "max_retry_period": 360,
}
if TOOL_NAMES.__len__() > 0:
    LLM_CONFIG["functions"] = FUNCTIONS_CONFIG

# find or  a new agent row based on the discord username
# from sqlmodel import select
db_agent = SQL_DB_SESSION.exec(select(AgentModel).where(AgentModel.name == "DISCORD_BOT"))
db_agent = db_agent.one_or_none()
if db_agent is None:
    db_agent = AgentModel(name="DISCORD_BOT", system_message=DEFAULT_SYSTEM_MESSAGE)
    SQL_DB_SESSION.add(db_agent)
    SQL_DB_SESSION.commit()
    SQL_DB_SESSION.refresh(db_agent)

TEACHABLE_AGENT = EnhancedTeachableAgent(
    name="Assistant",
    llm_config=LLM_CONFIG,
    instructions=DEFAULT_SYSTEM_MESSAGE,
    db_agent_id=db_agent.id,
)
USER_AGENT = UserAgent(
    name="User",
    max_consecutive_auto_reply=0,
    human_input_mode="NEVER",
)

THREADS = []
MESSAGES = []
AGENTS = []
AGENTS.append(USER_AGENT)
AGENTS.append(TEACHABLE_AGENT)
MEMBERS = []
CHANNELS = []
CHANNEL_MESSAGES = {}
OAI_CHANNEL_MESSAGES = {}
CONNECTIONS = {}
# GROUP_CHAT = GroupChatExpanded(agents=AGENTS, messages=MESSAGES, max_round=50)
# GROUP_MANAGER = GroupChatManagerExpanded(groupchat=GROUP_CHAT, llm_config=LLM_CONFIG)
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

def generate_teachable_agent(name, db_id):
    agent = EnhancedTeachableAgent(
        name=name,
        llm_config=LLM_CONFIG,
        instructions=DEFAULT_SYSTEM_MESSAGE,
        db_agent_id=db_id,
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

@DISCORD_BOT.command(description="spit out tests")
async def test(ctx):
    # last 5
    for message in MESSAGES[-5:]:
        # print(message)
        msg = f"({message.get('role')}) said: \n {message.get('content')}"
        await ctx.send(msg)
    # for thread in THREADS:

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
    context = await DISCORD_BOT.get_context(message)
    context.message = message

    # Add Message from User to CHANNEL_MESSAGES
    DISCORD_BOT.dispatch("message_update", message)

    if isinstance(message.channel, discord.DMChannel) and message.author != DISCORD_BOT.user:
        logging.info("Received message %s in private channel", message)
        timestamp = context.message.created_at.strftime("%Y-%m-%d-%H-%M-%S")
        await USER_AGENT.a_initiate_chat(TEACHABLE_AGENT, message=f"{timestamp}: {message.content}", clear_history=False)
        last_message = TEACHABLE_AGENT.last_message(USER_AGENT)

        # if last message is a function call, ignore it
        if last_message is None:
            logging.info("No reply from")
            return

        if len(last_message["content"]) > 1024:
            logging.info("Found text %s in reply", last_message["content"])
            for i in range(0, len(last_message["content"]), 1024):
                msg = last_message["content"][i:i+1024]
                await message.channel.send(msg)
                return

        await message.channel.send(last_message["content"])
    else:
        await DISCORD_BOT.process_commands(message)

from guru.api.messages_client import create_message, list_messages
@DISCORD_BOT.event
async def on_message_update(message):
    if message.author != DISCORD_BOT.user:
        role = "user"
    else:
        role = "assistant"

    thread = None
    for t in THREADS:
        if t["discord_channel"] == message.channel.name:
            thread = t
            break

    if thread is None:
        logging.info("No thread found for channel %s", message.channel.name)
        return None


    if message.content == "" or message.content is None:
        # TODO: This is where we will disect the message type and not just rely on text only media
        logging.info("No message content found to create")
        return None

    oai_message = {
        "content": message.content,
        "role": role,
    }

    response = list_messages(thread["id"])
    try:
        if response["status"] is not 200:
            logging.error("Error occurred while listing message.")
            return None
    except:
        pass

    messages = response

    if len(messages) == 0:
        logging.info("No messages found")
        logging.info("Creating a message for thread")
        create_response = create_message(thread["id"], oai_message)
        logging.info("Created message")
        MESSAGES.append(create_response)
    else:
        logging.info("Found messages")
        matched_message = None
        for m in messages:
            if m["content"] == message.content:
                logging.info("Found message")
                MESSAGES.append(m)
                matched_message = m
                break
        if matched_message is None:
            logging.info("Creating a message for thread")
            create_response = create_message(thread["id"], oai_message)
            try:
                if create_response["status"] is not 200:
                    logging.error("Error occurred while creating message.")
                    return None
            except:
                pass

            logging.info("Created message")
            MESSAGES.append(create_response)


@DISCORD_BOT.event
async def on_update_channel(channel):
    channel_name = channel.name
    logging.info(f"Updating channel {channel_name}")

    if channel not in CHANNELS:
        logging.info(f"Adding channel {channel_name}")
        CHANNELS.append(channel)

    if isinstance(channel, (discord.TextChannel, discord.VoiceChannel)):
        for i in range(3):
            try:
                response = list_threads(discord=True, discord_channel=channel_name)

                if not response:
                    logging.info("No threads found")
                    logging.info("Creating a thread for channel")
                    thread_data = {
                        "discord_channel": channel_name,
                        "discord": True,
                    }
                    response = create_thread(thread_data)
                    logging.info("Created thread")
                    THREADS.append(response[0])

                else:
                    logging.info("Found threads")
                    for thread in response:
                        if thread["discord_channel"] == channel_name:
                            logging.info("Found thread")
                            THREADS.append(thread)
                            break
                break
            except Exception as e:
                logging.error(f"Error occurred while listing threads: {e}")
                await asyncio.sleep(5)

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
async def on_speak(ctx, audio_file_path: str):
    await play_audio_to_voice_channel(ctx, file_path=audio_file_path)

# ======= COGS & LOOPS =======

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
        try:
            async for message in channel.history():
                DISCORD_BOT.dispatch("message_update", message)
        except:
            pass

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

start_task.start()
DISCORD_BOT.run(BOT_TOKEN)