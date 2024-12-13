import json
import threading
import logging

from datetime import datetime

from more_itertools import divide
from confluent_kafka import Producer

from config.settings import PARTITIONS, TOPIC, KAFKA_HOST_AND_PORT

logger = logging.getLogger('django.request')


def delivery_report(err, msg):
    if err is not None:
        print(f'Ошибка доставки сообщения: {err}')
    else:
        print(f'Сообщение доставлено в {msg.topic()} [{msg.partition()}]')


def send_contact_list_part_message_and_authentication_data_to_partition(contacts_list_for_one_partition: list[str],
        partition: int, message_content: str, message_header: str, sender_email: str, app_password: str) -> None:
    '''
    Отправка списка контактов, сообщения и данных аутентификации 
    в определенную партицию. Создаем Producer
    и отправляем сообщение для каждого контакта
    '''
    conf = {
        'bootstrap.servers': KAFKA_HOST_AND_PORT
    }
    try:
        producer = Producer(conf)
    except Exception as e:
        logging.error(f'{[datetime.now()]}Error creating Kafka producer: {e}')

    for contact in contacts_list_for_one_partition:
        print(contact, partition, message_content)
        data = {'contact': contact, 'message': message_content, 'header': message_header,
            'sender': sender_email, 'app_password': app_password}
        try:
            producer.produce(TOPIC, value=json.dumps(data), partition=partition, callback=delivery_report)
            producer.flush()
        except Exception as e:
            logging.error(f'{[datetime.now()]}Error sending message to Kafka: {e}')


def distribute_contact_list_message_and_authentication_data_to_partitions(contacts_list: list[str], 
        message: str, message_header: str, sender_email: str, app_password: str) -> None:
    '''
    Разделяем список контактов на количество частей равное количеству партиций 
    и отправляем каждую часть в отдельном потоке чтобы ускорить отправку так как это IO-bound операция
    '''
    contacts_lists = [list(part) for part in divide(len(PARTITIONS), contacts_list)]
    for partition, contacts_list_part in zip(PARTITIONS, contacts_lists):
        thread = threading.Thread(target=send_contact_list_part_message_and_authentication_data_to_partition, 
            args=(contacts_list_part, partition, message, message_header, sender_email, app_password))
        thread.start()

