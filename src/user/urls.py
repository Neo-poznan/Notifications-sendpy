from django.urls import path
from . import views

app_name = "user"

urlpatterns = [
    path('registration/', views.RegistrationView.as_view(), name='registration'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('update/', views.UserUpdateView.as_view(), name='update'),
    path('change-password/', views.UserPasswordChangeView.as_view(), name='change_password'),
    path('change-password-done/', views.UserPasswordChangeDoneView.as_view(), name='change_password_done'),
]

