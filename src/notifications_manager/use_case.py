import asyncio
from asgiref.sync  import sync_to_async

from django.core.exceptions import ValidationError

from user.models import User
from .validators import csv_file_validator, csv_file_content_validator
from .repository import send_contact_list_part_message_and_authentication_data_to_partition
from .helpers import distribute_contact_list_to_partitions
from config.settings import PARTITIONS


class NotificationsManagerUseCase:
    def __init__(self, recipient_contact_repository,
                smtp_credentials_repository, message_repository,
                smtp_connection_repository,
                ):
        self._recipient_contact_repository = recipient_contact_repository
        self._smtp_credentials_repository = smtp_credentials_repository
        self._message_repository = message_repository
        self._smtp_connection_repository = smtp_connection_repository

    def set_recipient_contacts(self, contacts_file: bytes, user: User) -> str:
        try:
            csv_file_validator(contacts_file)
            csv_file_content_validator(contacts_file)
        except ValidationError as error:
             return error.message
        else:
            self._recipient_contact_repository.add_recipient_contacts_from_csv(contacts_file, user)
            return 'Контакты добавлены'

    def set_smtp_credentials(self, user: User, smtp_server_host: str, smtp_server_port: str) -> str:
        try:
            smtp_connection = self._smtp_connection_repository(smtp_server_host, smtp_server_port)
            smtp_connection.smtp_login_test(user.email, self._smtp_credentials_repository.get_user_smtp_password(user))
        except Exception as error:
            return 'Настройки SMTP не были сохранены. Проверьте введенные данные вашего почтового сервера и smtp пароля'
        else:
            self._smtp_credentials_repository.set_smtp_host_and_port(user, smtp_server_host, smtp_server_port)
            return 'Настройки SMTP сохранены'
        
    def  send_notifications(self, user: User) -> None:
        contacts_list = self._recipient_contact_repository.get_user_contacts(user)
        message_object = self._message_repository.get_user_message(user)
        smtp_credentials_object = self._smtp_credentials_repository.get_user_smtp_credentials(user)
        asyncio.run(distribute_contact_list_message_and_authentication_data_to_partitions(contacts_list=contacts_list, 
                message=message_object.message, message_subject=message_object.subject,
                sender_email=smtp_credentials_object.email,
                smtp_password=smtp_credentials_object.smtp_password,
                server_host=smtp_credentials_object.smtp_server_host, server_port=smtp_credentials_object.smtp_server_port))


async def distribute_contact_list_message_and_authentication_data_to_partitions(contacts_list: list[str], 
        message: str, message_subject: str, sender_email: str, smtp_password: str,
        server_host: str, server_port: str
    ) -> None:
    '''
    Разделяем список контактов на количество частей равное количеству партиций 
    и отправляем каждую часть в отдельном потоке чтобы ускорить отправку так как это IO-bound операция
    '''
    contacts_lists = await sync_to_async(distribute_contact_list_to_partitions)(contacts_list)
    for partition, contacts_list_part in zip(PARTITIONS, contacts_lists):
        asyncio.create_task(
        send_contact_list_part_message_and_authentication_data_to_partition(contacts_list_part, partition, 
        message, message_subject, sender_email, smtp_password, server_host, server_port
        ))

            