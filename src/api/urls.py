from django.urls import path
from . import views

app_name = "api"

urlpatterns = [
    path('send-message/', views.SendMessageFromApiView.as_view(), name='send_message'),
]

