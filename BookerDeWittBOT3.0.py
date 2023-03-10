import discord
from discord.ext import commands
import asyncio
import youtube_dl

# The bot's command prefix is '!', and it has all intents enabled
client = commands.Bot(command_prefix='!', intents=discord.Intents.all())

# This is a Discord bot that uses the commands extension from the discord.py library. It also uses asyncio, discord, and youtube_dl libraries.

#- !commands: Lists all of the available commands


# Create a queue for storing songs
song_queue = asyncio.Queue()

# Define a function for adding a song to the queue
async def add_song(song_url):
    try:
        song = discord.FFmpegPCMAudio(song_url)
    except Exception as e:
        return await ctx.send(f'An error occurred while trying to play the song: {e}')
    await song_queue.put(song)


@client.command()
async def skip_song(ctx):
    """
    Skip the current song and play the next song in the queue.

    If the bot is not currently playing any music, or if there are no more songs in the queue, this command does nothing.
    """
    voice_client = ctx.voice_client
    # Check if the bot is currently playing music
    if not voice_client.is_playing():
        return await ctx.send('The bot is not currently playing any music.')
    # Skip to the next song
    await skip_song(voice_client)

# Define a function for skipping to the next song
async def skip_song(voice_client):
    
    # Stop the current song
    voice_client.stop()
    # If there are more songs in the queue, play the next one
    if not song_queue.empty():
        song = song_queue.get()
        voice_client.play(song)

    
    # Stop the current song
    voice_client.stop()
    # If there are more songs in the queue, play the next one
    if not song_queue.empty():
        song = await song_queue.get()
        voice_client.play(song)

@client.command()
async def play_song(ctx, *, query: str):
    """
    Play a song by URL or search query.

    The song will be added to the queue, and if the bot is not currently playing music,
    it will start playing the first song in the queue.
    """
    # Get the voice channel that the user is in
    voice_channel = ctx.author.voice.channel
    if not voice_channel:
        return await ctx.send('You are not connected to a voice channel.')

    # Get the voice client for the voice channel
    voice_client = ctx.voice_client
    # If the bot is not already connected to the voice channel, connect to it
    if not voice_client:
        voice_client = await voice_channel.connect()

    # Search for the song on YouTube
    ydl_opts = {
        'default_search': 'ytsearch',
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }                   
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(query, download=False)
            if 'formats' not in info:
                return await ctx.send(f'No results found for query: {query}')
            song_url = info['formats'][0]['url']
        except youtube_dl.utils.ExtractorError:
            return await ctx.send(f'No results found for query: {query}')
        except Exception as e:
            return await ctx.send(f'An error occurred while trying to play the song: {e}')

    # Add the song to the queue
    await add_song(song_url)

    # If the bot is not currently playing a song, start playing the first song in the queue
    if not voice_client.is_playing():
        song = await song_queue.get()
        voice_client.play(song)

@client.command()
async def stop_song(ctx):
    """
    Stop the current song and clear the queue.

    If the bot is not currently playing any music, this command does nothing.
    """
    voice_client = ctx.voice_client
    # Check if the bot is currently playing music
    if not voice_client.is_playing():
        return await ctx.send('The bot is not currently playing any music.')
    # Stop the current song
    voice_client.stop()
    # Clear the queue
    while not song_queue.empty():
        song_queue.get_nowait()


@client.command()
async def tts(ctx, *, message: str):
    """
    Speak the provided message using text-to-speech.

    The message will be spoken in the voice channel that the user is currently connected to.
    """
    # Get the voice channel that the user is in
    voice_channel = ctx.author.voice.channel
    if not voice_channel:
        return await ctx.send('You are not connected to a voice channel.')

    # Get the voice client for the voice channel
    voice_client = ctx.voice_client
    # If the bot is not already connected to the voice channel, connect to it
    if not voice_client:
        try:
            voice_client = await voice_channel.connect()
        except Exception as e:
            return await ctx.send(f'An error occurred while trying to connect to the voice channel: {e}')

    # Speak the message using text-to-speech
    try:
        await ctx.send(message, tts=True)
    except Exception as e:
        return await ctx.send(f'An error occurred while trying to speak the message: {e}')

@client.command()
async def commands(ctx, command_name: str = None):
    """Show a list of all available commands or detailed help for a specific command."""
    try:
        if command_name:
            # Get the specified command
            command = client.get_command(command_name)
            if command:
                # Format the help text for the command
                message = '**Command:** `!{}`\n{}\n'.format(command.name, command.help)
                if command.aliases:
                    message += '**Aliases:** {}\n'.format(", ".join(command.aliases))
                await ctx.send(message)
            else:
                await ctx.send('Command `!{}` not found.'.format(command_name))
        else:
            # Get a list of all commands
            commands = []
            for command in client.commands:
                commands.append((command.name, command.help))

            # Format the list of commands into a message
            message = '**Available commands:**\n'
            for name, help_text in commands:
                message += '`!{}`: {}\n'.format(name, help_text)

            await ctx.send(message)
    except Exception as e:
        await ctx.send('An error occurred while trying to send the message: {}'.format(e))



# This code runs the Discord bot client with the specified token. The token is used to authenticate the bot with the Discord API.
# To run the bot, replace the token with your own bot token. You can get a bot token by creating a bot account @Discord Developer Portal.

client.run('BOT TOKEN HERE')

#Thousands of doors... opening all at once. My God! They are beautiful!
