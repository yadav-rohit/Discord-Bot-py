import os
import discord
import logging
from dotenv import load_dotenv
from online import keep_alive
import nacl
from discord import FFmpegPCMAudio
import youtube_dl
import discord.utils
from discord.ext import commands, tasks
from itertools import cycle
from youtubesearchpython import VideosSearch


load_dotenv()

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log',
                              encoding='utf-8',
                              mode='w')
handler.setFormatter(
    logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

bot = commands.Bot(command_prefix="$")


@bot.command(name="ping")
async def ping(ctx: commands.Context):
    await ctx.send(f"Pong! {round(bot.latency * 1000)}ms")
    print('wokred')

@bot.event
async def on_ready():
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.listening ,name="Zen Modders"))
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
# announcment code
@bot.command(name="anc")
async def anc(ctx):   
    await ctx.send(f"Enter The Announcment")

    # This will make sure that the response will only be registered if the following
    # conditions are met:
    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel 
      

    msg = await bot.wait_for("message", check=check)
    tit = await ctx.send(f"Enter The Title")
    def check(ttle):
        return msg.author == ctx.author and msg.channel == ctx.channel 
    ttle = await bot.wait_for("message", check=check)
    channel = bot.get_channel('#enter your anouncment channel id here') 
    
    # await channel.send(f'{ctx.message.guild.default_role} {msg.content}')
    embed=discord.Embed(title=f"{ttle.content}", description=f"{msg.content}", color=53380)
    await channel.send(f'{ctx.message.guild.default_role}')
    await channel.send(embed=embed)    


#music code
song_played=[]
song_url=[]
chvc=[]

#before running install pip install pynacl
#for audio pip install ffmpeg

FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'} #locking options for ffmpeg


