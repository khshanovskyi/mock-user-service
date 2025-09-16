import datetime
import logging
import os
import random
import re
from contextlib import asynccontextmanager
from typing import List, Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from fastapi import FastAPI, HTTPException, Depends, Query
from pydantic import BaseModel, validator
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from generate_users import generate_test_users, generate_user_data, create_user_in_db
from models import SessionLocal, User, Address, CreditCard

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Disable SQLAlchemy logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

DATABASE_URL = "sqlite:///./users.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False  # Disable SQL query logging
)

scheduler = AsyncIOScheduler()


def initialize_users():
    """Initialize users only if database is empty"""
    db = SessionLocal()
    try:
        user_count = db.query(User).count()
        if user_count == 0:
            logger.info("Database is empty, generating initial test users...")
            generate_test_users(int(os.getenv('USERS_NUMBER', 100)))
            logger.info(f"Successfully initialized {os.getenv('USERS_NUMBER', 100)} test users")
        else:
            logger.info(f"Database already contains {user_count} users, skipping initialization")
    finally:
        db.close()


def scheduled_user_management():
    """Scheduled job to add and remove users"""
    db = SessionLocal()
    try:
        users_to_add = random.randint(1, 7)
        added_count = 0

        for _ in range(users_to_add):
            user_data = generate_user_data()
            user_id = create_user_in_db(db, user_data)
            if user_id:
                added_count += 1

        users_to_delete = random.randint(1, 3)
        oldest_users = db.query(User).order_by(User.created_at.asc()).limit(users_to_delete).all()

        deleted_count = 0
        for user in oldest_users:
            try:
                db.query(Address).filter(Address.user_id == user.id).delete()
                db.query(CreditCard).filter(CreditCard.user_id == user.id).delete()

                db.delete(user)
                deleted_count += 1
            except Exception as e:
                logger.error(f"Error deleting user {user.id}: {str(e)}")
                db.rollback()
                continue

        db.commit()

        # Get current user count
        total_users = db.query(User).count()

        logger.info(
            f"Scheduled job completed: Added {added_count} users, deleted {deleted_count} users. Total users: {total_users}")

    except Exception as e:
        logger.error(f"Error in scheduled user management: {str(e)}")
        db.rollback()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan"""
    logger.info("Starting UserService API...")
    initialize_users()

    scheduler.add_job(
        scheduled_user_management,
        trigger=IntervalTrigger(minutes=5),
        id='user_management',
        name='Add and remove users every 5 minutes',
        replace_existing=True
    )
    scheduler.start()
    logger.info("Scheduler started - user management job will run every 5 minutes")

    yield

    logger.info("Shutting down UserService API...")
    scheduler.shutdown()


class AddressModel(BaseModel):
    country: str
    city: str
    street: str
    flat_house: str


class CreditCardModel(BaseModel):
    num: str
    cvv: str
    exp_date: str

    @validator('num')
    def validate_card_number(cls, v):
        clean_num = re.sub(r'[\s-]', '', v)
        if not re.match(r'^\d{13,19}$', clean_num):
            raise ValueError('Invalid credit card number format')
        return '-'.join([clean_num[i:i + 4] for i in range(0, len(clean_num), 4)])

    @validator('cvv')
    def validate_cvv(cls, v):
        if not re.match(r'^\d{3,4}$', v):
            raise ValueError('CVV must be 3 or 4 digits')
        return v

    @validator('exp_date')
    def validate_exp_date(cls, v):
        if not re.match(r'^\d{2}/\d{4}$', v):
            raise ValueError('Expiration date must be in MM/YYYY format')
        return v


class UserCreate(BaseModel):
    name: str
    surname: str
    email: str
    phone: Optional[str] = None
    date_of_birth: Optional[str] = None
    address: Optional[AddressModel] = None
    gender: Optional[str] = None
    company: Optional[str] = None
    salary: Optional[float] = None
    about_me: str
    credit_card: Optional[CreditCardModel] = None


class UserUpdate(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[str] = None
    address: Optional[AddressModel] = None
    gender: Optional[str] = None
    company: Optional[str] = None
    salary: Optional[float] = None
    credit_card: Optional[CreditCardModel] = None


class UserResponse(BaseModel):
    id: int
    name: str
    surname: str
    email: str
    phone: Optional[str]
    date_of_birth: Optional[str]
    address: Optional[AddressModel]
    gender: Optional[str]
    company: Optional[str]
    salary: Optional[float]
    about_me: Optional[str]
    credit_card: Optional[CreditCardModel]
    created_at: datetime.datetime

    class Config:
        from_attributes = True


app = FastAPI(
    title="UserService API",
    version="1.0.0",
    lifespan=lifespan
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_user_with_details(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None

    user = {
        "id": user.id,
        "name": user.name,
        "surname": user.surname,
        "email": user.email,
        "phone": user.phone,
        "date_of_birth": user.date_of_birth,
        "gender": user.gender,
        "company": user.company,
        "salary": user.salary,
        "about_me": user.about_me,
        "created_at": user.created_at,
        "address": None,        # Always include, default to None
        "credit_card": None,    # Always include, default to None
    }

    address = db.query(Address).filter(Address.user_id == user_id).first()
    if address:
        user["address"] = {
            "country": address.country,
            "city": address.city,
            "street": address.street,
            "flat_house": address.flat_house
        }
    credit_card = db.query(CreditCard).filter(CreditCard.user_id == user_id).first()
    if credit_card:
        user["credit_card"] = {
            "num": credit_card.num,
            "cvv": credit_card.cvv,
            "exp_date": credit_card.exp_date
        }

    return user


@app.get("/v1/users/search", response_model=List[UserResponse])
async def search_users(
        name: Optional[str] = Query(None, description="Search by name (partial match)"),
        surname: Optional[str] = Query(None, description="Search by surname (partial match)"),
        email: Optional[str] = Query(None, description="Search by email (partial match)"),
        db: Session = Depends(get_db)
):
    """
    Search users by various criteria.

    All text fields (name, surname, email) support partial matching (case-insensitive).
    Gender must be an exact match.
    Date of birth can be searched by exact date or date range.
    """
    logger.info(f"Search users request - name: {name}, surname: {surname}, email: {email}")

    query = db.query(User)

    if name:
        query = query.filter(User.name.ilike(f"%{name}%"))

    if surname:
        query = query.filter(User.surname.ilike(f"%{surname}%"))

    if email:
        query = query.filter(User.email.ilike(f"%{email}%"))

    users = query.all()

    result = []
    for user in users:
        user_details = get_user_with_details(db, user.id)
        if user_details:
            result.append(user_details)

    logger.info(f"Search users completed - found {len(result)} users matching criteria")
    return result


@app.get("/v1/users", response_model=List[UserResponse])
async def get_all_users(db: Session = Depends(get_db)):
    """Get all users"""
    logger.info("Get all users request")

    users = db.query(User).all()
    result = []

    for user in users:
        user_details = get_user_with_details(db, user.id)
        if user_details:
            result.append(user_details)

    logger.info(f"Get all users completed - returned {len(result)} users")
    return result


@app.get("/v1/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID"""
    logger.info(f"Get user request - user_id: {user_id}")

    user_details = get_user_with_details(db, user_id)

    if not user_details:
        logger.warning(f"User not found - user_id: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")

    logger.info(f"Get user completed successfully - user_id: {user_id}")
    return user_details


