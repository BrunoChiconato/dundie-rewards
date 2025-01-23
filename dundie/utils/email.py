import re
import smtplib
from email.mime.text import MIMEText

from dundie.settings import SMTP_HOST, SMTP_PORT, SMTP_TIMEOUT
from dundie.utils.log import get_logger

log = get_logger()

regex = r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b"


def check_valid_email(adress):
    """Check if email is valid."""
    return bool(re.fullmatch(regex, adress))


def send_email(from_, to, subject, text):
    """Send email."""
    if not isinstance(to, list):
        to = [to]

    try:
        with smtplib.SMTP(
            host=SMTP_HOST, port=SMTP_PORT, timeout=SMTP_TIMEOUT
        ) as server:
            message = MIMEText(text)
            message["Subject"] = subject
            message["From"] = from_
            message["To"] = "".join(to)

            server.sendmail(from_, to, message.as_string())
    except Exception as e:
        log.error(f"Failed to send email: {e}")
