from typing import Optional

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

from user.models import User


class EmailAuthenticationBackend(BaseBackend):
    '''
    Backend для аутентификации пользователя в системе по email.
    Это переписанный код django.contrib.auth.backends.ModelBackend,
    а именно его двух методов отвечающих за аутентификацию пользователя
    '''
    def authenticate(self, request, username: str = None, password: str = None, **kwargs) -> Optional[User]:
        '''
        Метод для аутентификации пользователя по email и паролю.
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

    def get_user(self, user_id: int) -> Optional[User]:
        '''
        Метод для получения пользователя по его id
        '''
        try:
            UserModel = get_user_model()
            user = UserModel.objects.get(pk=user_id)
            return user
        except UserModel.DoesNotExist:
            return None
        
