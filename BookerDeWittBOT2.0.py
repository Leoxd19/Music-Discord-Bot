
from discord.ext import commands
import asyncio
import discord
import youtube_dl

# The bot's command prefix is '!', and it has all intents enabled
client = commands.Bot(command_prefix='!', intents=discord.Intents.all())

# This is a Discord bot that uses the commands extension from the discord.py library. It also uses asyncio, discord, and youtube_dl libraries.

# To use the bot, add it to your Discord server and use the following commands:
#- !command1: Description of command 1.
#- !command2: Description of command 2.

# Create a queue for storing songs
song_queue = asyncio.Queue()

# Create a function for adding a song to the queue
async def add_song(song_url):
    try:
        song = discord.FFmpegPCMAudio(song_url)
    except Exception as e:
        return await ctx.send(f'An error occurred while trying to play the song: {e}')
    await song_queue.put(song)

# Create a function for skipping to the next song
async def skip_song():
    # Stop the current song
    voice_client.stop()
    # If there are more songs in the queue, play the next one
    if not song_queue.empty():
        song = await song_queue.get()
        voice_client.play(song)

@client.command()
async def play_song(ctx, *, query: str):
    """Play a song by URL or search query."""
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
    """Stop the current song and clear the queue."""
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
async def skip_song(ctx):
    """Skip the current song and play the next song in the queue."""
    voice_client = ctx.voice_client
    # Check if the bot is currently playing music
    if not voice_client.is_playing():
        return await ctx.send('The bot is not currently playing any music.')
    # Skip to the next song
    await skip_song()

# This code runs the Discord bot client with the specified token. The token is used to authenticate the bot with the Discord API

client.run('MTA1MzAxMTk5MjA5NDQ0MTQ5Mg.GQ3j8k.7g9gboOumOOj4pnt74Gcy41lGdwWIbPgVQa4nU')