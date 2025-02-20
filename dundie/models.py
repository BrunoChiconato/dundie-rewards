"""Models module."""

from datetime import datetime
from typing import List, Optional

from pydantic import condecimal, validator
from sqlmodel import Field, Relationship, SQLModel

from dundie.utils.email import check_valid_email
from dundie.utils.user import generate_simple_password


class InvalidEmailError(Exception):
    pass


class Person(SQLModel, table=True):
    """Person model.

    Attributes:
        id: Optional[int] - Person's ID.
        email: str - Person's email.
        name: str - Person's name.
        dept: str - Person's department.
        role: str - Person's role.
        currency: str - Person's currency.
        balance: List[Balance] - Person's balance.
        movement: List[Movement] - Person's movements.
        user: User - Person's user.

    Methods:
        validate_email(cls, v: str) -> str - Validates the email.
        __str__() -> str - Returns a string representation of the person.

    Raises:
        InvalidEmailError - Raised when the email is invalid.
    """

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    email: str = Field(nullable=False, index=True)
    name: str = Field(nullable=False)
    dept: str = Field(nullable=False, index=True)
    role: str = Field(nullable=False)
    currency: str = Field(default="USD")

    balance: List["Balance"] = Relationship(back_populates="person")
    movement: List["Movement"] = Relationship(back_populates="person")
    user: "User" = Relationship(back_populates="person")

    @property
    def superuser(self):
        return self.role == "Manager"

    @validator("email")
    def validate_email(cls, v: str) -> str:
        if not check_valid_email(v):
            raise InvalidEmailError(f"Invalid email: {v}")
        return v

    def __str__(self) -> str:
        return f"{self.name} - {self.role}"


class Balance(SQLModel, table=True):
    """Balance model.

    Attributes:
        id: Optional[int] - Balance's ID.
        person_id: int - Person's ID.
        value: condecimal - Balance's value.
        person: Person - Person's balance.

    Methods:
        None

    Raises:
        None
    """

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    person_id: int = Field(
        foreign_key="person.id", sa_column_kwargs={"unique": True}
    )
    value: condecimal(decimal_places=3) = Field(default=0)

    person: Person = Relationship(back_populates="balance")

    class Config:
        json_encoders = {Person: lambda p: p.pk}


class Movement(SQLModel, table=True):
    """Movement model.

    Attributes:
        id: Optional[int] - Movement's ID.
        person_id: int - Person's ID.
        actor: str - Movement's actor.
        value: condecimal - Movement's value.
        date: datetime - Movement's date.
        person: Person - Person's movement.

    Methods:
        None

    Raises:
        None
    """

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    person_id: int = Field(foreign_key="person.id")
    actor: str = Field(nullable=False, index=True)
    value: condecimal(decimal_places=3) = Field(default=0)
    date: datetime = Field(default_factory=lambda: datetime.now())

    person: Person = Relationship(back_populates="movement")

    class Config:
        json_encoders = {Person: lambda p: p.pk}


class User(SQLModel, table=True):
    """User model.

    Attributes:
        id: Optional[int] - User's ID.
        person_id: int - Person's ID.
        password: str - User's password.
        person: Person - Person's user.

    Methods:
        None

    Raises:
        None
    """

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    person_id: int = Field(
        foreign_key="person.id", sa_column_kwargs={"unique": True}
    )
    password: str = Field(default_factory=generate_simple_password)

    person: Person = Relationship(back_populates="user")

    class Config:
        json_encoders = {Person: lambda p: p.pk}
