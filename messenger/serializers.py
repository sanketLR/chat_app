from rest_framework import serializers
from django.contrib.auth.models import User
from messenger.models import (
    Message,
    Chat_Room
)
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import base64
import os


class UserCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model=User
        fields=['id','username', 'password']
      

class MessageSerializer(serializers.ModelSerializer):

    user = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            "room",
            "user",
            "content",
            "date_added",
        ]

    def derive_key(self, password):

        salt = b'salt_salt_salt'

        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), salt=salt, iterations=100000, length=32, backend=default_backend())

        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))[:32]  # Truncate to 32 bytes (256 bits)

        return key
    
    def get_content(self, obj):
            
        password = os.getenv("MESSAGE_PASSWORD")

        key = self.derive_key(password)

        data = base64.urlsafe_b64decode(obj.content)
        
        iv = data[:16]

        ciphertext = data[16:]

        cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())

        decryptor = cipher.decryptor()

        decrypted_message = decryptor.update(ciphertext) + decryptor.finalize()

        return decrypted_message.decode("utf-8")

    def get_user(self, obj):
        return obj.user.username

class ChatRoomSerializer(serializers.ModelSerializer):

    class Meta:
        model = Chat_Room
        fields = [
            "cr_name",
            "cr_discription"
        ]

    def validate(self, data):
        cr_name = data.get('cr_name')
        cr_discription = data.get('cr_discription')

        if not cr_name:
            raise serializers.ValidationError("Room name cannot be empty.")

        if not cr_discription:
            raise serializers.ValidationError("Room description cannot be empty.")

        return data
    