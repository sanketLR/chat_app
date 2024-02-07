import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from channels.exceptions import StopConsumer
from messenger.models import Message,Chat_Room
from django.contrib.auth.models import User
import datetime
import base64
import os
import asyncio

#cryptography
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


class SimpleChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        '''
        Creaet a group and add channel into that group

        Fetch group name from the scop.

        Note :  
            In group (group name) space is not supported. Remove space or add '_' insted of space.
        '''

        self.room_name = self.scope['url_route']['kwargs']['name']

        if ' ' in self.room_name:
            self.room_name = self.room_name.replace(' ', '_')
        
        self.room_group_name = self.room_name

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        asyncio.create_task(self.send_ping())
        
    async def send_ping(self):
        while True:
            await asyncio.sleep(10)  # Send ping every 10 seconds
            await self.send(text_data=json.dumps({"pong": "pong"}))
            
        '''
        Receive data from the client side
        Broadcast the message into all channels through the related group
        

        text_data - string (need to convert into dict)
                  - Contains data dict as string formated

        ➡ text_data : {"msg":"ewr","user":"admin"}
        ➡ text_data : <class 'str'>

        "type" : "user_chat" 
            - Custom handler to perform some task

        '''
    async def receive(self, text_data):
        '''
        Receive data from the client side
        Broadcast the message into all channels through the related group
        '''

        client_msg = json.loads(text_data)

        if client_msg.get('action') == 'update_message':
            # Extract necessary data from the received message
            message_id = client_msg.get('message_id')
            print('➡ chat_app/messenger/consumers.py:77 message_id:', message_id)
            updated_content = client_msg.get('updated_content')
            print('➡ chat_app/messenger/consumers.py:79 updated_content:', updated_content)
            
            # Perform the update operation, for example, update the message content in the database
            # You need to implement this part based on your Django models
            try:
                encrypted_message_update = self.encrypt_message(updated_content)
                message_obj_content = self.update_message_content(message_id, encrypted_message_update)
                print('➡  message_obj_content:', message_obj_content)

                now_time = datetime.datetime.now()
                formatted_time = now_time.strftime("%d-%m-%Y %H:%M:%S")

                client_msg["message_id"] = message_id
                client_msg["updated_content"] = updated_content

                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type" : "user_update_chat",
                        "message" : client_msg,
                        "now_time" : formatted_time
                    }
                )      

            except Exception as e:
                # Handle any errors that may occur during the update operation
                print(f"Error updating message: {e}")
        else:
            now_time = datetime.datetime.now()
            formatted_time = now_time.strftime("%d-%m-%Y %H:%M:%S")
            
            if "ping" in client_msg:
                print("Msg from client", client_msg["ping"])
            else:
                message = client_msg["msg"]
                username = client_msg["user"]
                room = client_msg["room"]

                if message:
                    encrypted_message = self.encrypt_message(message)
                    message_obj = await self.save_chat_message(encrypted_message, username, formatted_time, room)
                    
                    client_msg["msg"] = encrypted_message
                    client_msg["msg_id"] = message_obj.id 

                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            "type" : "user_chat",
                            "message" : client_msg,
                            "now_time" : formatted_time
                        }
                    )

    async def user_update_chat(self, event):

        client_msg_time = event["now_time"]
        client_msg = event["message"] # [msg, msg_id, user, room]

        updated_content = client_msg["updated_content"]
        print('➡ chat_app/messenger/consumers.py:150 updated_content:', updated_content)

        decrypted_message = self.decrypt_message(updated_content)
        print('➡ chat_app/messenger/consumers.py:153 decrypted_message:', decrypted_message)

        message = decrypted_message if decrypted_message else "Decryption failed"

        decodedMessage = message
        print('➡ chat_app/messenger/consumers.py:158 decodedMessage:', decodedMessage)

        message_id = client_msg["message_id"]
        time = client_msg_time

        await self.send(text_data=json.dumps({
            "message": decodedMessage,
            "message_id": message_id,
            "now_time": time,
        }))
  

    async def user_chat(self, event):
        '''
        event - String from client (dict)
        
        - Save chat message
        - Send that message back to client
        '''

        client_msg_time = event["now_time"]
        client_msg = event["message"] # [msg, msg_id, user, room]

        decrypted_message = self.decrypt_message(client_msg["msg"])

        message = decrypted_message if decrypted_message else "Decryption failed"

        decodedMessage = message

        message_id = client_msg["msg_id"]
        username = client_msg["user"]
        room = client_msg["room"]
        time = client_msg_time

        await self.send(text_data=json.dumps({
            "message": decodedMessage,
            "message_id": message_id,
            "username": username,
            "now_time": time,
            "room": room
        }))


    @sync_to_async
    def save_chat_message(self, message, username, now_time, room):

        get_user = User.objects.filter(username = username).first()
        get_room = Chat_Room.objects.filter(cr_name = room).first()

        if get_user is not None:

            message_obj = Message.objects.create(
                room = get_room,
                user = get_user,
                content = message,
                date_added = now_time
            )
            return message_obj
        
    @sync_to_async
    def update_message_content(self, message_id, updated_content):
        print('➡ chat_app/messenger/consumers.py:179 updated_content:', updated_content)
        # Fetch the message object from the database using the message_id
        try:
            message_obj = Message.objects.get(pk=message_id)
            print('➡ chat_app/messenger/consumers.py:181 message_obj:', message_obj.content)
            # Update the message content with the new content


            message_obj.content = updated_content
            print('➡ chat_app/messenger/consumers.py:186 message_obj.content:', message_obj.content)
            # Save the updated message object
            message_obj.save()
            return message_obj.content
        except Message.DoesNotExist:
            print("Message does not exist.")
            return None
        except Exception as e:
            print(f"Error updating message: {e}")
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
