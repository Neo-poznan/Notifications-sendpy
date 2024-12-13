from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView
from django.urls import reverse_lazy

from .forms import RegistrationForm, LoginForm


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
