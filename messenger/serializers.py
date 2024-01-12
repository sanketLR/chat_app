from rest_framework import serializers
from django.contrib.auth.models import User
from . models import *

class UserCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model=User
        fields=['id','username', 'password']
      


class MessageSerializer(serializers.ModelSerializer):
    # Define a SerializerMethodField for the 'user' field
    user = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            "room",
            "user",
            "content",
            "date_added",
        ]

    # Define the method to get the 'username' for the 'user' field
    def get_user(self, obj):
        return obj.user.username
