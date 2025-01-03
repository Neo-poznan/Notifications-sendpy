import csv
from django.db import models, connection

from user.models import User


class Recipient_contact(models.Model):
    '''Контакты получателей сообщений'''
    contact = models.EmailField(verbose_name='Электронная почта получателя')
    user = models.ForeignKey('user.User', on_delete=models.CASCADE, verbose_name='Пользователь, которому принадлежит список рассылки')

    @classmethod
    def parse_csv_and_add_contacts_to_database(self, contact_table_file: bytes, user: User) -> None:
        '''Добавление контактов в базу данных, добавляем только те контакты, которых еще не было'''
        file_data = contact_table_file.decode('utf-8').splitlines()
        csv_reader = csv.reader(file_data)

        cursor = connection.cursor()
        cursor.execute(f'''
            SELECT contact FROM notifications_manager_recipient_contact
                    where user_id = {user.id}
            ''')
        existing_contacts = cursor.fetchall()
        existing_contacts = [row[0] for row in existing_contacts]

        for row in csv_reader:
            print(row)
            if not row[0] in existing_contacts:
                self.objects.create(contact=row[0], user=user)
                print('добавилось', row[0])
    
    @classmethod
    def get_contacts_from_database(self, user: User) -> list:
        '''Получение контактов из базы данных'''
        cursor = connection.cursor()
        cursor.execute(f'''
            SELECT contact FROM notifications_manager_recipient_contact
                    where user_id = {user.id}
            ''')
        contacts = cursor.fetchall()
        contacts = [row[0] for row in contacts]
        return contacts


class Message(models.Model):
    message_layout = models.TextField(verbose_name='Сообщение')
    header = models.CharField(verbose_name='Заголовок', max_length=150)
    user = models.ForeignKey('user.User', on_delete=models.CASCADE, verbose_name='Пользователь, которому принадлежит сообщение')

    @classmethod
    def reset_user_message(self, message_layout: str,message_header: str , user: User) -> None:
        '''
        Когда пользователь сохраняет сообщение то удаляем старое если оно есть 
        и создаем новое
        '''
        self.objects.filter(user=user).delete()
        self.objects.create(message_layout=message_layout, header=message_header, user=user)


class SmtpLoginAndServerData(models.Model):
    user_id = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True,
        verbose_name='Пользователь, которому принадлежит строка данных с данными smtp')
    email = models.EmailField(verbose_name='Электронная почта пользователя. Она дублирует ту, что в модели User')
    app_password = models.CharField(max_length=50, 
        verbose_name= 'Пароль приложения с помощью которого будет осуществляться вход на smtp сервер')
    mail_server_host = models.CharField(max_length=70, blank=True, null=True, verbose_name='Хост smtp сервера')
    mail_server_port = models.CharField(max_length=5, blank=True, null=True, verbose_name='Порт smtp сервера')

    @classmethod
    def set_server_data(self, user, server_host, server_port):
        '''
        Заносим данные сервера в базу
        '''
        row = self.objects.get(user_id=user)
        row.mail_server_host=server_host
        row.mail_server_port=server_port
        row.save()

    