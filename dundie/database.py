import warnings

from sqlalchemy.exc import SAWarning  # type: ignore
from sqlmodel import Session, create_engine  # type: ignore
from sqlmodel.sql.expression import Select, SelectOfScalar  # type: ignore

from dundie import models
from dundie.settings import SQL_CON_STRING

SelectOfScalar.inherit_cache = True  # type: ignore
Select.inherit_cache = True  # type: ignore

warnings.filterwarnings("ignore", category=SAWarning)

engine = create_engine(SQL_CON_STRING, echo=False)
models.SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    return Session(engine)
