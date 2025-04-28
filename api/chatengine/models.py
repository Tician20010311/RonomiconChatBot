from django.db import models


class ChatBot(models.Model):
    access_token = models.CharField(max_length=200, null=True, blank=True)
    refresh_token = models.CharField(max_length=200, null=True, blank=True)
    expires_in = models.IntegerField()
    token_type = models.CharField(max_length=200, null=True, blank=True)
    nickname = models.CharField(max_length=200)
    twitch_channel = models.CharField(max_length=200, null=True, blank=True)
    openai_api_key = models.CharField(max_length=200, null=True, blank=True)
    rephrase_prompt = models.TextField(blank=True, null=True)
    twitch_prefix = models.CharField(max_length=20,blank=True, null=True,default="!")
    generic_prompt = models.TextField(blank=True,null=True)

    def __str__(self):
        return f"{self.nickname} ({self.twitch_channel})"
    
class ChatUser(models.Model):
    chatbot = models.ForeignKey(ChatBot, on_delete=models.CASCADE)
    platform = models.CharField(max_length=200)
    username = models.CharField(max_length=200)
    callname = models.CharField(max_length=200, blank=True, null=True) 
    current_score = models.IntegerField(default=1000)

    @property
    def visible_name(self):
        return self.callname or self.username

    def __str__(self):
        return f"{self.platform} ({self.username})"
    
    class Meta:
        unique_together = ('chatbot', 'platform', 'username')

class SimpleCommands(models.Model):
    chatbot = models.ForeignKey(ChatBot, on_delete=models.CASCADE)
    command = models.CharField(max_length=100,unique=True)
    response = models.TextField()

    def __str__(self):
        return f"{self.command} -> {self.response}"
    
class ChatLog(models.Model):
    chatbot = models.ForeignKey(ChatBot, on_delete=models.CASCADE)
    platform = models.CharField(max_length=200)
    chatuser = models.ForeignKey(ChatUser, on_delete=models.CASCADE , blank=True, null=True)    
    sender = models.CharField(max_length=200)
    message = models.TextField()
    response = models.TextField(blank=True, null=True)
    context = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.sender} ({self.created_at}/{self.platform})"
    
    class Meta:
        ordering = ['-created_at']
