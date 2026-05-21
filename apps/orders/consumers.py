import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

class OrderConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        user = self.scope['user']
        if not user.is_authenticated:
            await self.close()
            return
        self.group_name = f'user_{user.id}_orders'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.send(text_data=json.dumps({'message': 'Connected to order updates'}))
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        await self.send(text_data=json.dumps({'message': 'Disconnected from order updates'}))
        
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        if message_type == 'ping':
            await self.send(text_data=json.dumps({'type': 'pong'}))
            
    async def order_status_update(self, event):
        
        await self.send(text_data=json.dumps({
            'type': 'order_status_update',
            'order_number': event['order_number'],
            'new_status': event['new_status'],
            'message':event['message'],
            'timestamp': event['timestamp']
        }))        
        
    