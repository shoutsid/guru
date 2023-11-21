import logging
from discord_bot.audio_to_text import AudioToText

global IN_VC
IN_VC = False

# TODO: Check if the bot is in a voice channel
# Constantly listen for activation words
# if activation words are found, start recording


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


@DISCORD_BOT.command(description="Join Voice")
async def join(ctx):
    global IN_VC, CONNECTIONS
    vc = await ctx.author.voice.channel.connect()
    CONNECTIONS.update({ctx.guild.id: vc})
    IN_VC = True
    logging.info("Joined %s channel", ctx.author.voice.channel.name)


@DISCORD_BOT.command(description="Status Check")
async def status(ctx):
    msg = "I am online and ready to go!"
    msg += f"\nIN_VC: {IN_VC}"
    if any(CONNECTIONS):
        msg += "\nI am currently connected to the following channels:"
        for channel in CONNECTIONS:
            msg += f"\n{channel}"
    await ctx.send(msg)


# ========== VOICE EVENTS ==========


@DISCORD_BOT.event
async def on_stop_recording(ctx):
    ctx.guild.voice_client.stop_recording()
    logging.info("Stopped recording in %s channel",
                 ctx.author.voice.channel.name)


@DISCORD_BOT.event
async def on_start_recording(ctx):
    ctx.guild.voice_client.start_recording(
        discord.sinks.MP3Sink(), finished_callback, ctx)
    logging.info("Started recording in %s channel",
                 ctx.author.voice.channel.name)


# TODO: Think about renaming this method
@DISCORD_BOT.event
async def on_join_channel(ctx):
    await ctx.author.voice.channel.connect()
    logging.info("Joined %s channel", ctx.author.voice.channel.name)


@DISCORD_BOT.event
async def on_speak(ctx, audio_file_path: str):
    await play_audio_to_voice_channel(ctx, file_path=audio_file_path)


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

    discord_file = discord.File(
        audio.file, f"{folder}/{user_id}.{sink.encoding}")
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
            embed.add_field(
                name=f"Reply", value=last_message["content"], inline=False)
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
        embed.add_field(
            name="Reply", value=last_message["content"], inline=False)
        await embed_message.edit(embed=embed)

    if IN_VC:
        await do_tts(ctx, text=last_message["content"], embed=embed, embed_message=embed_message)
    return


async def do_tts(ctx, text, embed=discord.Embed(), embed_message=None):
    # If the message is pure text, we can use ElevenLabsText2SpeechTool to convert it to speech
    # Then we can play the audio in the voice channel
    logging.info("Converting text to speech")
    tts = ElevenLabsText2SpeechTool()
    file_path = tts.run(text)
    time.sleep(5)  # allow for the file to be created
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
    logging.info("Callback started! I have successfully recorded the Audio of %s",
                 'and '.join(recorded_users))
    files = []
    timestamp = ctx.message.created_at.strftime("%Y-%m-%d-%H-%M-%S")
    for user_id, audio in sink.audio_data.items():
        await process_audio(ctx, sink, audio, files, timestamp, user_id)
    logging.info("Finished recording in %s channel",
                 ctx.author.voice.channel.name)