@app.post("/v1/users", response_model=UserResponse, status_code=201)
async def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    logger.info(f"Create user request - email: {user_data.email}")

    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        logger.warning(f"User creation failed - email already exists: {user_data.email}")
        raise HTTPException(status_code=400, detail="User with such email is already registered")

    try:
        db_user = User(
            name=user_data.name,
            surname=user_data.surname,
            email=user_data.email,
            phone=user_data.phone,
            date_of_birth=user_data.date_of_birth,
            gender=user_data.gender,
            company=user_data.company,
            salary=user_data.salary,
            about_me=user_data.about_me
        )
        db.add(db_user)
        db.flush()

        if user_data.address:
            db_address = Address(
                user_id=db_user.id,
                country=user_data.address.country,
                city=user_data.address.city,
                street=user_data.address.street,
                flat_house=user_data.address.flat_house
            )
            db.add(db_address)
            db.flush()
            logger.info(f"Address created for user_id: {db_user.id}")

        if user_data.credit_card:
            db_credit_card = CreditCard(
                user_id=db_user.id,
                num=user_data.credit_card.num,
                cvv=user_data.credit_card.cvv,
                exp_date=user_data.credit_card.exp_date
            )
            db.add(db_credit_card)
            db.flush()
            logger.info(f"Credit card created for user_id: {db_user.id}")

        db.commit()
        logger.info(f"User created successfully - user_id: {db_user.id}, email: {user_data.email}")

    except Exception as error:
        logger.error(f"Error creating user - email: {user_data.email}, error: {str(error)}")
        db.rollback()
        raise error

    return get_user_with_details(db, db_user.id)


