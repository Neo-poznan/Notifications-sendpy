from django.http import HttpResponseForbidden

from .models import SmtpCredentials, Message

class SmtpPasswordRequiredMixin:
    '''
    Класс примесь для проверки наличия пароля приложений у пользователя
    '''
    def dispatch(self, request, *args, **kwargs):
        if not SmtpCredentials.objects.filter(user_id=self.request.user):
            return HttpResponseForbidden("<h1>403 Forbidden</h1><br><p>Обязательно нужно указать пароль smtp.</p>")
        return super().dispatch(request, *args, **kwargs)


class MessageRequiredMixin:
    '''
    Класс примесь для проверки наличия сообщения у пользователя
    '''
    def dispatch(self, request, *args, **kwargs):
        if not Message.objects.filter(user=self.request.user):
            return HttpResponseForbidden("<h1>403 Forbidden</h1><br><p>Обязательно нужно создать сообщение.</p>")
        return super().dispatch(request, *args, **kwargs)
    
