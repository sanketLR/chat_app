from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Chat_Room(models.Model):
    cr_name = models.CharField(max_length=200, blank= True, null= True)
    cr_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.cr_name


class Message(models.Model):
    room = models.ForeignKey(Chat_Room,related_name='rooms',related_query_name="rooms", on_delete=models.CASCADE, null=True, blank = True)
    user = models.ForeignKey(User,related_name='users',related_query_name="users", on_delete=models.CASCADE,null=True)
    content = models.TextField()
    date_added = models.CharField(null=True,max_length=300)

    class Meta:
        ordering = ('date_added',)
    
    def __str__(self):
        return self.content + "  from -> " + self.user.username