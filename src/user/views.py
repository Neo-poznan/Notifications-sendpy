from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView
from django.db.models.base import Model as Model
from django.views.generic import CreateView, UpdateView
from django.urls import reverse_lazy

from .forms import RegistrationForm, LoginForm, UserUpdateForm, UserPasswordChangeForm
from .models import User
from notifications_manager.models import SmtpCredentials


class RegistrationView(CreateView):
    template_name = 'user/registration.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('user:login')


class LoginView(LoginView):
    template_name = 'user/login.html'
    form_class = LoginForm

    def get_success_url(self) -> str:
        return reverse_lazy('notifications_manager:set_recipient_list')
    

class LogoutView(LogoutView):
    
    def get_success_url(self) -> str:
        return reverse_lazy('user:login')
    

class UserUpdateView(UpdateView):
    template_name = 'user/user_update.html'
    form_class = UserUpdateForm
    success_url = reverse_lazy('user:update')

    def get_object(self) -> User:
        '''
        Перепишем метод get_object. По умолчанию этот метод возвращает 
        объект по id переданному в url, но нам нужен объект текущего пользователя
        '''
        return self.request.user
    
    def form_valid(self, form):
        '''
        Переопределим метод form_valid, чтобы в базу заносились изменения
        модели данных сервера, так как поле электронной почты в ней дублирует поле 
        в модели в конце вызываем метод родительского класса чтобы обновить поле
        в модели пользователя
        '''
        user = self.get_object()
        smtp_data_object = SmtpCredentials.objects.get(user_id=user)
        smtp_data_object.email = form.cleaned_data['email']
        smtp_data_object.save()
        return super().form_valid(form)
    

class UserPasswordChangeView(PasswordChangeView):
    template_name = 'user/change_password.html'
    form_class = UserPasswordChangeForm


class UserPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = 'user/password_change_done.html'
    
