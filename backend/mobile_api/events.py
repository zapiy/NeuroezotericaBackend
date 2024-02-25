from channels.layers import InMemoryChannelLayer, get_channel_layer

from .models import MobileUserModel, MobileServicePurchaseMessage, MobileClientServicePurchase
from pyqumit import SimpleEvent
import asyncio


class AppActions:
    channel_layer: InMemoryChannelLayer = get_channel_layer("default")
    
    on_new_message = SimpleEvent[MobileServicePurchaseMessage]()
    on_chat_state_changed = SimpleEvent[MobileClientServicePurchase]()
    
    @classmethod
    async def send_message(
        cls, user: MobileUserModel, chat: MobileClientServicePurchase, 
        type: MobileServicePurchaseMessage.Type,
        content: str = None
    ):
        await MobileServicePurchaseMessage(
            from_expert = (user.selected_role == MobileUserModel.Role.EXPERT),
            purchase = chat,
            type = type,
            content = content
        ).asave(force_insert = True)
        asyncio.create_task(
            cls.channel_layer.group_send(
                f"chat_{chat.uuid}", {
                    "type": "on_chat_message"
                }
            )
        )
