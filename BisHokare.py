import discord
from discord.ext import commands
import youtube_dl
import asyncio
import dotenv
import os
from youtubesearchpython.__future__ import VideosSearch

dotenv.load_dotenv()
bot = commands.Bot(command_prefix=["&", "$"], description = "Bot pour tout le monde!")
bot.remove_command("help")
musics = {}
ytdl = youtube_dl.YoutubeDL()


@bot.event
async def on_ready():
    print("Ready")


class Video:
    def __init__(self, link):
        video = ytdl.extract_info(link, download=False)
        video_format = video["formats"][0]
        self.url = video["webpage_url"]
        self.stream_url = video_format["url"]

@bot.command()
async def leave(ctx):
    client = ctx.guild.voice_client
    await client.disconnect()
    musics[ctx.guild] = []

@bot.command()
async def resume(ctx):
    client = ctx.guild.voice_client
    if client.is_paused():
        client.resume()


@bot.command()
async def pause(ctx):
    client = ctx.guild.voice_client
    if not client.is_paused():
        client.pause()


@bot.command()
async def skip(ctx):
    client = ctx.guild.voice_client
    client.stop()


def play_song(client, queue, song):
    source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(song.stream_url
        , before_options = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"))

    def next(_):
        if len(queue) > 0:
            new_song = queue[0]
            del queue[0]
            play_song(client, queue, new_song)
        else:
            asyncio.run_coroutine_threadsafe(client.disconnect(), bot.loop)

    client.play(source, after=next)


@bot.command()
async def play(ctx, text):
	print("play")
	client = ctx.guild.voice_client

	search = VideosSearch(text, limit=1)
	result = await search.next()

	if client and client.channel:
		video = Video(result['result'][0]['link'])
		musics[ctx.guild].append(video)
	else:
		channel = ctx.author.voice.channel
		video = Video(result['result'][0]['link'])
		musics[ctx.guild] = []
		client = await channel.connect()
		await ctx.send(f"Je lance : {video.url}")
		play_song(client, musics[ctx.guild], video)

@bot.command()
async def help(message):
	prefix = (await bot.get_prefix(message))[0]
	embed = discord.Embed(
		color=discord.Color.from_rgb(176, 86, 0), #rgb(135,206,250)
		title="Commandes",
		description=f"``{prefix}play (URL YT)`` : Lance la musique dans ton salon vocal \n ``{prefix}pause`` : Met en pause la musique \n ``{prefix}resume`` : Reprends la musique \n ``{prefix}skip`` : Passe à la musique suivante"
	)
	await message.channel.send(embed=embed)


bot.run(os.getenv("TOKEN"))