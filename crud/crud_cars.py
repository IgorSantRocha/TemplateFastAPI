from crud.base import CRUDBase
from models.car_model import Car
from schemas.car_schema import CarCreate, CarUpdate


class CRUDItem(CRUDBase[Car, CarCreate, CarUpdate]):
    pass


car = CRUDItem(Car)
