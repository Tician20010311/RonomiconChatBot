from django.core.management.base import BaseCommand
from connections.platforms.twitch import Bot
from chatengine.engine import ChatEngine
from connections.platforms.twitch import Bot
from chatengine.models import ChatBot
from django.conf import settings

class Command(BaseCommand):
    help = 'A bot indítása...'

    def add_arguments(self, parser):
        parser.add_argument("--nickname",type=str)

    def handle(self, *args, **options):
        nickanem = options["nickname"]
        chatbot = ChatBot.objects.get(nickname=nickanem)
        chatengine = ChatEngine(chatbot=chatbot)
        bot = Bot(chatengine=chatengine)
        bot.run()
