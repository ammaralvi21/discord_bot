import os
import discord
import sys
from discord import VoiceState, Member, FFmpegPCMAudio
from discord.ext.commands import Bot
from dotenv import load_dotenv
import time
from gtts import gTTS
import datetime
import random
import asyncio
import logging
import emoji
from transformers import BartTokenizer, BartForConditionalGeneration

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
LOG = logging.getLogger(__name__)

LOG.info('Fetching Komeiji Bart Emoji')
path = "KomeijiForce/bart-large-emojilm"
tokenizer = BartTokenizer.from_pretrained(path)
generator = BartForConditionalGeneration.from_pretrained(path)

def translate(sentence, **argv):
    inputs = tokenizer(sentence, return_tensors="pt")
    generated_ids = generator.generate(inputs["input_ids"], **argv)
    decoded = tokenizer.decode(generated_ids[0], skip_special_tokens=True).replace(" ", "")
    return decoded


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

LOG.info('Fetching word list')
WORDLE_WORDS = open("wordle.txt").read().splitlines()

@client.event
async def on_ready():
    LOG.info(f'{client.user=}')
    LOG.info(f'{client.user.id=}')
    for guild in client.guilds:
        for channel in guild.channels:
            LOG.info(f"{channel=}")
        if guild.name == GUILD:
            break
    LOG.info(f'{client.user} is connected to the following guild: {guild.name}(id: {guild.id})')
    client.loop.create_task(wordle_word())
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
    LOG.info(f"on_voice_state_update {member=}, {before=}, {after=}")
    if member.nick is not None:
        name = member.nick
    else:
        name = member
    if not before.channel and after.channel and member.id != client.user.id:
        await join_play_audio(state=after, audio=get_tts(text=f"{name} has joined", filename="welcome"))

    if before.channel and not after.channel and member.id != client.user.id:
        await join_play_audio(state=before, audio=get_tts(text=f"{name} has left", filename="goodbye"))

    if before.self_mute and not after.self_mute and member.id != client.user.id:
        await join_play_audio(state=before, audio=get_tts(text=f"{name} has self unmuted", filename="unmuted"))

    if not before.self_mute and after.self_mute and member.id != client.user.id:
        await join_play_audio(state=before, audio=get_tts(text=f"{name} has self muted", filename="muted"))

    if before.self_stream and not after.self_stream and member.id != client.user.id:
        await join_play_audio(state=before, audio=get_tts(text=f"{name} stopped streaming", filename="stop_streaming"))

    if not before.self_stream and after.self_stream and member.id != client.user.id:
        await join_play_audio(state=before, audio=get_tts(text=f"{name} started streaming", filename="start_streaming"))

    if before.afk and not after.afk and member.id != client.user.id:
        await join_play_audio(state=before, audio=get_tts(text=f"{name} is back", filename="isnt_afk"))

    if not before.afk and after.afk and member.id != client.user.id:
        await join_play_audio(state=before, audio=get_tts(text=f"{name} is now AFK", filename="is_afk"))


    if before.channel and after.channel and before.channel != after.channel and member.id != client.user.id:
        await join_play_audio(state=before, audio=get_tts(text=f"{name} has left",   filename="goodbye"))
        await join_play_audio(state=after,  audio=get_tts(text=f"{name} has joined", filename="welcome"))

async def wordle_word():
    LOG.info(f"wordle_word: initializing")
    last = time.time()
    await client.wait_until_ready()
    my_chan = None
    LOG.info(f"wordle_word: finding guild + channel")
    for guild in client.guilds:
        if guild.name == GUILD:
            for channel in guild.channels:
                if channel.name == "scotts-miners":
                    my_chan = channel
                    LOG.info(f"Channel found {channel=}")
                    break
    LOG.info(f"wordle_word: entering main loop")
    while not client.is_closed():
        curr_hr = datetime.datetime.now(datetime.UTC).hour
        elapsed = time.time() - last
        wait_s = 3*3600    # 3 hour wait
        schedule_hr = 11   # At utc=11, pst=4, est=7
        LOG.info(f"Alive message, {curr_hr=}, {elapsed=}, {wait_s=}")
        if curr_hr == schedule_hr and elapsed > wait_s:
            LOG.info(f"Hour match and elapsed time match")
            last = time.time()
            if my_chan is not None:
                await my_chan.send(content=f'WAKE UP!!!!!, Today\'s first word: "{random.choice(WORDLE_WORDS)}"')
            else:
                LOG.info(f"Channel not found {client.guilds=}")
                for guild in client.guilds:
                    for channel in guild.channels:
                        LOG.info(f"Available channels: {guild=} {channel=}")
        await asyncio.sleep(30)

@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return

    if message.content.startswith('$dt poll'):
        p = discord.Poll(question="Play", multiple=False, duration=datetime.timedelta(hours=1.0))
        p.add_answer(text="Yes")
        p.add_answer(text="No")
        await message.channel.send(poll=p)
    if message.author.nick in ['Ammar', 'Brandon'] and message.channel.name == "scotts-miners":
        sentence = message.content
        decoded = translate(sentence, num_beams=4, do_sample=True, max_length=100)
        valid_emojis = []
        for ch in decoded:
            if emoji.is_emoji(ch):
                valid_emojis.append(ch)
        for emj in valid_emojis:
            await message.add_reaction(emj)

client.run(TOKEN)