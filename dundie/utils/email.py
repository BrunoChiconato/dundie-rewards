"""Email utilities."""

import os
import re
import smtplib
from datetime import datetime
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


def create_pw_txt(email: str, plain_password: str) -> None:
    """Creates a .txt file with all the e-mails and plain passwords
    of the employees.

    Args:
        email (str): Employee email address.
        plain_password(str): Plain password generated at the moment that the
        employee is loaded to the database.

    Returns:
        None
    """
    txt_path = os.path.abspath("./passwords_txt.txt")

    if os.path.exists(txt_path):
        with open(txt_path, mode="a") as txt_file:
            txt_file.write(
                f"{datetime.now()} | Email: {email} | Password: {plain_password}\n"
            )
    else:
        with open(txt_path, mode="w") as txt_file:
            txt_file.write(
                f"{datetime.now()} | Email: {email} | Password: {plain_password}\n"
            )


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
