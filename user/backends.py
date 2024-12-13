from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model


class EmailBackend(BaseBackend):
    '''
    Backend для аутентификации по email
    это переписанный код django.contrib.auth.backends.ModelBackend
    а именно его двух методов отвечающих за аутентификацию пользователя
    '''
    def authenticate(self, request, username=None, password=None, **kwargs):
        '''
        Метод для аутентификации пользователя по email и паролю.
        Получаем модель пользователя, получаем пользователя передавая в модель email 
        проверяем пароль и если все верно возвращаем пользователя
        '''
        try:
            UserModel = get_user_model()
            user = UserModel.objects.get(email=username)
            if user.check_password(password):
                return user
            else:
                return None
        except (UserModel.DoesNotExist, UserModel.MultipleObjectsReturned):
            return None

    def get_user(self, user_id):
        '''
        Метод для получения пользователя по его id
        '''
        try:
            UserModel = get_user_model()
            user = UserModel.objects.get(pk=user_id)
            return user
        except UserModel.DoesNotExist:
            return None
        
