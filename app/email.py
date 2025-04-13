import smtplib
import os

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader

from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv(override=True) 

env = Environment(loader=FileSystemLoader("templates/emails"))

def render_template(template_name: str, **context) -> str:
    template = env.get_template(template_name)
    return template.render(**context)

def send_email(to: str, subject: str, body: str, html: bool = False) -> None:

    # Выгружаем SMTP-данные
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = os.getenv("SMTP_PORT")
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")

    # Настройка письма
    msg = MIMEMultipart("alternative")  # поддерживает и plain, и html
    msg['From'] = smtp_user
    msg['To'] = to
    msg['Subject'] = subject

    # Добавляем текст письма
    if html:
        html_body = MIMEText(body, "html")
        msg.attach(html_body)
    else:
        plain_body = MIMEText(body, "plain")
        msg.attach(plain_body)

    try:
        # Подключаемся к SMTP-серверу
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:  # Используем SSL для порт 465
            server.login(smtp_user, smtp_password)  # Логинимся на сервер
            server.sendmail(smtp_user, to, msg.as_string())  # Отправляем письмо

        print("Email sent successfully")
    except Exception as e:
        print(f"Error sending email: {e}")