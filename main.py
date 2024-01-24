import discord
import random
import sqlite3
from py2048 import G2048
import asyncio
import datetime
import dateutil.tz as dutz

f = open("text/login.txt", "r")
token = f.read()
f.close()

dbName = "data.db"

# consts below

f = open("text/shortResponses.txt", "r")
shortResponses = eval(f.read())
f.close()

f = open("text/shortReactions.txt", "r")
shortReactions = eval(f.read())
f.close()

f = open("text/helpPage.txt", "r")
helpPage = eval(f.read())
f.close()

f = open("text/badWords.txt", "r")
badWords = f.read().splitlines()
f.close()

f = open("text/sexWords.txt", "r")
sexWords = f.read().splitlines()
f.close()

skin2048 = "text/2048/skin.txt"

f = open(skin2048, "r+")
disp2048 = f.read().splitlines();
if len(disp2048) < 18:
  f.seek(0)
  f.write(''':black_large_square:
:two:
:four:
:eight:
:red_square:
:orange_square:
:yellow_square:
:green_square:
:blue_square:
:purple_square:
:white_large_square:
:white_check_mark:
:hash:
:atom:
:one:
:three:
:six:
:octagonal_sign:''')
  f.truncate()
f.close()

f = open("text/mentioned.txt", "r")
mentioned = f.read().splitlines()
f.close()

f = open("text/admin.txt", "r")
admin = [int(i) for i in f.read().splitlines()]
f.close()

s2048 = "text/2048/state.txt"
g2048 = G2048()

f = open(s2048, "r+")
try:
  g2048.fromString(f.read())
except:
  g2048.__init__()
  f.seek(0)
  f.write(g2048.toString())
  f.truncate()
f.close()

tDMessages = [
  {"time": {"hour": 7, "minute": 0, "second": 0}, "text": "good morning"},
  {"time": {"hour": 22, "minute": 30, "second": 0}, "text": "good night"},
  # {"time": {"hour": 0, "minute": 0, "second": 0}, "text": ""},
]

localTime = dutz.tzlocal()
tDChannelID = # INPUT CHANNEL ID HERE

# functions and classes below

async def timeDependent():
  tDChannel = client.get_channel(tDChannelID) # connect to channel in which messages will be sent
  
  while True:
    currentTime = datetime.datetime.now(localTime)
    print(f"current time: {currentTime}")
    
    nearest = datetime.timedelta(days = 1)
    message = "error what just happened" # this is impossible to reach
    
    for i in tDMessages:
      t = i["time"]
      t = datetime.datetime(
        year=currentTime.year,
        month=currentTime.month,
        day=currentTime.day,
        hour=t["hour"],
        minute=t["minute"],
        second=t["second"],
        tzinfo=localTime,
      )
      timeDifference = (t - currentTime)
      
      if timeDifference < datetime.timedelta():
        timeDifference += datetime.timedelta(days = 1) # e.g. it is 23:00 and waiting till 7:00
      
      if timeDifference < nearest:
        nearest = timeDifference
        message = i["text"]
    
    s = nearest.seconds + 1 # in case the program says it twice because it's technically the same second
    print(f"waiting for {s} seconds")
    await asyncio.sleep(s)
    await tDChannel.send(message)

def listNewline(l): # l -> str where str.splitlines() -> l
  r = ""
  for i in l:
    r += i + "\n"
  return r[:-1]


class g2048View(discord.ui.View):
  
  @discord.ui.button(label="", emoji="⬅")
  async def left(self, button, interaction):
    await self.move("left", interaction)
  
  @discord.ui.button(label="", emoji="⬆")
  async def up(self, button, interaction):
    await self.move("up", interaction)
  
  @discord.ui.button(label="", emoji="⬇")
  async def down(self, button, interaction):
    await self.move("down", interaction)
  
  @discord.ui.button(label="", emoji="➡")
  async def right(self, button, interaction):
    await self.move("right", interaction)
  
  async def move(self, direction, interaction):
    g2048 = G2048() # 2048 game
    f = open(s2048, "r+")
    g2048.fromString(f.read())
    
    x = g2048.move(direction)
    if x:
      g2048.generateTile()
    embed = discord.Embed(
      color = discord.Color.blurple(),
      title = f"Score: {g2048.score}"
    )
    if g2048.canMove():
      await interaction.response.send_message(g2048render(g2048), embed=embed, view=g2048View())
    else:
      embed.add_field(name="Game Over!", value=f"Board String: {g2048.toString()}", inline=False)
      await interaction.response.send_message(g2048render(g2048), embed=embed)
      g2048.__init__()
    
    f.seek(0)
    f.write(g2048.toString())
    f.truncate()
    f.close()

