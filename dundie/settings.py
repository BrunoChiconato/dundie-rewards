"""Settings for the Dundie project."""

import os

ROOT_PATH: str = os.path.dirname(__file__)
DATABASE_PATH: str = os.path.join(ROOT_PATH, "..", "assets", "database.db")
SQL_CON_STRING = f"sqlite:///{DATABASE_PATH}"

DATEFMT: str = "%d/%m/%Y %H:%M:%S"
API_BASE_URL = "https://economia.awesomeapi.com.br/json/last/USD-{currency}"
