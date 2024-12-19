import json

from django.views.generic import View
from django.http import request, response, HttpResponseBadRequest

from notifications_manager.kafka import distribute_contact_list_message_and_authentication_data_to_partitions

class SendMessageFromApiView(View):
    def get(request: request) -> response:
        '''
        Если тип запроса get то возвращаем ошибку
        '''
        return HttpResponseBadRequest()

    def post(request: request) -> response:
        '''
        Парсим тело запроса и отправляем на рассылку
        '''
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)
        try:
            message = body_data['message']
            message_header = body_data['message_header']
            recipient_email_list = body_data['recipient_email_list']
            sender_email = body_data['sender_email']
            app_password = body_data['app_password']
            distribute_contact_list_message_and_authentication_data_to_partitions(recipient_email_list,
                message, message_header, sender_email, app_password)
        except Exception as e:
            return HttpResponseBadRequest()

        