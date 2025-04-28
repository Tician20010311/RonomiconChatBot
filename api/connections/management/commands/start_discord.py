from django.core.management.base import BaseCommand
from django.conf import settings
from chatengine.engine import ChatEngine
from chatengine.models import ChatBot
from connections.platforms.discord_connection import set_chatengine , get_discord_client

class Command(BaseCommand):
    help = 'A bot indítása...'

    def add_arguments(self, parser):
        parser.add_argument("--nickname",type=str)

    def handle(self, *args, **options):
        nickanem = options["nickname"]
        chatbot = ChatBot.objects.get(nickname=nickanem)
        chatengine = ChatEngine(chatbot=chatbot)
        set_chatengine(chatengine)
        discord_client = get_discord_client()
        discord_client.run(settings.DISCORD_ACCESS_TOKEN)

