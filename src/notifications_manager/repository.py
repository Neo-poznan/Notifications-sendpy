import csv
import smtplib
import json
import logging
from abc import ABC, abstractmethod
from typing import Optional
from datetime import datetime


from aiokafka import AIOKafkaProducer

from .models import RecipientContact, Message, SmtpCredentials
from user.models import User
from config.settings import TOPIC, KAFKA_HOST_AND_PORT

logger = logging.getLogger('django.request')


class RecipientContactsRepositoryInterface(ABC):
    @abstractmethod
    def add_recipient_contacts_from_csv(self, csv_file: bytes, user: User) -> None:
        pass

    @abstractmethod
    def get_user_contacts(self, user: User) -> list:
        pass

    @abstractmethod
    def delete_user_contacts(self, user: User) -> None:
        pass


class MessageRepositoryInterface(ABC):
    @abstractmethod
    def create_or_update_user_message(self, user: User, ) -> None:
        pass

    @abstractmethod
    def get_user_message(self, user: User) -> Optional[Message]:
        pass


class SmtpCredentialsRepositoryInterface(ABC):
    @abstractmethod
    def create_object_with_user_email_and_password(self, user: User, app_password: str) -> None:
        pass

    @abstractmethod
    def set_smtp_host_and_port(self, use: User, server_host: str, server_port: str) -> None:
        pass

    @abstractmethod
    def get_user_smtp_password(self, user: User) -> Optional[str]:
        pass

    @abstractmethod
    def get_user_smtp_credentials(self, user: User) -> Optional[SmtpCredentials]:
        pass


class SmtpConnectionRepositoryInterface(ABC):
    @abstractmethod
    def smtp_login_test(self, email: str, smtp_password: str) -> None:
        pass


class RecipientContactsRepository(RecipientContactsRepositoryInterface):
    def __init__(self):
        self._model = RecipientContact

    def add_recipient_contacts_from_csv(self, csv_file: bytes, user: User) -> None:
        'Добавим только те контакты, которых еще нет у пользователя'
        file_data = csv_file.decode('utf-8').splitlines()
        csv_reader = csv.reader(file_data)

        for row in csv_reader:
            try:
                self._model.objects.create(contact=row[0], user=user)
            except Exception as e:
                pass
    
    def get_user_contacts(self, user: User) -> list:
        contacts = self._model.objects.filter(user=user).only('contact').values_list('contact', flat=True)
        return contacts
    
    def delete_user_contacts(self, user: User) -> None:
        self._model.objects.filter(user=user).delete()


class MessageRepository(MessageRepositoryInterface):
    def __init__(self):
        self._model = Message

    def create_or_update_user_message(self, user: User, message: str, message_subject: str) -> None:
        message_object = self._model.objects.filter(user=user).first()
        if not message_object:
            self._model.objects.create(message=message, subject=message_subject, user=user)
        else:
            message_object.message = message
            message_object.subject = message_subject
            message_object.save()

    def get_user_message(self, user: User) -> Optional[Message]:
        return self._model.objects.filter(user=user).first()
    
    
class SmtpCredentialsRepository(SmtpCredentialsRepositoryInterface):
    def __init__(self):
        self._model = SmtpCredentials

    def create_object_with_user_email_and_password(self, user: User, smtp_password: str) -> None:
        self._model.objects.create(user=user, smtp_password=smtp_password, email=user.email)

    def set_smtp_host_and_port(self, user: User, server_host: str, server_port: str) -> None:
        smtp_data_row = self._model.objects.get(user=user)
        smtp_data_row.smtp_server_host = server_host
        smtp_data_row.smtp_server_port = server_port
        smtp_data_row.save()

    def get_user_smtp_password(self, user: User) -> Optional[str]:
        smtp_credentials_object = self._model.objects.filter(user=user).first()
        return smtp_credentials_object.smtp_password if smtp_credentials_object else None
    
    def get_user_smtp_credentials(self, user: User) -> Optional[SmtpCredentials]:
        smtp_credentials_object = self._model.objects.filter(user=user).first()
        return smtp_credentials_object


class SmtpConnectionRepository(SmtpConnectionRepositoryInterface):
    def __init__(self, smtp_server_host: str, smtp_server_port: str):
        self._model = SmtpCredentials
        self.smtp_connection_object = smtplib.SMTP(smtp_server_host, smtp_server_port)

    def smtp_login_test(self, email: str, smtp_password: str) -> None:
        self.smtp_connection_object.starttls()
        self.smtp_connection_object.login(email, smtp_password)
        self.smtp_connection_object.quit()
        

async def send_contact_list_part_message_and_authentication_data_to_partition(contacts_list_for_one_partition: list[str],
        partition: int, message_content: str, message_subject: str, sender_email: str, smtp_password: str, 
        server_host: str, server_port: str
    ) -> None:
    '''
    Отправка списка контактов, сообщения и данных аутентификации 
    в определенную партицию. Создаем Producer
    и отправляем сообщение для каждого контакта
    '''
    try:
        producer = AIOKafkaProducer(bootstrap_servers=KAFKA_HOST_AND_PORT)
    except Exception as e:
        logging.error(f'{[datetime.now()]}Error creating Kafka producer: {e}')

    for contact in contacts_list_for_one_partition:
        print(contact, partition, message_content)
        data = {'contact': contact, 'message': message_content, 'message_subject': message_subject,
            'sender': sender_email, 'app_password': smtp_password, 'server_host': server_host, 'server_port': server_port}
        try:
            await producer.start()
            await producer.send_and_wait(TOPIC, value=json.dumps(data), partition=partition)
        except Exception as e:
            logging.error(f'{[datetime.now()]}Error sending message to Kafka: {e}')
        finally:
            await producer.stop()

