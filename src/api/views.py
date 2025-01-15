import json

from django.views.generic import View
from django.http import request, response, HttpResponseBadRequest, JsonResponse

from notifications_manager.use_case import distribute_contact_list_message_and_authentication_data_to_partitions

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
        try:
            body_unicode = request.body.decode('utf-8')
            body_data = json.loads(body_unicode)
        except Exception as e:
            return HttpResponseBadRequest('Вам нужно передать тело запроса в формате json')
        try:
            message = body_data['message']
            message_subject = body_data['message_subject']
            recipient_email_list = body_data['recipient_email_list']
            sender_email = body_data['sender_email']
            smtp_password = body_data['smtp_password']
            smtp_server_host = body_data['server_host']
            smtp_server_port = body_data['server_port']
            distribute_contact_list_message_and_authentication_data_to_partitions(body_data['recipient_email_list'],
            body_data['message'], body_data['message_subject'], body_data['sender_email'], body_data['smtp_password'],
            body_data['server_host'], body_data['server_port'])
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return HttpResponseBadRequest('Вам нужно передать пары, указанные в документации')

