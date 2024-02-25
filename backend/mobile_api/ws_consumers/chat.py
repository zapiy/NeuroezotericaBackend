import logging

from web import CustomAsyncJsonWebsocketConsumer
from mobile_api.events import AppActions
from mobile_api.models import (
    MobileSessionModel, MobileUserModel,
    MobileClientServicePurchase, MobileServicePurchaseMessage
)

logger = logging.getLogger("ws_chat_consumer")
logger.setLevel(logging.DEBUG)


class ChatConsumer(CustomAsyncJsonWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['id']
        self.session: MobileSessionModel = self.scope["session"]
        self.user: MobileUserModel = self.session.user
        
        try:
            try:
                if self.user.selected_role == MobileUserModel.Role.EXPERT:
                    self.chat = await MobileClientServicePurchase.objects.aget(
                        uuid = self.chat_id,
                        service__owner = self.user.uuid,
                        status = MobileClientServicePurchase.Status.ACTIVE,
                    )
                elif self.user.selected_role == MobileUserModel.Role.CLIENT:
                    self.chat = await MobileClientServicePurchase.objects.aget(
                        uuid = self.chat_id,
                        client_id = self.user.uuid,
                        status = MobileClientServicePurchase.Status.ACTIVE,
                    )
                    
                    await AppActions.send_message(self.user, self.chat, MobileServicePurchaseMessage.Type.JOIN)
                else:
                    await self.close(code=-1)
            except MobileClientServicePurchase.DoesNotExist:
                await self.close(code=-1)
            
        except MobileClientServicePurchase.DoesNotExist:
            await self.close(code=-1)
            return None
        
        await self.accept()
        
        self.group_name = f"chat_{self.chat_id}"
        
        logger.debug(f"[{self.group_name}] Joined => {self.user.phone}")
        await self.join_group(self.group_name)
        
    async def disconnect(self, code: int):
        await self.leave_group(self.group_name)
        await self.channel_layer.group_send(self.group_name, {
            "type": "on_end_call"
        })
        
        if self.user.role == MobileUserModel.Role.CLIENT:
            await AppActions.send_message(self.user, self.chat, MobileServicePurchaseMessage.Type.LEAVE)

    async def receive_json(self, content, **kwargs):
        if content["type"] == "start_call":
            logger.debug(f"[{self.group_name}] Received 'start_call'")
            await self.channel_layer.group_send(self.group_name, {
                "type": "on_start_call", 
                "data": content["data"]
            })
            
        elif content["type"] == "answer_call":
            logger.debug(f"[{self.group_name}] Received 'answer_call'")
            await self.channel_layer.group_send(self.group_name, {
                "type": "on_answer_call", 
                "data": content["data"]
            })
            
        elif content["type"] == "ice_candidate":
            logger.debug(f"[{self.group_name}] Received 'ice_candidate'")
            await self.channel_layer.group_send(self.group_name, {
                "type": "on_ice_candidate", 
                "data": content["data"]
            })
        
        elif content["type"] == "end_call":
            logger.debug(f"[{self.group_name}] Received 'end_call'")
            await AppActions.send_message(self.user, self.chat, MobileServicePurchaseMessage.Type.END_CALL)
            await self.channel_layer.group_send(self.group_name, {
                "type": "on_end_call"
            })
    
    async def on_chat_message(self, event):
        await self.send_json({ "type": "new_message" })
        
    async def on_start_call(self, event):
        await self.send_json({ "type": "start_call", "data": event["data"] })
        
    async def on_answer_call(self, event):
        await self.send_json({ "type": "answer_call", "data": event["data"] })
        
    async def on_ice_candidate(self, event):
        await self.send_json({ "type": "ice_candidate", "data": event["data"] })
        
    async def on_end_call(self, event):
        await self.send_json({ "type": "end_call" })
