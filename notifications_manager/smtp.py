import smtplib
from typing import Never, Union


def smtp_login_test(email: str, password: str) -> Union[None, Never]:
    '''
    Создаем SMTP сервер и проверяем можно ли залогиниться на нем с данными пользователя
    '''
    server = smtplib.SMTP(host='smtp.gmail.com', port=587)
    server.starttls()
    server.login(email, password)

