import os
import discord
from discord import VoiceState, Member, FFmpegPCMAudio
from discord.ext.commands import Bot
from dotenv import load_dotenv
import time
from gtts import gTTS
import datetime


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'{client.user=}')
    print(f'{client.user.id=}')
    for guild in client.guilds:
        for channel in guild.channels:
            print(f"{channel=}")
        if guild.name == GUILD:
            break
    print(f'{client.user} is connected to the following guild: {guild.name}(id: {guild.id})')
    # myobj = gTTS(text=f"Hey there fuckers", lang='en', slow=False)
    # myobj.save("welcome.mp3")
    # #ch.play(discord.FFmpegPCMAudio(executable="C:/ffmpeg/bin/ffmpeg.exe", source="welcome.mp3"))
    # #await ch.play(discord.FFmpegPCMAudio(executable="C:/path/ffmpeg.exe", source="C:/songpath"))
    # audio_source = discord.FFmpegPCMAudio('/home/bbandit/ws/discord_bot/welcome.mp3')
    # vc = await ch.connect()
    # vc.play(audio_source)
    
    # await ch.connect()
    # await ch.send("Hello, my name is deep throat", tts=True)

async def join(state: VoiceState):
    ch = state.channel
    vc = discord.utils.get(client.voice_clients, guild=ch.guild)
    if vc is not None and vc.channel.id == ch.id:
        time.sleep(0.7)
        return vc
    elif vc is not None:
        await vc.disconnect()
        vc = await ch.connect()
        return vc
    else:
        vc = await ch.connect()
        return vc


async def join_play_audio(state: VoiceState, audio: FFmpegPCMAudio):
    vc = await join(state=state)
    while vc.is_playing():
        pass
    vc.play(audio)


def get_tts(text, filename):
    filepath = f'/tmp/{filename}.mp3'
    myobj = gTTS(text=text, lang='en', slow=False)
    myobj.save(filepath)
    return FFmpegPCMAudio(filepath)


@client.event
async def on_voice_state_update(member: Member, before: VoiceState, after: VoiceState):
    print(f"on_voice_state_update {member=}, {before=}, {after=}")
    if not before.channel and after.channel and member.id != client.user.id:
        await join_play_audio(state=after, audio=get_tts(text=f"{member} has joined", filename="welcome"))

    if before.channel and not after.channel and member.id != client.user.id:
        await join_play_audio(state=before, audio=get_tts(text=f"{member} has left", filename="goodbye"))

    if before.channel and after.channel and member.id != client.user.id:
        await join_play_audio(state=before, audio=get_tts(text=f"{member} has left",   filename="goodbye"))
        await join_play_audio(state=after,  audio=get_tts(text=f"{member} has joined", filename="welcome"))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$deepthroat test poll'):
        p = discord.Poll(question="Is this useful?", multiple=False, duration=datetime.timedelta(hours=1.0))
        p.add_answer(text="Yes")
        p.add_answer(text="No")
        await message.channel.send(poll=p)

client.run(TOKEN)
