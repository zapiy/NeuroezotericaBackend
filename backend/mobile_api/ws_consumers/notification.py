from typing import Dict, Optional

import logging
from web import CustomAsyncJsonWebsocketConsumer
from enum import Enum
from ..events import AppActions
from ..models import MobileSessionModel, MobileServicePurchaseMessage, MobileUserModel, MobileClientServicePurchase


class NotificationType(Enum):    
    NEED_REFRESH = "need_refresh"
    CHAT_CHAGED = "chat_changed"
    NEW_MESSAGE = "new_message"
    
    START_CALL = "start_call"
    END_CALL = "end_call"


def typed_response(type: NotificationType, data: Optional[dict] = None):
    return { "type": type, "data": data }

logger = logging.getLogger("notification_ws")
logger.setLevel(logging.DEBUG)

USERS: Dict[str, "NotificationConsumer"] = {}


class NotificationConsumer(CustomAsyncJsonWebsocketConsumer):    
    async def connect(self):
        print("Channel layer type", type(self.channel_layer))
        self.session: MobileSessionModel = self.scope["session"]
        self.user: MobileUserModel = self.session.user
        await self.accept()
        USERS[self.session.user.uuid] = self
        AppActions.on_new_message += self.on_new_message
    
    async def disconnect(self, code):
        try:
            del USERS[self.session.user.uuid]
            AppActions.on_new_message -= self.on_new_message
        except KeyError:
            pass
    
    async def get_chat_by_id(self, chat_id: int):
        if chat_id is None or chat_id < 1:
            return None
        
        try:
            if self.user.role == MobileUserModel.Role.EXPERT:
                return await MobileClientServicePurchase.objects.aget(
                    uuid = chat_id,
                    service__owner_id = self.user.uuid,
                    status = MobileClientServicePurchase.Status.PAID,
                )
            elif self.user.role == MobileUserModel.Role.CLIENT:
                return await MobileClientServicePurchase.objects.aget(
                    uuid = chat_id,
                    client = self.user.uuid,
                    status = MobileClientServicePurchase.Status.PAID,
                )
        except MobileClientServicePurchase.DoesNotExist:
            return None
        
    async def has_permit_chat(self, chat: MobileClientServicePurchase):
        pass
    
    async def receive_json(self, content: dict, **kwargs):
        logger.info(f'{content["type"]} => {content["data"]}')
        if content["type"] == NotificationType.START_CALL.value:
            if self.user.role == MobileUserModel.Role.EXPERT:
                chat = await self.get_chat_by_id(content["data"]["chat_id"])
                if chat is not None:
                    peer = USERS.get(chat.client_id, None)
                    if peer is None:
                        await self.send_json({
                            "type": NotificationType.END_CALL.value
                        })
                    else:                        
                        await peer.send_json({
                            "type": NotificationType.START_CALL.value, 
                            "data": content["data"]
                        })
                    
            elif self.user.role == MobileUserModel.Role.CLIENT:
                chat = await self.get_chat_by_id(content["data"]["chat_id"])
                if chat is not None:
                    peer = USERS.get(chat.service.owner_id, None)
                    if peer is None:
                        await self.send_json({
                            "type": NotificationType.END_CALL.value
                        })
                    else:                        
                        await peer.send_json({
                            "type": NotificationType.START_CALL.value, 
                            "data": content["data"]
                        })
                    
        elif content["type"] == NotificationType.END_CALL:
            self.is_calling = False
    
    async def on_new_message(self, message: MobileServicePurchaseMessage):
        if (
            self.session.user.role == MobileUserModel.Role.CLIENT
            and message.purchase.client == self.session.user.client_extra
        ):
            await self.send_json(typed_response(
                NotificationType.NEW_MESSAGE, {
                    "chat_id": message.purchase.uuid,
                }
            ))
        elif (
            self.session.user.role == MobileUserModel.Role.EXPERT
            and message.purchase.service.owner == self.session.user.expert_extra
        ):
            await self.send_json(typed_response(
                NotificationType.NEW_MESSAGE, {
                    "chat_id": message.purchase.uuid,
                }
            ))
