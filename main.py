import discord
from discord.ext import commands
import asyncio
from youtube_search import YoutubeSearch
from discord.utils import get
from discord_slash import SlashCommand
from discord_slash import SlashContext
from discord_slash.utils import manage_commands
import youtube_dl
import asyncio
import os
from keep_alive import keep_alive
import json
import random

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!",intents=intents)
slash = SlashCommand(bot, sync_commands=True)
playlist = [[]]
loop = False
volumes = 10

def set_Embed(title="",description="",color=random.randint(0x000000,0xFFFFFF)):
    return discord.Embed(title=title,description=description,color=color)

@bot.event
async def on_ready():
    print(f'로그인 성공: {bot.user.name}!')

async def song_start(ctx,voice,i):
    try:
        if not voice.is_playing() and not voice.is_paused():
            ydl_opts = {'format': 'bestaudio'}
            FFMPEG_OPTIONS = {'before_options': '-nostdin','options':'-vn'}
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"https://youtube.com{playlist[i][1]}",download=False)
                URL = info["formats"][0]["url"]
            voice.play(discord.FFmpegPCMAudio(URL,**FFMPEG_OPTIONS))
            voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
            voice.source = discord.PCMVolumeTransformer(voice.source)
            voice.source.volume = 0.5
        while voice.is_playing() or voice.is_paused():
            await asyncio.sleep(0.1)
    except:
        return


@bot.command(aliases=["play","p","재생"])
async def Play(ctx,*,keyword):
    try:
        results = YoutubeSearch(keyword,max_results=1).to_dict()
        global playlist
        playlist.append([results[0]['title'],results[0]['url_suffix']])
        await ctx.send(embed=set_Embed(title="노래 추가",description=f'{results[0]["title"]}'))

        channel = ctx.author.voice.channel
        if bot.voice_clients == []:
            await channel.connect()
        voice = bot.voice_clients[0]

        if not voice.is_playing() and not voice.is_paused():
            global i
            i = 0
            while True:
                await song_start(ctx,voice,i)
                if loop:
                    if i < len(playlist) - 1:
                        i = i + 1
                    else:
                        i = 0
                    continue
                elif i < len(playlist) -1:
                    i = i + 1
                    continue
                playlist = [[]]
                break
    except Exception as e:
        await ctx.send(f"Play Error\n{e}")
@bot.command(aliases=['loop','반복'])
async def Loop(ctx):
    try:
        global loop
        loop = True if loop == False else False
        await ctx.send(embed=set_Embed(title="반복",description=loop))
    except:
        await ctx.send("Loop Error")

@bot.command(aliases = ['save','저장'])
async def Save(ctx,*,arg):
    with open(f"{arg}.json", "w+", encoding='utf-8-sig') as f:
        global playlist
        json_string = json.dump(playlist, f, indent=2, ensure_ascii=False)

@bot.command(aliases = ["load","로드"])
async def Load(ctx,*,arg):
    try:
        global playlist
        jstring = open(f"{arg}.json", "r", encoding='utf-8-sig').read()
        playlist = json.loads(jstring)

        global i
        await ctx.send(embed=set_Embed("플레이리스트 추가 완료",f"저장된 플레이리스트 {arg}가 현재 플레이리스트에 로드되었습니다!",discord.Color.green()))

        channel = ctx.author.voice.channel
        if bot.voice_clients == []:
            await channel.connect()

        voice = bot.voice_clients[0]
        if voice.is_playing() or voice.is_paused():
            i = -1
            bot.voice_clients[0].stop()
        else:
            i = 0
            while True:
                await song_start(ctx,voice,i)
                if loop:
                    if i < len(playlist) -1:
                        i = i + 1
                    else:
                        i = 0
                    continue
                elif i < len(playlist) -1:
                    i = i + 1
                    continue
                playlist = [[]]
                break
    except:
        await ctx.send("Load Error")

@bot.command(aliases = ["q","que","플레이리스트"])
async def Que(ctx):
    try:
        quetext = ""
        for title in range(len(playlist)):
            try:
                quetext = f"{quetext}\n{title + 1}. {playlist[title][0]}"
            except:
                del playlist[title]
        await ctx.send(embed=set_Embed("플레이리스트",quetext))
    except:
        pass

@bot.command(aliases = ["remove","삭제"])
async def Remove(ctx,arg):
    try:
        global playlist
        remove_song = playlist[int(arg) - 1][0]
        del(playlist[int(arg) - 1])
        global i
        i = i -1
        if i + 1 == int(arg) - 1:
            bot.voice_clients[0].stop()
        await ctx.send(embed=set_Embed("노래 삭제 완료",remove_song))
    except:
        await ctx.send("노래 제거중 오류 발생")

@bot.command(aliases = ["leave","l","나가"])
async def Leave(ctx):
    try:
        await bot.voice_clients[0].disconnect()
    except:
        await ctx.send("Leave Error")

@bot.command(aliases = ["skip","s","스킵"])
async def Skip(ctx):
    try:
        bot.voice_clients[0].stop()
    except:
        await ctx.send("Skip Error")

@bot.command(aliases = ["pause","일시정지"])
async def Pause(ctx):
    try:
        bot.voice_clients[0].pause()
    except:
        await ctx.send("Pause Error")

@bot.command(aliases = ["resume","r","다시재생"])
async def Resume(ctx):
    try:
        bot.voice_clients[0].resume()
    except:
        await ctx.send("Resume Error")

@bot.command(aliases = ["volume","v","볼륨"])
async def Volume(ctx):
    """
    try:
        global volumes
        voice = get(bot.voice_clients, guild=ctx.guild)  
        if ctx.voice_client is None:
            return await ctx.send("봇이 음성채널에 있지 않습니다.")
        if vol > 0 and vol <= 100:
            if voice.is_playing():                          
                voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
                voice.source = discord.PCMVolumeTransformer(voice.source)
                voice.source.volume = vol / 100
            await ctx.send(embed=set_Embed("볼륨 변경",f"{ctx.author.mention}에 의해 불륨이 {vol}으로 변경되었습니다."))
            volumes = vol
        else:
            await ctx.send("볼륨을 1 ~ 200으로 입력 해 주세요")
            return
        volumes = vol
    except Exception as e:
        print(e)
        await ctx.send("Volume Error")
    """
    await ctx.send(embed=discord.Embed(title="볼륨 변경 방법",description="1.음성채널에 있는 봇 우클릭.\n2.사용자 볼륨에서 조절"))

keep_alive()
bot.run(os.getenv("token"))