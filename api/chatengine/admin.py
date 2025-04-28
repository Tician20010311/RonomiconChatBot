from django.contrib import admin

from chatengine.models import SimpleCommands , ChatBot , ChatUser, ChatLog

class ChatbotAdmin(admin.ModelAdmin):
    list_display = ("nickname", "twitch_channel")

class SimpleCommandsAdmin(admin.ModelAdmin):
    list_display = ("command", "response")

class ChatUserAdmin(admin.ModelAdmin):
    list_display = ("chatbot", "platform", "username")

class ChatLogAdmin(admin.ModelAdmin):
    list_display = ("sender", "created_at", "message", "response", "context")
    list_filter = ("chatbot", "platform", "sender")

admin.site.register(SimpleCommands, SimpleCommandsAdmin)
admin.site.register(ChatBot, ChatbotAdmin)
admin.site.register(ChatUser, ChatUserAdmin)
admin.site.register(ChatLog, ChatLogAdmin)
