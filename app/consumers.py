import json
from channels.generic.websocket import AsyncWebsocketConsumer, SyncConsumer, AsyncConsumer
from channels.consumer import SyncConsumer
from asgiref.sync import sync_to_async
from channels.exceptions import StopConsumer
import websockets
from . models import Message,Chat_Room
from django.contrib.auth.models import User
import asyncio
from . models import *
from channels.db import database_sync_to_async


class MySyncConsumer(SyncConsumer):

    def websocket_conntect(self, event):
        print("Websocket connected", event)
        self.send({
            "type" : "websocket.accept"
        })

    def websocket_receive(self, event):
        print("Message received from client", event)
        print(event['text'])
        self.send({
            "type" : "websocket.send",
            "text" : "Message sent to the client"
        })

    def websocket_disconnect(self, event):
        print("websocket disconnected",event)
        raise StopConsumer()
    
class MyAsyncConsumer(AsyncConsumer):
    
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



class TradeConsumer(AsyncWebsocketConsumer):
    
    async def connect_to_websocket(self, uris):
        connections = []

        for uri in uris:
            connection = await websockets.connect(uri)
            connections.append(connection)

        return connections

    async def connect(self):

        await self.accept()

        await self.channel_layer.group_add(
            "trade_data_group",
            self.channel_name
        )

        uri_lst = [
            "wss://stream.binance.com:9443/ws/btcusdt@trade",
            "wss://stream.binance.com:9443/ws/ethusdt@trade",
            "wss://stream.binance.com:9443/ws/mtcusdt@trade", #
            "wss://stream.binance.com:9443/ws/dotusdt@trade",
            "wss://stream.binance.com:9443/ws/adausdt@trade",
            "wss://stream.binance.com:9443/ws/ethbtc@trade",
            "wss://stream.binance.com:9443/ws/axsbtc@trade"
        ]
        
        connections = await self.connect_to_websocket(uri_lst)
        tasks = [self.receive_data(connection) for connection in connections]
        print("➡ tasks :", tasks)
        await asyncio.gather(*tasks)

    async def receive_data(self, connection):
        while True:
            try:
                response = await connection.recv()
                await self.saveTrade(response)
                await self.send(response)
            except websockets.ConnectionClosed:
                # Handle connection closed if needed
                break
            await asyncio.sleep(2)


    @database_sync_to_async
    def saveTrade(self, data1):

        json_data1 = json.loads(data1)
        get_trade_name = json_data1["s"]
        # json_data2 = json.loads(data2)

        # print("➡ json_data:", json_data)
        # print("➡ json_data type:", type(json_data))
        
        if json_data1:
            TradeData.objects.create(tradeJson=json_data1, tradeName = get_trade_name)

        # if json_data2:
        #     TradeData.objects.create(tradeJson=json_data1, tradeName = "ethusdt")

    async def disconnect(self, event):
        await self.close()

# class TradeConsumer(AsyncWebsocketConsumer):

#     async def connect(self):
#         await self.accept()

#         uri = "wss://stream.binance.com:9443/ws/btcusdt@trade"
        
#         async with websockets.connect(uri) as binance_ws:

#             while True:

#                 response = await binance_ws.recv()

#                 await self.save_trade(response)

#                 await self.send(response)

#                 await asyncio.sleep(2)

#     @sync_to_async
#     def save_trade(self, data):
#         json_data = json.loads(data)
#         if json_data:
#             TradeData.objects.create(tradeJson=json_data)
        
        
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
