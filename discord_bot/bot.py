import os
import io
import re
import discord
from dotenv import load_dotenv

__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

from discord.ext import commands
from langchain.agents import load_tools
from langchain.tools import Tool, ElevenLabsText2SpeechTool
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
    'ddg-search', 'requests_all', 'terminal', 'arxiv', 'wikipedia', 'sleep'
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
    "functions": FUNCTIONS_CONFIG
}
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
    code_execution_config={ "work_dir": "agent_workplace" },
    max_consecutive_auto_reply=10,
    human_input_mode="NEVER"
)

COMMAND_EXECUTION_AGENT = UserAgent(
    name="CommandExecutionAgent",
    code_execution_config={ "work_dir": "agent_workplace" },
    max_consecutive_auto_reply=100,
    human_input_mode="NEVER",
)

USER_AGENT = UserAgent(
    name="User",
    max_consecutive_auto_reply=0,
    human_input_mode="NEVER",
)

MESSAGES = []
AGENTS = []
AGENTS.append(USER_AGENT)
AGENTS.append(COMMAND_EXECUTION_AGENT)
AGENTS.append(TEACHABLE_AGENT)
GROUP_CHAT = GroupChatExpanded(agents=AGENTS, messages=MESSAGES, max_round=50)
GROUP_MANAGER = GroupChatManagerExpanded(groupchat=GROUP_CHAT, llm_config=LLM_CONFIG)
MEMBERS = []

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

USER_AGENT.register_function(
    function_map=FUNCTIONS_MAP
)

def add_function(name, description, func):
    FUNCTIONS_MAP[name] = func
    tool = Tool(name=name, description=description, func=func)
    FUNCTIONS_CONFIG.append(generate_llm_config(tool))

# =========== COMMANDS

@DISCORD_BOT.command(description="Join Voice")
async def join(ctx):
    await ctx.author.voice.channel.connect()
    logging.info("Joined %s channel", ctx.author.voice.channel.name)

@DISCORD_BOT.command(description="Leave Voice")
async def leave(ctx):
    for x in DISCORD_BOT.voice_clients:
        await x.disconnect()
        logging.info("Left %s channel", ctx.author.voice.channel.name)
        return

@DISCORD_BOT.command(description="Learn from the conversation")
async def learn(ctx):
    DISCORD_BOT.dispatch("learn", ctx)

@DISCORD_BOT.command(description="Join and Start Recording")
async def start(ctx):
    DISCORD_BOT.dispatch("join_channel", ctx)
    io.sleep(1)
    DISCORD_BOT.dispatch("start_recording", ctx)

@DISCORD_BOT.command(description="Start Recording ")
async def record(ctx):
    DISCORD_BOT.dispatch("start_recording", ctx)

@DISCORD_BOT.command(description="Stop Recording the Voice Channel")
async def stop(ctx):
    DISCORD_BOT.dispatch("stop_recording", ctx)

@DISCORD_BOT.command(description="Ask Question to Agent and expect a voice")
async def ask(ctx):
    await deal_with_message(ctx, ctx.message.content[6:])


# =========== EVENTS

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
    logging.info("Learned from the conversation")

@DISCORD_BOT.event
async def on_speak(ctx, audio_file_path: str):
    await play_audio_to_voice_channel(ctx, audio_file_path)

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

async def deal_with_message(ctx, message):
    timestamp = ctx.message.created_at.strftime("%Y-%m-%d-%H-%M-%S")
    message = f"{timestamp}: {message}"
    await USER_AGENT.a_initiate_chat(GROUP_MANAGER, message=message, clear_history=True)
    last_message = GROUP_MANAGER.last_message(USER_AGENT)
    # if last message is a function call, ignore it
    if last_message is None:
        logging.info("No reply from")
        return

    # check if this reply contains a file
    file_path = extract_file_path(last_message["content"])
    if file_path is not None:
        logging.info("Found file path %s in reply", file_path)
        await play_audio_to_voice_channel(ctx, file_path)

    # If the message is pure text, we can use ElevenLabsText2SpeechTool to convert it to speech
    # Then we can play the audio in the voice channel
    if last_message["content"]:
        logging.info("Found text %s in reply", last_message["content"])
        tts = ElevenLabsText2SpeechTool()
        file_path = tts.run(last_message["content"])
        await play_audio_to_voice_channel(ctx, file_path)
    return

# Primary talking loop
async def play_audio_to_voice_channel(ctx, file_path):
    for x in DISCORD_BOT.voice_clients:
        if x == ctx.guild.voice_client:
            vc = x
    if not vc or not vc.is_connected():
        return
    # audio_file can be a wav, mp3 etc
    try:
        vc.play(discord.FFmpegOpusAudio(source=file_path))
    except:
        await play_audio_to_voice_channel(ctx, file_path)


# async def merged_finished_callback(sink: MP3Sink, channel: discord.TextChannel):
#     mention_strs = []
#     audio_segs: list[pydub.AudioSegment] = []
#     files: list[discord.File] = []
#     longest = pydub.AudioSegment.empty()

#     for user_id, audio in sink.audio_data.items():
#         mention_strs.append(f"<@{user_id}>")
#         seg = pydub.AudioSegment.from_file(audio.file, format="mp3")
#         # Determine the longest audio segment
#         if len(seg) > len(longest):
#             audio_segs.append(longest)
#             longest = seg
#         else:
#             audio_segs.append(seg)
#         audio.file.seek(0)
#         files.append(discord.File(audio.file, filename=f"{user_id}.mp3"))
#     for seg in audio_segs:
#         longest = longest.overlay(seg)
#     with io.BytesIO() as f:
#         longest.export(f, format="mp3")
#         await channel.send(
#             f"Finished! Recorded audio for {', '.join(mention_strs)}.",
#             files=files + [discord.File(f, filename="recording.mp3")],
#         )

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

if __name__ == "__main__":
    DISCORD_BOT.run(BOT_TOKEN)