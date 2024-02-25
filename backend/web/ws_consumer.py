from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import InMemoryChannelLayer, get_channel_layer
import orjson

from .json_encoder import custom_json_encoder


class CustomAsyncJsonWebsocketConsumer(AsyncWebsocketConsumer):
    """
    Variant of AsyncWebsocketConsumer that automatically JSON-encodes and decodes
    messages as they come in and go out. Expects everything to be text; will
    error on binary data.
    """
    channel_layer: InMemoryChannelLayer = get_channel_layer("default")
    
    async def receive(self, text_data=None, bytes_data=None, **kwargs):
        if bytes_data:
            await self.receive_json(await self.decode_json(bytes_data), **kwargs)
        else:
            raise ValueError("No bytes section for incoming WebSocket frame!")

    async def receive_json(self, content, **kwargs):
        pass

    async def send_json(self, content):
        await super().send(bytes_data=await self.encode_json(content))

    async def join_group(self, name: str):
        await self.channel_layer.group_add(name, self.channel_name)
        
    async def leave_group(self, name: str):
        await self.channel_layer.group_discard(name, self.channel_name)
    
    @classmethod
    async def decode_json(cls, buffer):
        return orjson.loads(buffer)

    @classmethod
    async def encode_json(cls, data):
        return orjson.dumps(data, default=custom_json_encoder, option=orjson.OPT_PASSTHROUGH_DATETIME)
