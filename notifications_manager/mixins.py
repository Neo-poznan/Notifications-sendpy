from django.http import HttpResponseForbidden

from .models import SmtpLoginAndServerData

class AppPasswordRequiredMixin:
    '''
    Класс примесь для проверки наличия пароля приложений у пользователя
    '''
    def dispatch(self, request, *args, **kwargs):
        if not SmtpLoginAndServerData.objects.filter(user_id=self.request.user):
            return HttpResponseForbidden("<h1>403 Forbidden</h1><br><p>Обязательно нужно указать пароль приложений</p>")
        return super().dispatch(request, *args, **kwargs)
    
