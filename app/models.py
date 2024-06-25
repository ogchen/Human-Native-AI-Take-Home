from pydantic import BaseModel
from enum import auto
from enum import StrEnum


class DataType(StrEnum):
    TEXT = auto()
    IMAGE = auto()
    AUDIO = auto()
    VIDEO = auto()
    ANIMATION = auto()


class Data(BaseModel):
    dataset_id: str
    id: str
    value: str


class Dataset(BaseModel):
    org_id: str
    id: str
    name: str
    type: DataType


class Organisation(BaseModel):
    id: str
    name: str
    email: str


class User(BaseModel):
    username: str
    full_name: str
    email: str
    org_id: str
