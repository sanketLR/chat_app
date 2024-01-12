import json
from channels.generic.websocket import AsyncWebsocketConsumer, AsyncConsumer
from asgiref.sync import sync_to_async
from channels.exceptions import StopConsumer
from . models import Message,Chat_Room
from django.contrib.auth.models import User
from . models import *
import datetime
from typing import Dict, Any, Union
from typing import Union

class MySyncConsumer(AsyncConsumer):

    async def websocket_connect(self, event):
        print("Websocket connected", event)
        await self.send({
            "type" : "websocket.accept"
        })

    async def websocket_receive(self, event):
        print("Message received from client", event)
        print(event['text'])
        await self.send({
            "type" : "websocket.send",
            "text" : "Message sent to the client"
        })
    
    async def websocket_disconnect(self, event):
        print("Websocket disconnected", event)
        raise StopConsumer()


class SimpleChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        '''Creaet a group and add channel into that group'''

        await self.channel_layer.group_add(
            "python_chat",
            self.channel_name
        )

        await self.accept()
        
    async def receive(self, text_data):
        '''

        Receive data from the client side
        Broadcast the message into all channels through the related group

        text_data - string 
                  - Contains data dict as string formated

        ➡ text_data : {"msg":"ewr","user":"admin"}
        ➡ text_data : <class 'str'>

        "type" : "user_chat" 
            - Custom handler to perform some task

        '''
        
        await self.channel_layer.group_send(
            "python_chat",
            {
                "type" : "user_chat",
                "message" : text_data,
                
            }
        )

    async def user_chat(self, event):
        '''
        event - String from client (dict)
        
        - Save chat message
        - Send that message back to client
        '''
            
        client_msg = json.loads(event["message"]) 

        message = client_msg["msg"]
        username = client_msg["user"]
        now_time = str(datetime.datetime.now())
        if message !=  "":
            
            await self.save_chat_message(message, username, now_time)

            await self.send(text_data=json.dumps({
                "message" : message,
                "username" : username,
                "now_time" : now_time
            }))

    @sync_to_async
    def save_chat_message(self, message, username, now_time):

        get_user = User.objects.filter(username = username).first()
        get_room = Chat_Room.objects.filter(cr_name = "python_group").first()

        if get_user is not None:
            Message.objects.create(
                room = get_room,
                user = get_user,
                content = message,
                date_added = now_time
            )

    async def disconnect(self,event):
        self.channel_layer.group_discard(
            "python_group",
            self.channel_name
        )
        raise StopConsumer()


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        
    async def disconnect(self, event):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        raise StopConsumer()


    async def receive(self,text_data):
        print("berfor text data= ", type(text_data))
        print("berfor text data= ", text_data)

        data = json.loads(text_data)
        print("after text data",type(data))
        message = data['message']
        username = data['username']
        now_time = data['now_time']
        room = data['room']
        if message:
            await self.save_message(username, room,message ,now_time)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type':'chat_message',
                    'message':message,
                    'username':username,
                    'room':room,
                    'now_time':now_time,
                }
            )
        
            
    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        now_time = event['now_time']
        room = event['room']
        print("EVENT",event)
        if message != '':
            await self.send(text_data=json.dumps({
                'message':message,
                'username':username,
                'room':room,
                'now_time':now_time,
            }))

    
    @sync_to_async
    def save_message(self, username,room,message, now_time):
        user = None
        try:
            user = User.objects.get(username = username)
                                      
            room = Chat_Room.objects.get(cr_name = room)
            if message != '':
                Message.objects.create(user = user, room =room, content = message,date_added =now_time)
        except:
            user = User.objects.get(username = username)

            room = Chat_Room.objects.get(cr_name = room)
            if message != '':
                Message.objects.create(user= user,room =room, content = message,date_added =now_time)
