import discord, random
from core.config import Configuration
from core.client import Client
from core.console import Console
from core.enums import Auth, Event, Restriction
from core.music import Music

client = Client(
    config = Configuration(),
    music_path = ".music"
)

@client.react(Event.ON_COMMAND, 'ping', permission = Auth.DEFAULT)
async def test_command(message, *args):
    await message.channel.send('Pong!')
    
@client.react(Event.ON_COMMAND, 'test', permission = Auth.OWNER)
async def test2_command(message, *args):
    await message.channel.send('Seems like you have atleast owner permission.')
    
@client.react(Event.ON_COMMAND, 'set', permission = Auth.DEFAULT)
async def test3_command(message, *args):
    try:
        auth = Auth.convert(message.content.split(' ')[1])
    except ValueError as e:
        await message.reply(e)
        return
    client.retrieve_server(message.guild.id).retrieve_member(message.author.id).permission = auth
    await message.reply(f"Successfully changed your server permission to {auth}")
    
@client.react(Event.ON_COMMAND, 'nsfw', restriction = Restriction.NSFW)
async def test4_command(message, *args):
    await message.channel.send('Seems like this is a nsfw channel.')
    
# @client.react(Event.ON_MESSAGE, after_command = True)
# async def test5_on_message(message):
#     await message.channel.trigger_typing()
#     await message.channel.send('This was triggered after command')
# 
# @client.react(Event.ON_MESSAGE)
# async def test6_on_message(message):
#     await message.channel.trigger_typing()
#     await message.channel.send('This was triggered before command')
    
@client.react(Event.ON_REACTION_ADD)
async def test7_on_reaction_add(reaction, user):
    await reaction.message.reply(f'{user.mention} reacted to this message')
    
# @client.react(Event.ON_REACTION_REMOVE)
# async def test8_on_reaction_remove(reaction, user):
#     await reaction.message.reply(f'{user.mention} removed his reacton from this message')

@client.react(Event.ON_COMMAND, "latency")
async def current_latency(message : discord.Message, *args):
    await message.reply(f"Current ping is {round(client.latency, 1)}")

@client.react(Event.ON_COMMAND, "join")
async def join_voice(message : discord.Message, *args):
    voice_channel : discord.VoiceChannel = message.author.voice
    if voice_channel is not None:
        vc = await voice_channel.connect()
        vc.listen(client._audio_sink)
        await message.channel.send(f"I'm now listening to {voice_channel.name}")

@client.react(Event.ON_COMMAND, "leave", requires_voice = True)
async def join_voice(message : discord.Message, *args):
    voice_channel = message.guild.voice_client.channel
    vc = message.guild.voice_client
    vc.stop()
    vc.stop_listening()
    await vc.disconnect()
    await message.channel.send(f"I'm no longer listening to {voice_channel.name}")

@client.react(Event.ON_COMMAND, "record", requires_voice = True)
async def start_record(message, *args):
    vc : discord.VoiceClient = await message.author.voice.channel.connect() # Connect to the voice channel of the author
    vc.start_recording(discord.sinks.MP3Sink(), finished_callback, ctx) # Start the recording
    vc.average_latency()
    await message.reply("Recording...")

@client.react(Event.ON_COMMAND, "play")
async def test_music_command(message, *args):
    # Gets voice channel of message author
    arg = ' '.join(args)
    await message.reply(f"Searching for '{arg}'")
    await message.channel.trigger_typing()
    voice_channel = message.author.voice
    channel = None
    if voice_channel is not None:
        vc = await voice_channel.channel.connect()
        track = client.music.search_track(arg)
        await message.channel.send(f"Now playing '{track.name}'")
        vc.play(discord.FFmpegPCMAudio(executable = "ffmpeg.exe", source = track.path))
        # Sleep while audio is playing.
        # while vc.is_playing():
        #     sleep(.1)
        # await vc.disconnect()
    else:
        await message.reply("You are not in a voice channel.")

console = Console()

@console.func('scan')
def test_console(path):
    client.music.merge(Music.scan(path))
    client.music.save(path)
    
@console.func('test2')
async def test_async_console(*args):
    game = discord.Game(' '.join(args))
    await client.change_presence(activity = game)

client.run(access_console = console)

# client.run(threaded = True)
# 
# while not client.is_ready:
#     pass
# 
# while True:
#     pass