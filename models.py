from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import logging

DATABASE_URL = "sqlite:///./users.db"

logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Address(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    country = Column(String(100), nullable=False)
    city = Column(String(100), nullable=False)
    street = Column(String(200), nullable=False)
    flat_house = Column(String(50), nullable=False)

class CreditCard(Base):
    __tablename__ = "credit_cards"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    num = Column(String(19), nullable=False)
    cvv = Column(String(4), nullable=False)
    exp_date = Column(String(7), nullable=False)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    surname = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20), nullable=True)
    gender = Column(String(10), nullable=True)
    date_of_birth = Column(String(20), nullable=True)
    company = Column(String(200), nullable=True)
    salary = Column(Float, nullable=True)
    about_me = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


print("Creating database tables...")
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
print("Database tables created successfully!")