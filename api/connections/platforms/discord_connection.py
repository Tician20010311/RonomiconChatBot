import discord

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(
    intents=intents,
    status=discord.Status.online)

chatengine = None
SOURCE_NAME = "discord"

def set_chatengine(ce):
    global chatengine
    chatengine = ce

def get_discord_client():
    return client

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    print(f"{message.author}: {message.author.name}/: {message.content}")

    response = await chatengine.get_response(
        SOURCE_NAME,
        message.author.name, 
        message.content,
        )
    if response:
        await message.channel.send(response)

