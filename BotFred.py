from discord.ext import commands
import asyncio
import discord
import youtube_dl


client = commands.Bot(command_prefix='!', intents=discord.Intents.all())

# Create a queue for storing songs
song_queue = asyncio.Queue()

# Create a function for adding a song to the queue
async def add_song(song_url):
    song = discord.FFmpegPCMAudio(song_url)
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
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=False)
        song_url = info['formats'][0]['url']
        await add_song(song_url)

    # If the bot is not currently playing a song, start playing the first song in the queue
    if not voice_client.is_playing():
        song = await song_queue.get()
        voice_client.play(song)

@client.command()
async def stop_song(ctx):
    """Stop the current song and clear the queue."""
    voice_client = ctx.voice_client
    # Stop the current song
    voice_client.stop()
    # Clear the queue
    while not song_queue.empty():
        song_queue.get_nowait()

@client.command()
async def skip_song(ctx):
    """Skip the current song and play the next song in the queue."""
    await skip_song()

client.run('BOT TOKEN HERE')
