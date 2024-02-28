from typing import Any, List
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.request import RequestClient
from api import crud, models, schemas
from api import deps

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=List[schemas.Car])
async def read_cars(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
) -> Any:
    """
    Retrieve cars.
    """
    logger.info("Consultando carros")
    return crud.car.get_multi(db=db, skip=skip, limit=limit)


@router.post("/", response_model=schemas.Car)
async def create_car(
        *,
        db: Session = Depends(deps.get_db),
        car_in: schemas.CarCreate,
) -> Any:
    """
    Create new car.
    """
    car = crud.car.create(db=db, obj_in=car_in)
    return car


@router.delete(path="/{id}", response_model=schemas.Car)
async def delete_car(
        *,
        db: Session = Depends(deps.get_db),
        id: int,
) -> Any:
    """
    Delete an item.
    """
    car = crud.car.get(db=db, id=id)
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    car = crud.car.remove(db=db, id=id)
    return car


@router.get(path="/request")
async def request():
    client = RequestClient('GET', 'https://viacep.com.br/ws/03073010/json/',
                           {'test': 'test'}, {'param1': 'teste'}, 30)
    response = await client.send_api_request()
    return response
