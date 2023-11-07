import discord
from discord.ext import commands

BOT_TOKEN = 'MTE1MTIwMjE4NzUxMTM0OTMzOQ.GtM45p.DV_4RQ8HIQMA73v2iamLaGuWHc6eoY3_nQzNxU'

intents = discord.Intents.default()
intents.messages = True  # This is for listening to messages
intents.guilds = True  # This is necessary for guild-specific information
intents.message_content = True  # Necessary to read the content of the messages


bot = commands.Bot(command_prefix='!', intents=intents)

class View(discord.ui.View): # Create a class called View that subclasses discord.ui.View
    def __init__(self,error):
        super().__init__(timeout=60)
        self.error = error


    @discord.ui.button(label="Send crash report", style=discord.ButtonStyle.primary) # Create a button with the label "😎 Click me!" with color Blurple
    async def button_callback(self, button, interaction):
        await bot.get_channel(919272053310386236).send(self.error)
        await interaction.response.send_message("Crash report sent!") # Send a message when the button is clicked
        await self.stop()

@bot.command(description="Start Recording the Voice Channel")
async def vstart(ctx):
    await ctx.author.voice.channel.connect() # Connect to the voice channel of the author
    ctx.guild.voice_client.start_recording(discord.sinks.MP3Sink(), finished_callback, ctx) # Start the recording
    await ctx.send("I am listening...")

async def finished_callback(sink, ctx):
    # Here you can access the recorded files:
    recorded_users = [
        f"<@{user_id}>"
        for user_id, audio in sink.audio_data.items()
    ]
    embed = discord.Embed(title="Callback finished!",description=f'I have successfully recorded the Audio of {"and ".join(recorded_users)}')
    files = [discord.File(audio.file, f"{user_id}.{sink.encoding}") for user_id, audio in sink.audio_data.items()]
    await ctx.channel.send(embed=embed, files=files)

@bot.event
async def on_error(ctx,error):
    embed = discord.Embed(title="Yikes, that failed!",description=f'<:outage:937070871317741658> While running `{ctx.command.name}`, I encountered an error')
    embed.color = 0xFF0000
    embed.add_field(name="Error",value=error)
    embed.add_field(name="Details",value=f"```py\n{error.with_traceback(None)}```")
    view = View(error)
    await ctx.send(embed=embed,view=view)
    await view.wait()

@bot.command(description="Stop Recording the Voice Channel")
async def vstop(ctx):
    ctx.guild.voice_client.stop_recording() # Stop the recording, finished_callback will shortly after be called
    await ctx.send("Stopped!")


bot.run(BOT_TOKEN)