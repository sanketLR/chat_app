from channels.generic.websocket import AsyncWebsocketConsumer
import json
import websockets
import asyncio
from . models import *
from channels.db import database_sync_to_async
from django.db import transaction

class TradeConsumer(AsyncWebsocketConsumer):
    
    async def connect_to_websocket(self, uris):
        print("➡ self :", self)
        
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
        print("➡ uri_lst :", uri_lst)
        
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
            await asyncio.sleep(4)

    @database_sync_to_async
    def saveTrade(self, data):

        json_data1 = json.loads(data)
        get_trade_name = json_data1["s"]
        # json_data2 = json.loads(data2)

        # print("➡ json_data:", json_data)
        # print("➡ json_data type:", type(json_data))
        
        if json_data1:
            TradeData.objects.create(tradeJson=json_data1, tradeName = get_trade_name)

        # if json_data2:
        #     TradeData.objects.create(tradeJson=json_data1, tradeName = "ethusdt")

    async def disconnect(self, event):
        self.close()

    