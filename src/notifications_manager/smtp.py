import smtplib


def smtp_login_test(email: str, password: str, smtp_server: smtplib.SMTP) -> None:
    '''
    
    '''
    smtp_server.starttls()
    smtp_server.login(email, password)
    smtp_server.quit()


def smtp_connection_test(host, port) -> smtplib.SMTP:
    return smtplib.SMTP(host=host, port=port)

