from django.contrib import admin

from chatengine.models import SimpleCommands , ChatBot , ChatUser

class ChatbotAdmin(admin.ModelAdmin):
    list_display = ("nickname", "twitch_channel")

class SimpleCommandsAdmin(admin.ModelAdmin):
    list_display = ("command", "response")

class ChatUserAdmin(admin.ModelAdmin):
    list_display = ("chatbot", "platform", "username")

admin.site.register(SimpleCommands, SimpleCommandsAdmin)
admin.site.register(ChatBot, ChatbotAdmin)
admin.site.register(ChatUser, ChatUserAdmin)
