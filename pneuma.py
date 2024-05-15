import discord
from discord.ext import commands
import yt_dlp as youtube_dl
from dotenv import load_dotenv
import os
from youtubesearchpython import VideosSearch
import logging
import asyncio

load_dotenv()

TOKEN = os.getenv('TOKEN')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# you may need to adjust this path if you have errors
ffmpeg_path = 'ffmpeg' 

# generates an easier to read suppressed error
youtube_dl.utils.bug_reports_message = lambda: ''

# error tracker
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("bot.log"),
                        logging.StreamHandler()
                    ])

logger = logging.getLogger(__name__)

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    # this does not expose your public IP address, use Hamachi if you have connectivity problems or concerns
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        try:
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        except youtube_dl.utils.DownloadError as e:
            raise discord.DiscordException(f"Pneuma could not extract information from URL: {url}")

        if 'entries' in data:
            # Take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

async def disconnect_after_timeout(ctx, timeout=300):
    await asyncio.sleep(timeout)
    if not ctx.voice_client.is_playing():
        await ctx.voice_client.disconnect()
        await ctx.send("Pneuma disconnected from the voice channel due to inactivity.")


@bot.event
async def on_ready():
    logger.info(f'Pneuma connected as {bot.user}')


## BOT COMMANDS ##

@bot.command(name='join')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send('You are not connected to a voice channel.')
        return
    else:
        channel = ctx.message.author.voice.channel

    await channel.connect()

@bot.command(name='play')
async def play(ctx, *, query):
    # Check if the bot is in a voice channel
    if ctx.voice_client is None:
        await ctx.send("Pneuma is not connected to a voice channel!! Use !join to invite the bot to your voice channel.")
        return

    async with ctx.typing():
        if query.startswith('http'):
            url = query
        else:
            videos_search = VideosSearch(query, limit=1)
            video_result = videos_search.result()['result'][0]
            url = video_result['link']

        try:
            player = await YTDLSource.from_url(url, loop=bot.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: logger.error(f'Player error: {e}') if e else None)
            await ctx.send(f'Pneuma now playing: {player.title}')

            # Cancel any existing disconnect task and start a new one
            if hasattr(ctx.voice_client, 'disconnect_task'):
                ctx.voice_client.disconnect_task.cancel()

            ctx.voice_client.disconnect_task = bot.loop.create_task(disconnect_after_timeout(ctx))

        except Exception as e:
            await ctx.send(f'An error occurred: {str(e)}')

@bot.command(name='leave')
async def leave(ctx):
    if ctx.voice_client is not None:
        await ctx.voice_client.disconnect()
        await ctx.send("Pneuma disconnected from the voice channel.")
    else:
        await ctx.send("Pneuma is not connected to a voice channel.")

@bot.command(name='pause')
async def pause(ctx):
    if ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send('Paused the song.')
    else:
        await ctx.send('No audio is playing.')

@bot.command(name='resume')
async def resume(ctx):
    if ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send('Resumed the song.')
    else:
        await ctx.send('The audio is not paused.')

@bot.command(name='stop')
async def stop(ctx):
    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send('Stopped the song.')

        # Cancel any existing disconnect task and start a new one
        if hasattr(ctx.voice_client, 'disconnect_task'):
            ctx.voice_client.disconnect_task.cancel()

        ctx.voice_client.disconnect_task = bot.loop.create_task(disconnect_after_timeout(ctx))
    else:
        await ctx.send('No audio is playing.')

# Replace 'TOKEN' with your bot's token from your .env
bot.run(TOKEN)