def g2048render(game):
  i = lambda x: disp2048[game.board[x]]
  return (i(0)+i(1)+i(2)+i(3)+"\n"+
          i(4)+i(5)+i(6)+i(7)+"\n"+
          i(8)+i(9)+i(10)+i(11)+"\n"+
          i(12)+i(13)+i(14)+i(15))

def checkWords(string, words): # check if any of the words includes the string
  string = string.lower()
  if type(words) == list:
    for i in words:
      if i in string:
        return True
  elif type(words) == dict: # if it does then return the custom value
    for i in words.keys():
      if i in string:
        return words[i]
  return False
  

def cstr(string):
  index = 0
  result = ""
  while index < len(string):
    char = string[index]
    if char == "/":
      index += 1
      result += string[index]
    else:
      if char == "-":
        result += " "
      else:
        result += string[index]
    index += 1
  return result

def tctr(string):
  return string.replace("/", "//").replace("-", "/-").replace(" ", "-")

def parse(inst):
  result = []
  while inst[0] == " ":
    inst = inst[1:]
  while inst[-1] == " ":
    inst = inst[:-1]
  inst = inst + " " # end of inst
  while inst != "":
    index = inst.index(" ")
    result.append(inst[:index])
    inst = inst[index + 1:]
  return result

async def interpret(message, channel):
  global disp2048
  
  try:
    if message.content == "":
      return None
    elif checkWords(message.content, badWords):
      await message.add_reaction("❌")
      await message.reply("bad word")
    elif checkWords(message.content, sexWords):
      await message.add_reaction("💦")
      await message.reply("*daddy~*")
    elif message.content.lower() in shortResponses.keys():
      await message.reply(shortResponses[message.content.lower()])
    elif message.content.lower() in shortReactions.keys():
      await message.add_reaction(shortReactions[message.content.lower()])
    elif client.user in message.mentions:
      await message.reply(random.choice(mentioned))
    if message.content[0] != ";":
      return None
    
    inst = parse(message.content)
    
    if inst[0] == ";quote": # return a random quote
      conn = sqlite3.connect(dbName) 
      cursor = conn.cursor()
      
      # count number of quotes
      cursor.execute("SELECT COUNT(dispid) FROM quotes")
      count = cursor.fetchone()[0]
      
      if count == 0:
        await message.reply("there are no quotes in the database")
        return None
      
      if len(inst) == 1:
        index = random.randint(1, count)
      elif len(inst) == 2:
        if inst[1] == "count":
          conn.close()
          await channel.send(f"there are {count} quotes")
          return None
        try:
          index = int(inst[1])
        except:
          await message.reply("that is not an integer")
          return None
        if index > count:
          conn.close()
          await message.reply(f"there's only {count} quotes")
          return None
        elif index < 1:
          await message.reply(f"did {message.author} just try to input quote #{index}?")
          return None
      else:
        await message.reply(f"too many parameters ({len(inst)})")
        return None
      
      cursor.execute("SELECT quote, speaker FROM quotes WHERE dispid=?", (index,))
      quote, speaker = cursor.fetchone()
      
      conn.close()
      
      await channel.send(f"> {quote}\n\\- *{speaker}*")
    elif inst[0] == ";admin":
      uid = message.author.id
      
      if not uid in admin: #dont let those without permission use it
        await channel.send(f"access denied. UID {uid}")
        return None
        
      if inst[1] == "error":
        await channel.send("throwing error")
        ""[0]
      elif inst[1] == "quote":
        conn = sqlite3.connect(dbName)
        cursor = conn.cursor()
        
        if inst[2] == "add":
          cursor.execute("SELECT MAX(dispid) FROM quotes")
          largest = cursor.fetchone()[0]
          if largest == None:
            largest = 0
          cursor.execute("INSERT INTO quotes (quote, speaker, dispid) VALUES (?, ?, ?)", (cstr(inst[3]), cstr(inst[4]), largest + 1))
          conn.commit()
          
          await channel.send(f"insertion command executed (quote {largest + 1})")
        elif inst[2] == "delete":
          index = int(inst[3])
          cursor.execute("SELECT MAX(dispid) FROM quotes") # gets row with largest dispid
          largest = cursor.fetchone()[0]
          cursor.execute("DELETE FROM quotes WHERE dispid = ?", (index,)) # deletes specified row
          if index != largest:
            cursor.execute("UPDATE quotes SET dispid = ? WHERE dispid = ?", (index, largest)) # swaps dispids
          conn.commit()
          
          await channel.send("deletion commands executed")
        elif inst[2] == "dump":
          index = int(inst[3])
          cursor.execute("SELECT quote, speaker FROM quotes WHERE dispid=?", (index,))
          quote, speaker = cursor.fetchone()
          if len(inst) > 4:
            if inst[4] == "cmd":
              await channel.send(f"```\n;admin quote add {tctr(quote)} {tctr(speaker)}\n```")
              return None
          await channel.send(f"```\n{quote}\n{speaker}\n```")
        elif inst[2] == "list": # list out quotes
          
          index = 1
          if len(inst) > 3:
            index = int(inst[3])
          
          cursor.execute("SELECT COUNT(dispid) FROM quotes")
          count = cursor.fetchone()[0]
          
          embed = discord.Embed(
            color = discord.Color.gold(),
            title = "List of Quotes",
          )
          
          r = 0
          while r < 12 and index <= count:
            r += 1
            cursor.execute("SELECT quote, speaker FROM quotes WHERE dispid=?", (index,))
            quote, speaker = cursor.fetchone()
            embed.add_field(name=index, value=f"> {quote}\n\\- *{speaker}*", inline=True)
            index += 1
          await channel.send(embed=embed)
          
        
        conn.close()
      elif inst[1] == "cstr":
        await channel.send(f"cstr output:\n{cstr(inst[2])}")
      elif inst[1] == "tctr":
        i = await channel.fetch_message(message.reference.message_id)
        await channel.send(f"```\n{tctr(i.content)}\n```")
      elif inst[1] == "help":
        await channel.send(f"```\n{helpPage[inst[2]]}\n```")
      elif inst[1] == "2048":
        g2048 = G2048() # 2048 game
        f = open(s2048, "r+")
        g2048.fromString(f.read())
        if inst[2] == "str":
          await channel.send(f"```\n{g2048.toString()}\n```")
        elif inst[2] == "set":
          g2048.fromString(inst[3])
          await channel.send("successful set")
        elif inst[2] == "reset":
          g2048.__init__()
          await channel.send("successful reset")
        elif inst[2] == "score":
          g2048.score = inst[3]
          await channel.send("successful score set")
        elif inst[2] == "board":
          g2048.fromString(f"{inst[3]}.{g2048.score}")
          await channel.send("successful board set")
        elif inst[2] == "skin":
          if inst[3] == "dump":
            g = open(skin2048, "r")
            await channel.send(f"```\n{g.read()}\n```")
            g.close()
          elif inst[3] == "set":
            disp2048 = inst[4].splitlines()
            g = open(skin2048, "w")
            g.write(inst[4])
            g.close()
            await channel.send("successful skin set")
        f.seek(0)
        f.write(g2048.toString())
        f.truncate()
        f.close()
      elif inst[1] == "kys":
        await channel.send("farewell")
        quit()
      elif inst[1] == "test":
        pass
    elif inst[0] == ";help":
      page = "home"
      if len(inst) > 1:
        if inst[1] in ["list"]:
          page = inst[1]
        else:
          page = ";" + inst[1]
      if not page in helpPage.keys():
        await channel.send("invalid page")
        return None
      embed = discord.Embed(
        color = discord.Color.blurple(),
        title = "Help Page" if page == "home" else page,
      )
      embed.add_field(name="Information", value=helpPage[page], inline=False)
      if page == "home":
        embed.add_field(name="Commands", value="You can use `;help [command]` to get information about a command. You can use `;help list` to list every command.", inline=False)
      await channel.send(embed=embed)
    elif inst[0] == ";2048":
      g2048 = G2048() # 2048 game
      f = open(s2048, "r+")
      g2048.fromString(f.read())
      if len(inst) > 1:
        x = g2048.move(inst[1])
        if x:
          g2048.generateTile()
        else:
          if inst[1] in ["up", "right", "down", "left"]:
            await message.reply("the move was registered but nothing happened")
          else:
            await message.reply("invalid move")
          f.close()
          return None
      embed = discord.Embed(
        color = discord.Color.blurple(),
        title = f"Score: {g2048.score}"
      )
      # embed.add_field(name="Information", value="Use `;2048 [direction]` to play! \n`[direction]` can be `up`, `right`, `down`, or `left`.", inline=False)
      if g2048.canMove():
        await channel.send(g2048render(g2048), embed=embed, view=g2048View())
      else:
        embed.add_field(name="Game Over!", value=f"Board String: {g2048.toString()}", inline=False)
        await channel.send(g2048render(g2048), embed=embed)
        g2048.__init__()
      f.seek(0)
      f.write(g2048.toString())
      f.truncate()
      f.close()
    else:
      pass
  except Exception as e:
    await channel.send(f"ERROR! <@{admin[0]}>\n {e}")
    raise e
  

class Monkey(discord.Client):
  async def on_ready(self):
    print(f"Logged on as {self.user}")
    timeDependentLoop.create_task(timeDependent())
    
  async def on_message(self, message): 
    if message.author == client.user:
      print(f"Message from self: {message.content}")
      return None
    
    print(f"Message from {message.author}: {message.content}")
    channel = client.get_channel(message.channel.id)
    await interpret(message, channel)
    
    

intents = discord.Intents.default()
intents.message_content = True

client = Monkey(intents=intents)

timeDependentLoop = asyncio.get_event_loop()

client.run(token)
