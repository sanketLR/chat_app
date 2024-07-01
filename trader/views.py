from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class FlushRedisData(APIView):
    def post(self, request):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.flush)()
        return Response({'status': 'success', 'message': 'Redis data flushed successfully'}, status=status.HTTP_200_OK)
    
class RetrieveAllRedisData(APIView):
    def get(self, request, *args, **kwargs):
        channel_layer = get_channel_layer()
        
        # Get all keys
        keys = async_to_sync(channel_layer.group_layer.keys)()
        
        # Retrieve corresponding values
        data = async_to_sync(channel_layer.group_layer.mget)(keys)
        
        return Response({'data': dict(zip(keys, data))})
