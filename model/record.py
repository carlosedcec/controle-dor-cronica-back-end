from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from model.base import Base
from model.record_type import RecordType

class Record(Base):
    __tablename__ = "records"

    id = Column(Integer, primary_key=True)
    record_type_id = Column(Integer, ForeignKey("record_type.id"))
    date = Column(String(9))
    time = Column(String(12))
    value = Column(Integer)

    record_type = relationship("RecordType", back_populates="records")

    def __init__(self, record_type_id: int, date: str, time: str, value: int):
        self.record_type_id = record_type_id
        self.date = date
        self.time = time
        self.value = value