@app.put("/v1/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db)):
    """Update user by ID"""
    logger.info(f"Update user request - user_id: {user_id}")

    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        logger.warning(f"Update user failed - user not found: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")

    try:
        if user_data.name is not None:
            db_user.name = user_data.name
        if user_data.surname is not None:
            db_user.surname = user_data.surname
        if user_data.email is not None:
            existing_user = db.query(User).filter(User.email == user_data.email, User.id != user_id).first()
            if existing_user:
                logger.warning(f"Update user failed - email already exists: {user_data.email}")
                raise HTTPException(status_code=400, detail="Email already registered")
            db_user.email = user_data.email
        if user_data.phone is not None:
            db_user.phone = user_data.phone
        if user_data.date_of_birth is not None:
            db_user.date_of_birth = user_data.date_of_birth
        if user_data.gender is not None:
            db_user.gender = user_data.gender
        if user_data.company is not None:
            db_user.company = user_data.company
        if user_data.salary is not None:
            db_user.salary = user_data.salary

        if user_data.address is not None:
            db_address = db.query(Address).filter(Address.user_id == user_id).first()
            if db_address:
                db_address.country = user_data.address.country
                db_address.city = user_data.address.city
                db_address.street = user_data.address.street
                db_address.flat_house = user_data.address.flat_house
                logger.info(f"Address updated for user_id: {user_id}")

        if user_data.credit_card is not None:
            db_credit_card = db.query(CreditCard).filter(CreditCard.user_id == user_id).first()
            if db_credit_card:
                db_credit_card.num = user_data.credit_card.num
                db_credit_card.cvv = user_data.credit_card.cvv
                db_credit_card.exp_date = user_data.credit_card.exp_date
                logger.info(f"Credit card updated for user_id: {user_id}")

        db.commit()
        logger.info(f"User updated successfully - user_id: {user_id}")

    except HTTPException:
        raise
    except Exception as error:
        logger.error(f"Error updating user - user_id: {user_id}, error: {str(error)}")
        db.rollback()
        raise error

    return get_user_with_details(db, user_id)


@app.delete("/v1/users/{user_id}", status_code=204)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete user by ID"""
    logger.info(f"Delete user request - user_id: {user_id}")

    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        logger.warning(f"Delete user failed - user not found: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")

    try:
        # Delete related records first
        addresses_deleted = db.query(Address).filter(Address.user_id == user_id).delete()
        credit_cards_deleted = db.query(CreditCard).filter(CreditCard.user_id == user_id).delete()

        # Delete the user
        db.delete(db_user)
        db.commit()

        logger.info(f"User deleted successfully - user_id: {user_id}, "
                    f"addresses_deleted: {addresses_deleted}, credit_cards_deleted: {credit_cards_deleted}")

    except Exception as error:
        logger.error(f"Error deleting user - user_id: {user_id}, error: {str(error)}")
        db.rollback()
        raise error

    return {"message": "User deleted successfully"}


@app.get("/health")
def health_check():
    logger.info("Health check requested")
    return {"status": "healthy", "timestamp": datetime.datetime.utcnow()}


if __name__ == "__main__":
    import uvicorn

    print("Starting server...")
    uvicorn.run(app, host="0.0.0.0", port=8041)