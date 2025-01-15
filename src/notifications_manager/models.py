from django.db import models
from django.contrib.auth import get_user_model


class RecipientContact(models.Model):
    '''
    Контакты получателей сообщений. Используем тут композитный ключ
    чтобы у одного пользователя не было двух одинаковых контактов
    '''
    contact = models.EmailField(verbose_name='Электронная почта получателя')
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name='Пользователь, которому принадлежит список рассылки')

    class Meta:
        unique_together = (('contact', 'user'),)


class Message(models.Model):
    message = models.TextField(verbose_name='Сообщение')
    subject = models.CharField(verbose_name='Тема сообщения', max_length=150)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name='Пользователь, которому принадлежит сообщение')



class SmtpCredentials(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, primary_key=True,
        verbose_name='Пользователь, которому принадлежит строка данных с данными smtp')
    email = models.EmailField(verbose_name='Электронная почта пользователя. Она дублирует ту, что в модели User')
    smtp_password = models.CharField(max_length=50, verbose_name= 'Пароль с помощью которого будет осуществляться вход на smtp сервер')
    smtp_server_host = models.CharField(max_length=70, blank=True, null=True, verbose_name='Хост smtp сервера')
    smtp_server_port = models.CharField(max_length=5, blank=True, null=True, verbose_name='Порт smtp сервера')

    