from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from model import Base

class RecordType(Base):
    __tablename__ = "record_type"

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    order = Column(Integer)

    records = relationship("Record", back_populates="record_type")

    def __init__(self, name:str, order:int):
        self.name = name
        self.order = order