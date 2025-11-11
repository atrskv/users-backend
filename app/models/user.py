from faker import Faker
from pydantic import BaseModel, EmailStr
from sqlmodel import Field, SQLModel

from app.utils import fake_link

fake = Faker()


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: EmailStr
    first_name: str
    last_name: str
    avatar: str


class UserCreate(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    avatar: str

    @classmethod
    def random(cls):
        return cls(
            email=fake.email(),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            avatar=fake_link(),
        )


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    first_name: str | None = None
    last_name: str | None = None
    avatar: str | None = None
