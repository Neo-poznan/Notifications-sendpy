from django.urls import path
from . import views

app_name = "notifications_manager"

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('set-recipient-list/', views.SetRecipientListView.as_view(), name='set_recipient_list'),
    path('clear-contact-database/', views.clear_contact_database_view, name='clear_contact_database'),
    path('set-app-password/' , views.SetSmtpPasswordView.as_view(), name='set_smtp_password'),
    path('set-mail-server/',views.SetSmtpCredentialsView.as_view(), name='set_mail_server'),
    path('set-message/', views.SetMessageView.as_view(), name='set_message'),
    path('send-message/', views.SendMessageView.as_view(), name='send_message'),
]

