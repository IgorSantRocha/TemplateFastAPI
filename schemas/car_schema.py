from typing import Optional
from pydantic import BaseModel, Field


class CarBase(BaseModel):
    model: str
    year: int


class CarCreate(CarBase):
    pass


class CarUpdate(CarBase):
    pass


class CarInDbBase(CarBase):
    id: int


class Car(CarInDbBase):
    pass
