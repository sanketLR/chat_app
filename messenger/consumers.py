import json
import datetime
import asyncio
import base64
import os
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.exceptions import StopConsumer
from django.contrib.auth.models import User
from messenger.models import Message, Chat_Room
from asgiref.sync import sync_to_async
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import logging

class SimpleChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['name'].replace(' ', '_')
        self.room_group_name = self.room_name

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        asyncio.create_task(self.send_ping())

    async def send_ping(self):
        while True:
            await asyncio.sleep(10)  # Send ping every 10 seconds
            await self.send(text_data=json.dumps({"pong": "pong"}))

    async def receive(self, text_data):
        client_msg = json.loads(text_data)
        
        if client_msg.get('action') == 'delete_message':
            message_id = client_msg.get('message_id')
            if message_id:
                await self.delete_message_content(message_id)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "user_delete_chat",
                        "message_id": message_id
                    }
                )

        elif client_msg.get('action') == 'update_message':
            message_id = client_msg.get('message_id')
            updated_content = client_msg.get('updated_content')
            if  updated_content  !=  "" or None:
                try:
                    encrypted_message_update = self.encrypt_message(updated_content)
                    message_obj_content = await self.update_message_content(message_id, encrypted_message_update)
                    
                    now_time = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
                    client_msg["message_id"] = message_id
                    client_msg["updated_content"] = encrypted_message_update

                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            "type": "user_update_chat",
                            "message": client_msg,
                            "now_time": now_time
                        }
                    )      

                except Exception as e:
                    logging.error(f"Error updating message: {e}")
            else:
                logging.exception("Empty message")
        else:
            now_time = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            
            if "ping" in client_msg:
                pass
            else:
                message = client_msg["msg"]
                username = client_msg["user"]
                room = client_msg["room"]

                if message:
                    encrypted_message = self.encrypt_message(message)
                    message_obj = await self.save_chat_message(encrypted_message, username, now_time, room)
                    
                    client_msg["msg"] = encrypted_message
                    client_msg["msg_id"] = message_obj.id 

                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            "type": "user_chat",
                            "message": client_msg,
                            "now_time": now_time
                        }
                    )

    async def user_delete_chat(self, event):
        message_id = event["message_id"]

        await self.send(text_data=json.dumps({
            'event': 'message_deleted',
            'message_id': message_id
        }))
        
    async def user_update_chat(self, event):
        client_msg_time = event["now_time"]
        client_msg = event["message"]

        updated_content = client_msg["updated_content"]
        decrypted_message = self.decrypt_message(updated_content)
        message = decrypted_message if decrypted_message else "Decryption failed"

        message_id = client_msg["message_id"]

        await self.send(text_data=json.dumps({
            'event': 'message_updated',
            "message": message,
            "message_id": message_id,
        }))
  
    async def user_chat(self, event):
        client_msg_time = event["now_time"]
        client_msg = event["message"]

        decrypted_message = self.decrypt_message(client_msg["msg"])
        message = decrypted_message if decrypted_message else "Decryption failed"
        message_id = client_msg["msg_id"]
        username = client_msg["user"]
        room = client_msg["room"]

        await self.send(text_data=json.dumps({
            "event": 'message_save',
            "message": message,
            "message_id": message_id,
            "username": username,
            "now_time": client_msg_time,
            "room": room
        }))


    @sync_to_async
    def save_chat_message(self, message, username, now_time, room):
        get_user = User.objects.filter(username=username).first()
        get_room = Chat_Room.objects.filter(cr_name=room).first()

        if get_user is not None:
            message_obj = Message.objects.create(
                room=get_room,
                user=get_user,
                content=message,
                date_added=now_time
            )
            return message_obj

    @sync_to_async
    def update_message_content(self, message_id, updated_content):
        try:
            message_obj = Message.objects.get(pk=message_id)
            message_obj.content = updated_content
            message_obj.save()
            return message_obj.content
        except Message.DoesNotExist:
            logging.exception("Message does not exist.")
            return None
        except Exception as e:
            print(f"Error updating message: {e}")
            return None
            
    @sync_to_async
    def delete_message_content(self, message_id):
        try:
            message_obj = Message.objects.get(pk=message_id)
            message_obj.delete()
            return "Deleted"
        except Message.DoesNotExist:
            logging.exception("Message does not exist.")
            return None
        except Exception as e:
            print(f"Error deleting message: {e}")
            return None
            
    def derive_key(self, password):

        salt = b'salt_salt_salt'
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), salt=salt, iterations=100000, length=32, backend=default_backend())
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))[:32] 
        return key


    def encrypt_message(self, message):

        password = os.getenv("MESSAGE_PASSWORD")
        key = self.derive_key(password)
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(message.encode()) + encryptor.finalize()
        encrypted_message = iv + ciphertext

        return base64.urlsafe_b64encode(encrypted_message).decode()
    

    def decrypt_message(self, encrypted_message):

        password = os.getenv("MESSAGE_PASSWORD")
        key = self.derive_key(password)
        data = base64.urlsafe_b64decode(encrypted_message)
        iv = data[:16]
        ciphertext = data[16:]
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_message = decryptor.update(ciphertext) + decryptor.finalize()

        return decrypted_message.decode("utf-8")
    

    async def disconnect(self,event):

        self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        raise StopConsumer()
