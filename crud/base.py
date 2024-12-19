import logging
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import desc
from db.base_class import Base
from sqlalchemy import update  # Importe o update do SQLAlchemy aqui

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        logging.info(f'Obtendo {self.model.__name__} de id={id}')
        return db.query(self.model).filter(self.model.id == id).first()

    def get_first_by_filter(
        self, db: Session, *, order_by: str = "id", filterby: str = "enviado", filter: str
    ) -> List[ModelType]:
        logging.info(
            f'Obtendo lista de {self.model.__name__} cujo {filterby}={filter}')
        return db.query(self.model).order_by(getattr(self.model, order_by)).filter(getattr(self.model, filterby) == filter).first()

    def get_multi(
            self, db: Session, *, skip: int = 0, limit: int = 100, order_by: str = "id"
    ) -> List[ModelType]:
        logging.info(f'Obtendo lista de {self.model.__name__}')
        return db.query(self.model).order_by(getattr(self.model, order_by)).offset(skip).limit(limit).all()

    def get_multi_filter(
        self, db: Session, *, order_by: str = "id", filterby: str = "enviado", filter: str
    ) -> List[ModelType]:
        logging.info(
            f'Obtendo lista de {self.model.__name__} cujo {filterby}={filter}')
        return db.query(self.model).order_by(getattr(self.model, order_by)).filter(getattr(self.model, filterby) == filter).all()

    def get_multi_filters(
        self,
        db: Session,
        *,
        filters: List[Dict[str, Any]]
    ) -> List[ModelType]:
        query = db.query(self.model)
        logging.info(
            f'Obtendo lista de {self.model.__name__} de acordo com os filtros')

        # Definir um mapa de operadores
        operator_map = {
            '=': lambda field, value: field == value,
            '!=': lambda field, value: field != value,
            '<': lambda field, value: field < value,
            '<=': lambda field, value: field <= value,
            '>': lambda field, value: field > value,
            '>=': lambda field, value: field >= value,
            'like': lambda field, value: field.like(value),
            'ilike': lambda field, value: field.ilike(value),
            'in': lambda field, value: field.in_(value),
            'notin': lambda field, value: field.notin_(value),
            # Adicionar mais operadores conforme necessário
        }

        for filter in filters:
            field_name = filter["field"]
            operator = filter.get("operator", "=")  # Operador padrão é '='
            value = filter["value"]

            field = getattr(self.model, field_name)

            if operator in operator_map:
                query = query.filter(operator_map[operator](field, value))
            else:
                raise ValueError(f"Operador desconhecido: {operator}")

        return query.all()

    def get_last_by_filters(
        self,
        db: Session,
        *,
        filters: Dict[str, Dict[str, Union[str, int]]],
    ) -> Optional[ModelType]:
        logging.info(
            f'Obtendo último registro de {self.model.__name__} de acordo com os filtros')
        query = db.query(self.model)

        for filter_name, filter_data in filters.items():
            operator = filter_data['operator']
            filter_value = filter_data['value']

            if operator == '>':
                query = query.filter(
                    getattr(self.model, filter_name) > filter_value)
            elif operator == '<':
                query = query.filter(
                    getattr(self.model, filter_name) < filter_value)
            elif operator == '>=':
                query = query.filter(
                    getattr(self.model, filter_name) >= filter_value)
            elif operator == '<=':
                query = query.filter(
                    getattr(self.model, filter_name) <= filter_value)
            elif operator == '==':
                query = query.filter(
                    getattr(self.model, filter_name) == filter_value)
            elif operator == '!=':
                query = query.filter(
                    getattr(self.model, filter_name) != filter_value)
            elif operator == 'like':
                query = query.filter(
                    getattr(self.model, filter_name).like(f"%{filter_value}%"))
            elif operator == 'is_null':
                query = query.filter(
                    getattr(self.model, filter_name).is_(None))
            else:
                # Handle other operators as needed
                pass

        return query.order_by(desc(self.model.id)).first()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        logging.info(f'Criando objeto em {self.model.__name__}')
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def create_multi(self, db: Session, *, obj_in: List[CreateSchemaType]) -> List[ModelType]:
        logging.info(f'Criando lista de objetos {self.model.__name__}')
        db_objs = [self.model(**jsonable_encoder(item)) for item in obj_in]
        db.bulk_save_objects(db_objs)
        db.commit()
        return {'msg': 'Chamados inseridos com sucesso'}

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        logging.info(f'Atualizando o objeto de {self.model.__name__}')
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        obj_data = jsonable_encoder(db_obj)
        return obj_data

    def update_multi(
        self,
        db: Session,
        *,
        objs_in: List[Union[UpdateSchemaType, Dict[str, Any]]],
        filtro: str
    ) -> List[ModelType]:
        logging.info(f'Atualizando lista de objetos {self.model.__name__}')
        updated_objs = []
        for obj_in in objs_in:
            obj_data = jsonable_encoder(obj_in) if isinstance(
                obj_in, BaseModel) else obj_in
            filter_args = {filtro: obj_data[filtro]}
            db_obj = db.query(self.model).filter_by(**filter_args).first()
            if db_obj:
                db.execute(
                    update(self.model)
                    .filter_by(**filter_args)
                    .values(**obj_data)
                )
                db.commit()
                db.refresh(db_obj)
                updated_objs.append(db_obj)
        return [updated_objs]

    def remove(self, db: Session, *, id: int) -> ModelType:
        logging.info(f'Removendo objeto {self.model.__name__} de id={id}')
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj
