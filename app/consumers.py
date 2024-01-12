import json
from channels.generic.websocket import AsyncWebsocketConsumer, SyncConsumer, AsyncConsumer
from channels.consumer import SyncConsumer
from asgiref.sync import sync_to_async
from channels.exceptions import StopConsumer
import websockets
from django.contrib.auth.models import User
import asyncio
from . models import *
from channels.db import database_sync_to_async


class MySyncConsumer(SyncConsumer):

    def websocket_conntect(self, event):
        print("Websocket connected", event)
        self.send({
            "type" : "websocket.accept",
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
        print("Websocket connected HAHAH", event)
        await self.send({
            "type" : "websocket.accept",
            "msg" : "nothing"
        })

    async def websocket_receive(self, event):
        print("Message received from client HAHHAHA", event)
        print(event['text'])
        await self.send({
            "type" : "websocket.send",
            "text" : "Message sent to the client"
        })
    
    async def websocket_disconnect(self, event):
        print("Websocket disconnected HAHHAHAH", event)
        raise StopConsumer()




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
        
  