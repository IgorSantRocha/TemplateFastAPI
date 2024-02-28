from sqlalchemy import Column, Integer, String
from db.base_class import Base


class Car(Base):
    __tablename__ = 'TB_Car'
    id = Column(Integer, primary_key=True, index=True)
    model = Column(String(255), index=True)
    year = Column(Integer, index=True)
