from sqlalchemy import Column, Integer, String
from model.base import Base

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    description = Column(String(255))
    date = Column(String(9))
    time = Column(String(12))

    def __init__(self, description:str, date:str, time:str):
        self.description = description
        self.date = date
        self.time = time