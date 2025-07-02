# app/db/models.py
from sqlalchemy import Column, BigInteger, Integer, String, Text, TIMESTAMP, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(Text)
    full_name = Column(Text)
    role = Column(String, default="candidate")
    created_at = Column(TIMESTAMP, server_default=func.now())