#infinite loop to play music 24X7 untill closed/stopped 
@tasks.loop(seconds=5)
async def play_song(ctx, ch, channel,l):
  voice = discord.utils.get(bot.voice_clients, guild=ctx.guild) 
  global song_url
  #print(song_url)
  url=song_url[0]
  if not ch.is_playing() and not voice == None :
    try: 
      ydl_opts = {'format': 'bestaudio/best'}
      with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        video_title = info.get('title', None)
        URL = info['formats'][0]['url']
      ch.play(discord.FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
      text = embedding(f" Playing :{video_title}")
      await ctx.send(embed=text, delete_after=60.0)
      song_played.append(song_url[0])
      song_url.pop(0)
    except:
      await ctx.send("Connection Error!!")
  if len(song_url) == 0:
    for i in range(0,len(song_played)):
      song_url.append(song_played[i])
    
    song_played.clear()
  
@bot.command(help= "Skip the current song")
async def skip(ctx):
  ch=chvc[0]
  ch.stop()




#sets volume to user defined value
@bot.command()
async def volume(ctx, x: int):
  y=x/100
  vc = discord.utils.get(bot.voice_clients, guild=ctx.guild)
  vc.source = discord.PCMVolumeTransformer(vc.source)
  vc.source.volume = y
  text = discord.Embed(
  title= "**Volume Control**",
  description = f" Volume set to {int(x)} ",
  color= 53380,
  )
  await ctx.send(embed=text)


#play command to start an infinite loop

@bot.command(help="Channel name is optional." , brief="This command plays song from the available ones.Providing channel name is optional without which it will play on General")
async def play(ctx, channel='🔊only-songs1'):
 
 #joining the desired channel
  voice = discord.utils.get(bot.voice_clients, guild=ctx.guild) 
  # channel = discord.utils.get(ctx.guild.voice_channels, name=channel)
  channel = bot.get_channel(927962396167909447)
  if voice == None:
    await ctx.send(f"Joined **{channel}**")
  else:
    await ctx.voice_client.disconnect()
  ch = await channel.connect()
  if(len(chvc)!=0):
    chvc.pop(0)
  chvc.append(ch)
  print(chvc)
  await ctx.send(f"Playing on **{channel}** Channel")
  
  #get the number of songs and if none is present it will show up a message
  n = len(song_url)
  if not n==0:
    n=n-1
    play_song.start(ctx, ch, channel,n)
  else:
    text = discord.Embed(
    title= "**No Music**",
    description = "There is no music to play\nUse _add [url] to add a music",
    color= 53380,
    )

    await ctx.send(embed=text)
    


#add music
@bot.command(help='youtube link is required', brief='This adds a music to the playlist. The url must be of youtube')
async def add(ctx, * ,searched_song):
  print(searched_song)

  videosSearch = VideosSearch(searched_song, limit = 1)
  result_song_list = videosSearch.result()
  # print(result_song_list)
  title_song = result_song_list['result'][0]['title']
  urllink = result_song_list['result'][0]['link']

  song_url.append(urllink)
  text = discord.Embed(
  title= "**Song Added**",
  description = f"{title_song} is added to the Queue\nLink : {urllink}",
  color= 53380,
  )
  # text.add_image(url=f"{result_song_list['result'][0]['thumbnail']['url']}")
  await ctx.send(embed=text)
  # await ctx.send(f"LINK : {urllink} ADDED")
  

#leave vc and stop playing
@bot.command(help='This stops the loop' ,brief='This stops the music playing and the bot leaves the voice channel')
async def stop(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild) 
    if voice == None:
      return
    await ctx.voice_client.disconnect()
    play_song.stop()
    for i in range(0,len(song_played)):
      song_url.append(song_played[i])
    await ctx.send("Have left the channel")



#lists song
@bot.command(help="This shows the songs present in the directory" ,brief='This command lists all the songs available to play')
async def songs(ctx):
  l=len(song_url)
  if(l==0):
    await ctx.send("No music to play")
  for i in range(0,l):
      videosSearch = VideosSearch(song_url[i], limit = 1)
      result_song_list = videosSearch.result()
      # print(result_song_list)
      title_song = result_song_list['result'][0]['title']
      text = discord.Embed(
      description = f"{i+1}# Song Name : {title_song} ",
      color= 53380,
      )

      await ctx.send(embed=text)

#removes every song
@bot.command(help='The file name should be wiht mp3 extension' , brief='This command removes every0 available song')
async def clear_playlist(ctx):
  song_url.clear()
  text= discord.Embed(
  description="**Playlist cleared**",
  color = 53380,
  )

  await ctx.send(embed=text)


#clear
@bot.command(help='This command clears text messages', brief='This command clears given number of messages and by default it clears last 5 text messages')
async def clear(ctx, amount=5):
    await ctx.channel.purge(limit=amount)
    text = embedding("Cleared")
    await ctx.send(embed=text)

#remove a particular song   
@bot.command(help='The file name should be wiht mp3 extension' , brief='This command removes the specified file')
async def remove(ctx,x: int):
  x=x-1
  videosSearch = VideosSearch(song_url[x], limit = 1)
  result_song_list = videosSearch.result()
  title_song = result_song_list['result'][0]['title']
  text= embedding(f"{title_song} Removed")
  await ctx.send(embed=text)
  song_url.pop(x)

#custom help command
@bot.group(invoke_without_command=True)
async def hlp(ctx):
  text = discord.Embed(
  title= "**HELP TAB**",
  description = "***Welcome to Help Tab. Below are definations and how to use commands section*** \n\n$add** [url]\n\nThis adds the music to queue \n\n**$play [VoiceChannel(optional)]**\n\nThis command plays music in the desired channel or by default in General\n\n**$songs** \n\n Lists all the songs in the playlist\n\n**$volume [integer value]**\n\nSets the volume level\n\n**$stop**\n\nStops the music player\n\n**$clear_playlist**\n\nRemoves every song from the playlist\n\n**$remove [index from the list of songs provided by typing $songs]**\n\nRemoves the particular song\n\n",
  color= 53380,
  )
  
  await ctx.send(embed=text)
  
#embeds text  
def embedding(text: str):
  text= discord.Embed(
  description=f"**{text}**",
  color = 53380,
  )
  return(text)
  
#checks for errors
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('Invalid Command Used. Type //help to know the commands'
                       )
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(
            'Give proper values to the command an argument is missing')




keep_alive()
bot.run(os.getenv('TOKEN'))
