from django.http import HttpResponseForbidden

class AppPasswordRequiredMixin:
    '''
    Класс примесь для проверки наличия пароля приложений у пользователя
    '''
    def dispatch(self, request, *args, **kwargs):
        if not request.user.app_password:
            return HttpResponseForbidden("<h1>403 Forbidden</h1><br><p>Обязательно нужно указать пароль приложений</p>")
        return super().dispatch(request, *args, **kwargs)
    
