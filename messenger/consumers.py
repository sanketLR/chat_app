import json
from channels.generic.websocket import AsyncWebsocketConsumer, AsyncConsumer
from asgiref.sync import sync_to_async
from channels.exceptions import StopConsumer
from messenger.models import Message,Chat_Room
from django.contrib.auth.models import User
import datetime


class SimpleChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        '''
        Creaet a group and add channel into that group

        Fetch group name from the scop.
        '''

        self.room_name = self.scope['url_route']['kwargs']['name']

        self.room_group_name = self.room_name

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        
    async def receive(self, text_data):
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

        client_msg = json.loads(text_data) 

        message = client_msg["msg"]
        username = client_msg["user"]
        room = client_msg["room"]
        now_time = datetime.datetime.now()
        formatted_time = now_time.strftime("%d-%m-%Y %H:%M:%S")

        if message:
            await self.save_chat_message(message, username, formatted_time, room)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type" : "user_chat",
                "message" : client_msg,
                "now_time" : formatted_time
            }
        )

    async def user_chat(self, event):
        '''
        event - String from client (dict)
        
        - Save chat message
        - Send that message back to client
        '''

        client_msg_time = event["now_time"]

        client_msg = event["message"] 

        message = client_msg["msg"]
        username = client_msg["user"]
        room = client_msg["room"]

        time = client_msg_time

        if message !=  "":
            
            await self.send(text_data=json.dumps({
                "message" : message,
                "username" : username,
                "now_time" : time,
                "room" : room
            }))

    @sync_to_async
    def save_chat_message(self, message, username, now_time, room):
        get_user = User.objects.filter(username = username).first()
        get_room = Chat_Room.objects.filter(cr_name = room).first()

        if get_user is not None:
            Message.objects.create(
                room = get_room,
                user = get_user,
                content = message,
                date_added = now_time
            )

    async def disconnect(self,event):
        self.channel_layer.group_discard(
            self.room_group_name,
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


    async def receive(self,text_data):

        data = json.loads(text_data)
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

        
    async def disconnect(self, event):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        raise StopConsumer()
    