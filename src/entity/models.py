from datetime import datetime
from sqlalchemy import Integer, String, Date, Column
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    first_name: Mapped[str] = Column(String(50))
    last_name: Mapped[str] = Column(String(50))
    birthday: Mapped[datetime.date] = Column(Date)
    emails: Mapped[str] = Column(String(150))
    phone_numbers: Mapped[str] = Column(String(20))
    creation_date: Mapped[datetime.date] = Column(Date, default=func.current_date())
    last_update: Mapped[datetime.date] = Column(Date, onupdate=func.current_date())
