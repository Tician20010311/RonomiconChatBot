from chatengine.models import SimpleCommands, ChatUser
from django.template import Context, Template
from asgiref.sync import sync_to_async
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from django.conf import settings
from chatengine.games import Roulette , Blackjack


class ChatEngine:
    def __init__(self, chatbot):
        self.chatbot = chatbot
        self.simple_commands = {}
        self.openai_api_key = settings.OPENAI_API_KEY
        self.non_command_strings = []
        self.inicialize_games()
        self.load_commands()

    def inicialize_games(self):
        self.games = {"rulett": Roulette(self.chatbot),"blackjack":Blackjack(self.chatbot)}


    async def update_data(self):
        await sync_to_async(self.load_commands, thread_sensitive=True)()

    def load_commands(self):
        self.simple_commands = {}
        for command in SimpleCommands.objects.filter(
            chatbot__nickname=self.chatbot.nickname
        ):
            self.simple_commands[command.command] = command.response
        self.non_command_strings = self.simple_commands.keys()

    # Kapott szöveg átfogalmazása
    def rephrase_text(self, text):
        rephrase_prompt = self.chatbot.rephrase_prompt
        llm = ChatOpenAI(
            model_name="gpt-4o", temperature=1.0, api_key=self.openai_api_key
        )
        reword_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    rephrase_prompt,
                ),
                ("human", "Átfogalmazandó szöveg: " + text),
            ]
        )
        chain = reword_prompt | llm
        ai_response = chain.invoke({})
        return ai_response.content

    # Generál egy generic responset

    def generate_generic_response(self, sender, message):
        generic_prompt = self.chatbot.generic_prompt
        llm = ChatOpenAI(
            model_name="gpt-4.1", temperature=0.7, api_key=self.openai_api_key
        )
        answer_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    generic_prompt,
                ),
                ("human", sender + ": " + message),
            ]
        )
        chain = answer_prompt | llm
        ai_response = chain.invoke({})
        return ai_response.content

    @sync_to_async
    def get_or_create_chatuser(self, nickname):
        chatuser, _ = ChatUser.objects.get_or_create(
            chatbot=self.chatbot, platform="twitch", username=nickname
        )
        return chatuser

    async def play_roulette(self, sender, message):
        chatuser = await self.get_or_create_chatuser(sender)
        game = self.games["rulett"]
        return await game.player_move(chatuser, message)

    async def play_blackjack(self, sender, message):
        chatuser = await self.get_or_create_chatuser(sender)
        game = self.games["blackjack"]
        return await game.player_move(chatuser, message)

    async def get_response(self, source, sender, message):
        # await sync_to_async(self.chatbot.refresh_from_db())
        await self.update_data()
        command = ""
        non_command = ""
        matching_non_commands = [
            s for s in self.non_command_strings if message.lower().startswith(s)
        ]
        points_commands = ["pontszám", "pontszam", "points"]
        if any(
            [
                message.startswith(f"{self.chatbot.twitch_prefix}{c}")
                for c in points_commands
            ]
        ):
            chatuser = await self.get_or_create_chatuser(sender)
            return f"Kedves {sender}, jelenelegi pontszámod: {chatuser.current_score}"
        elif message.startswith(f"{self.chatbot.twitch_prefix}rulett"):
            return await self.play_roulette(sender, message)
        elif message.startswith(f"{self.chatbot.twitch_prefix}blackjack"):
            return await self.play_blackjack(sender, message)
        # Ha a szöveg egy kész parancs
        if matching_non_commands:
            non_command = matching_non_commands[0]
            template = Template(self.simple_commands[non_command])
            context = Context({"sender": sender, "message": message})
            return self.rephrase_text(template.render(context))
        # Ha a szöveg előtt prefixet kap ("!")
        elif source == "twitch" and message.startswith(self.chatbot.twitch_prefix):
            command = message[1:]
            method = getattr(self, "on_" + command, None)
            if method:
                response = method(sender, message)
                return self.rephrase_text(response)
        # Ha "@"
        elif (
            source == "twitch"
            and f"@{self.chatbot.nickname.lower()}" in message.lower()
        ):
            return self.generate_generic_response(sender, message)
        return ""
