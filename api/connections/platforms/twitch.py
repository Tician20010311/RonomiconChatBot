from twitchio.ext import commands
import datetime
import asyncio

class Bot(commands.Bot):

    SOURCE_NAME = "twitch"
    MESSAGE_FRAQUENCY = 2.0

    def __init__(self, chatengine):
        self.prefix = '!'
        super().__init__(token=chatengine.chatbot.access_token, prefix=chatengine.chatbot.twitch_prefix, initial_channels=[f'#{chatengine.chatbot.twitch_channel}'])
        self.chatengine = chatengine
        self.last_message_sent = datetime.datetime.now().timestamp()

    async def event_ready(self):
        print(f'Bejelentkezve mint : {self.nick}')
        print(f'UserID : {self.user_id}')

    async def send(self,channel , message):
        if not message:
            return
        time_since_last_message = datetime.datetime.now().timestamp() - self.last_message_sent 
        if time_since_last_message < self.MESSAGE_FRAQUENCY:
            # We have to wait a bit befor sending the next message
            await asyncio.sleep(self.MESSAGE_FRAQUENCY - time_since_last_message)
        await channel.send(message)
        self.last_message_sent = datetime.datetime.now().timestamp()

    async def event_message(self, message):
        if message.echo:
            return
        print(f"{message.author.name}: {message.content}")
        response = await self.chatengine.get_response(self.SOURCE_NAME,message.author.name, message.content)
        if response:
            message_arr = []
            while len(response) > 500:
                cut_index = response[:500].rfind(' ')
                message_arr.append(response[:cut_index])
                response = response[cut_index:]
            message_arr.append(response)
            for response in message_arr:
                await self.send(message.channel, response)
