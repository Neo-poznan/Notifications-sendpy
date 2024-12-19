from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView
from django.db.models.base import Model as Model
from django.views.generic import CreateView, UpdateView
from django.urls import reverse_lazy

from .forms import RegistrationForm, LoginForm, UserUpdateForm, UserPasswordChangeForm


class RegistrationVIew(CreateView):
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

    def get_object(self) -> Model:
        return self.request.user
    

class UserPasswordChangeView(PasswordChangeView):
    template_name = 'user/change_password.html'
    form_class = UserPasswordChangeForm


class UserPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = 'user/password_change_done.html'
    
