import smtplib
import os

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from dotenv import load_dotenv

load_dotenv()

def send_email(to: str, subject: str, body: str) -> None:

    # Выгружаем SMTP-данные из .env файла
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = os.getenv("SMTP_PORT")
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")

    # Настройка письма
    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = to
    msg['Subject'] = subject

    # Добавление текста сообщения
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Подключаемся к SMTP-серверу
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:  # Используем SSL для порт 465
            server.login(smtp_user, smtp_password)  # Логинимся на сервер
            server.sendmail(smtp_user, to, msg.as_string())  # Отправляем письмо

        print("Email sent successfully")
    except Exception as e:
        print(f"Error sending email: {e}")