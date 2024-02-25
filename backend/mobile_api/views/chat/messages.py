from django.http import HttpRequest
from django.db.models import Q
from django.conf import settings
from adrf.views import APIView

from pyqumit import safe_get
from web import CustomJsonResponse, process_image, wrap_filters
from mobile_api.events import AppActions
from mobile_api.authentication import MobileAuthentication, IsAuthenticated
from mobile_api.utils import typed_response, ResponseType
from mobile_api.models import MobileUserModel, MobileClientServicePurchase, MobileServicePurchaseMessage
from mobile_api.serializers import MessageSerializer


class MessagesView(APIView):
    
    authentication_classes = [MobileAuthentication]
    permission_classes = [IsAuthenticated]

    async def post(request: HttpRequest, uuid: str):
        user: MobileUserModel = request._user
        
        try:
            chat = await MobileClientServicePurchase.objects.aget(
                Q(status = MobileClientServicePurchase.Status.PAID)
                | Q(status = MobileClientServicePurchase.Status.ACTIVE),
                uuid = uuid,
                service__telegram_link__isnull= True,
            )
        except MobileClientServicePurchase.DoesNotExist:
            return typed_response(ResponseType.INVALID_FIELDS, status=404)
        
        if user.selected_role == user.Role.CLIENT and chat.client_id != user.client_extra_id:
            return typed_response(ResponseType.RESTRICT)
        elif user.selected_role == user.Role.EXPERT and chat.service.owner_id != user.expert_extra_id:
            return typed_response(ResponseType.RESTRICT)
        
        message_type = safe_get(request.POST, "type", MobileServicePurchaseMessage.Type)
        
        if message_type == MobileServicePurchaseMessage.Type.TEXT:
            content = safe_get(request.POST, "content", lambda v: str(v).strip(), validate=lambda v: len(v) in range(1, 1500))
            
            if content is not None:
                await AppActions.send_message(user, chat, MobileServicePurchaseMessage.Type.TEXT, content)
                return typed_response(ResponseType.OKAY)

        elif message_type == MobileServicePurchaseMessage.Type.IMAGE:
            try:
                img_id = process_image(
                    request.FILES["image"].file,
                    settings.BASE_DIR / f"media/message_images",
                    max_dimention=800
                )
                
                await AppActions.send_message(user, chat, MobileServicePurchaseMessage.Type.IMAGE, img_id)
                return typed_response(ResponseType.OKAY)
            except:
                return typed_response(ResponseType.INVALID_FIELDS)
            
        return typed_response(ResponseType.INVALID_FIELDS)


    async def get(request: HttpRequest, uuid: str):
        try:
            chat = await MobileClientServicePurchase.objects.aget(
                Q(status = MobileClientServicePurchase.Status.ACTIVE)
                | Q(status = MobileClientServicePurchase.Status.ARCHIVED),
                uuid = uuid,
                service__telegram_link__isnull = True,
            )
        except MobileClientServicePurchase.DoesNotExist:
            return typed_response(ResponseType.INVALID_FIELDS, status=404)
        
        user: MobileUserModel = request._user
        if user.selected_role == MobileUserModel.Role.CLIENT:
            if chat.client != user.client_extra:
                return typed_response(ResponseType.RESTRICT)
            
        elif user.selected_role == MobileUserModel.Role.EXPERT:
            if chat.service.owner != user.expert_extra:
                return typed_response(ResponseType.RESTRICT)
        else:
            return typed_response(ResponseType.RESTRICT)
        
        return CustomJsonResponse(MessageSerializer(
            many=True,
            instance = await wrap_filters(
                request, (
                    MobileServicePurchaseMessage.objects
                        .filter(purchase = chat)
                        .order_by("-created_at")
                ),
                paginate=True
            )
        ).data)
