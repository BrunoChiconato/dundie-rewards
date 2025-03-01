"""Email utilities."""

import re
import smtplib
from email.mime.text import MIMEText

from dundie.settings import SMTP_HOST, SMTP_PORT, SMTP_TIMEOUT
from dundie.utils.log import get_logger

log = get_logger()

regex = r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b"


def check_valid_email(address: str) -> bool:
    """Check if email is valid.

    Args:
        address (str): Email address.

    Returns:
        bool: True or False if the emails is a valid one.
    """
    return bool(re.fullmatch(regex, address))


# TODO: One day I will get this to work
def send_email(from_, to, subject, text) -> None:
    """Sends an email.

    Args:
        from_ (str): Sender email.
        to (str or list): Receiver email.
        subject (str): Email subject.
        text (str): Email text.

    Returns:
        None
    """
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
