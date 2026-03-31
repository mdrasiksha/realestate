from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from .database import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    phone = Column(String)
    status = Column(String, default="new")
    created_at = Column(DateTime, default=datetime.utcnow)
    follow_up_date = Column(DateTime, nullable=True)
    property_id = Column(Integer, ForeignKey("properties.id"))
    property = relationship("Property")


class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True)
    location = Column(String)
    price = Column(Integer)
    type = Column(String)
    status = Column(String, default="available")