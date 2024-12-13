from django.urls import path
from . import views

app_name = "user"

urlpatterns = [
    path("registration/", views.RegistrationVIew.as_view(), name="registration"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
]

