import smtplib
import logging

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader

from .settings import SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

env = Environment(loader=FileSystemLoader("templates/emails"))

def render_template(template_name: str, **context) -> str:
    template = env.get_template(template_name)
    return template.render(**context)

def send_email(to: str, subject: str, body: str, html: bool = False) -> None:
    # Настройка письма
    logger.debug("Настраиваем письмо")
    msg = MIMEMultipart("alternative")  # поддерживает и plain, и html
    msg['From'] = SMTP_USER
    msg['To'] = to
    msg['Subject'] = subject

    # Текст письма
    logger.debug("Добавляем текст письмо")
    if html:
        html_body = MIMEText(body, "html")
        msg.attach(html_body)
    else:
        plain_body = MIMEText(body, "plain")
        msg.attach(plain_body)

    try:
        # Подключение к SMTP-серверу
        logger.debug("Подключаемся к SMTP-серверу")
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:  # Используем SSL для порт 465
            server.login(SMTP_USER, SMTP_PASSWORD)  # Логинимся на сервер
            server.sendmail(SMTP_USER, to, msg.as_string())  # Отправляем письмо

        logger.debug("Письмо успешно отправлено на почту пользователя")
    except Exception as e:
        logger.debug(f"Ошибка при отправке письма: {e}")