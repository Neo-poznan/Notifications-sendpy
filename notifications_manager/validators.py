import csv
import re
from typing import Never

from django.core.exceptions import ValidationError


def csv_file_validator(file: bytes) -> Never:
    '''
    Проверка на то чтобы файл можно было читать как CSV
    '''
    try:
        file_data = file.decode('utf-8').splitlines()
        csv_reader = csv.reader(file_data)
    except Exception as e:
        raise ValidationError('You need to upload a csv file.')
    

def csv_file_content_validator(file: bytes) -> Never:
    '''
    Проверка содержимого CSV-файла
    Проверяем чтобы была одна колонка
    Проверяем чтобы в колонке был email 
    '''
    file_data = file.decode('utf-8').splitlines()
    csv_reader = csv.reader(file_data)
    for row in csv_reader:
        if len(row) != 1:
            raise ValidationError('Required 1 column')       
    for row in csv_reader:
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', row[0]):
            raise ValidationError('Invalid email format')
            
