import os
import datetime


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
