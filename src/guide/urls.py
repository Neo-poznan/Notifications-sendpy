from django.urls import path
from . import views

app_name = 'guide'

urlpatterns = [
    path('smtp/',views.SmtpGuideView.as_view(), name='smtp'),
    path('mail/', views.MailGuideView.as_view(), name='mail'),
    path('quick-start/', views.QuickStartGuideView.as_view(), name='quick_start'),
]

