import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader
from aiosmtplib import SMTP, SMTPException

from .settings import SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

env = Environment(loader=FileSystemLoader("templates/emails"))

def render_template(template_name: str, **context) -> str:
    template = env.get_template(template_name)
    return template.render(**context)

async def send_email(to: str, subject: str, body: str, html: bool = False) -> None:
    logger.info("Настраиваем письмо")
    msg = MIMEMultipart("alternative")
    msg["From"] = SMTP_USER
    msg["To"] = to
    msg["Subject"] = subject

    if html:
        msg.attach(MIMEText(body, "html"))
    else:
        msg.attach(MIMEText(body, "plain"))

    try:
        logger.info("Подключаемся к SMTP-серверу")
        smtp = SMTP(
            hostname=SMTP_SERVER,
            port=SMTP_PORT,
            use_tls=True,
            timeout=10,
        )
        await smtp.connect()
        await smtp.login(SMTP_USER, SMTP_PASSWORD)

        logger.info("Отправляем письмо")
        await smtp.send_message(msg)
        await smtp.quit()
        logger.info("Письмо успешно отправлено!")
    except SMTPException as e:
        logger.error(f"Ошибка при отправке письма: {e}", exc_info=True)
    except Exception as e:
        logger.error(f"Неизвестная ошибка: {e}", exc_info=True)