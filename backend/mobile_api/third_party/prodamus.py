from django.conf import settings
from aiohttp import ClientSession
from pyqumit import Singleton
import json

from ..models import MobileClientServicePurchase


class ProdamusAPI(Singleton):
    FORM_URL = settings.PRODAMUS_URL
    
    @classmethod
    async def create_link(cls, purchase: MobileClientServicePurchase):
        service_name = " ".join([
            purchase.service.owner.user.first_name, purchase.service.owner.user.last_name or "", "-",
            purchase.service.name, f"[{purchase.service.category.name}]"
        ])
        
        async with ClientSession() as session: 
            async with session.get(
                (cls.FORM_URL or "https://demo.payform.ru/"),
                params={
                    "do": "link",
                    "products": json.dumps([{
                        "name": service_name,
                        "price": purchase.price,
                        "quantity": 1,
                        "sku": purchase.service.uuid,
                    }]),
                    "order_sum": purchase.price,
                    "npd_income_type": "FROM_INDIVIDUAL",
                    "customer_phone": "+" + purchase.client.user.phone,
                    "installments_disabled": 1,
                    "type": "json",
                    "sys": "neuroezoterica_app",
                    "urlNotification": f"{settings.INTERNET_URL}/@/api/mobile/3party/prodamus/confirm/{purchase.confirm_hash}",
                    "demo_mode": 1, # FIXME
                }
            ) as resp:
                if resp.status == 200:
                    purchase.payment_link = (await resp.json())["payment_link"]
                    return True
        return False
