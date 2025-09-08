import random
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, Query
from pydantic import BaseModel, EmailStr, validator
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from typing import List, Optional
import datetime
import re
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging

from generate_users import generate_test_users, generate_user_data, create_user_in_db
from models import SessionLocal, User, Address, CreditCard

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = "sqlite:///./users.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

scheduler = AsyncIOScheduler()

def initialize_users():
    """Initialize users only if database is empty"""
    db = SessionLocal()
    try:
        user_count = db.query(User).count()
        if user_count == 0:
            logger.info("Database is empty, generating initial test users...")
            generate_test_users(1000)
        else:
            logger.info(f"Database already contains {user_count} users, skipping initialization")
    finally:
        db.close()

def scheduled_user_management():
    """Scheduled job to add and remove users"""
    db = SessionLocal()
    try:
        # Add random number of users (1-7)
        users_to_add = random.randint(1, 7)
        added_count = 0

        for _ in range(users_to_add):
            user_data = generate_user_data()
            user_id = create_user_in_db(db, user_data)
            if user_id:
                added_count += 1

        # Delete random number of oldest users (1-3)
        users_to_delete = random.randint(1, 3)
        oldest_users = db.query(User).order_by(User.created_at.asc()).limit(users_to_delete).all()

        deleted_count = 0
        for user in oldest_users:
            try:
                # Delete related records first
                db.query(Address).filter(Address.user_id == user.id).delete()
                db.query(CreditCard).filter(CreditCard.user_id == user.id).delete()

                # Delete user
                db.delete(user)
                deleted_count += 1
            except Exception as e:
                logger.error(f"Error deleting user {user.id}: {str(e)}")
                db.rollback()
                continue

        db.commit()

        # Get current user count
        total_users = db.query(User).count()

        logger.info(f"Scheduled job completed: Added {added_count} users, deleted {deleted_count} users. Total users: {total_users}")

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
        trigger=IntervalTrigger(minutes=1),
        id='user_management',
        name='Add and remove users every minute',
        replace_existing=True
    )
    scheduler.start()
    logger.info("Scheduler started - user management job will run every minute")

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
        return '-'.join([clean_num[i:i+4] for i in range(0, len(clean_num), 4)])

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
    email: EmailStr
    phone: str
    date_of_birth: datetime.date
    address: AddressModel
    gender: str
    company: Optional[str] = None
    salary: Optional[float] = None
    credit_card: CreditCardModel

    @validator('gender')
    def validate_gender(cls, v):
        if v.lower() not in ['male', 'female', 'other']:
            raise ValueError('Gender must be male, female, or other')
        return v.lower()

    @validator('phone')
    def validate_phone(cls, v):
        clean_phone = re.sub(r'[\s\-\(\)]', '', v)
        if not re.match(r'^\+?\d{10,15}$', clean_phone):
            raise ValueError('Invalid phone number format')
        return v

    @validator('date_of_birth')
    def validate_date_of_birth(cls, v):
        if v > datetime.date.today():
            raise ValueError('Date of birth cannot be in the future')
        min_date = datetime.date.today() - datetime.timedelta(days=120*365)
        if v < min_date:
            raise ValueError('Date of birth is too far in the past')
        return v

class UserUpdate(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    date_of_birth: Optional[datetime.date] = None
    address: Optional[AddressModel] = None
    gender: Optional[str] = None
    company: Optional[str] = None
    salary: Optional[float] = None
    credit_card: Optional[CreditCardModel] = None

    @validator('gender')
    def validate_gender(cls, v):
        if v and v.lower() not in ['male', 'female', 'other']:
            raise ValueError('Gender must be male, female, or other')
        return v.lower() if v else v

    @validator('phone')
    def validate_phone(cls, v):
        if v:
            clean_phone = re.sub(r'[\s\-\(\)]', '', v)
            if not re.match(r'^\+?\d{10,15}$', clean_phone):
                raise ValueError('Invalid phone number format')
        return v

    @validator('date_of_birth')
    def validate_date_of_birth(cls, v):
        if v:
            if v > datetime.date.today():
                raise ValueError('Date of birth cannot be in the future')
            min_date = datetime.date.today() - datetime.timedelta(days=120*365)
            if v < min_date:
                raise ValueError('Date of birth is too far in the past')
        return v

class UserResponse(BaseModel):
    id: int
    name: str
    surname: str
    email: str
    phone: str
    date_of_birth: datetime.date
    address: AddressModel
    gender: str
    company: Optional[str]
    salary: Optional[float]
    about_me: str
    credit_card: CreditCardModel
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

    address = db.query(Address).filter(Address.user_id == user_id).first()
    credit_card = db.query(CreditCard).filter(CreditCard.user_id == user_id).first()

    return {
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
        "address": {
            "country": address.country,
            "city": address.city,
            "street": address.street,
            "flat_house": address.flat_house
        },
        "credit_card": {
            "num": credit_card.num,
            "cvv": credit_card.cvv,
            "exp_date": credit_card.exp_date
        }
    }

@app.get("/v1/users/search", response_model=List[UserResponse])
def search_users(
        name: Optional[str] = Query(None, description="Search by name (partial match)"),
        surname: Optional[str] = Query(None, description="Search by surname (partial match)"),
        email: Optional[str] = Query(None, description="Search by email (partial match)"),
        gender: Optional[str] = Query(None, description="Search by gender (exact match)"),
        date_of_birth: Optional[datetime.date] = Query(None, description="Search by exact date of birth"),
        date_of_birth_from: Optional[datetime.date] = Query(None, description="Search for users born after this date (inclusive)"),
        date_of_birth_to: Optional[datetime.date] = Query(None, description="Search for users born before this date (inclusive)"),
        limit: int = Query(100, ge=1, le=1000, description="Maximum number of results to return"),
        offset: int = Query(0, ge=0, description="Number of results to skip"),
        db: Session = Depends(get_db)
):
    """
    Search users by various criteria.

    All text fields (name, surname, email) support partial matching (case-insensitive).
    Gender must be an exact match.
    Date of birth can be searched by exact date or date range.
    """

    # Validate gender if provided
    if gender and gender.lower() not in ['male', 'female', 'other']:
        raise HTTPException(status_code=400, detail="Gender must be 'male', 'female', or 'other'")

    # Validate date range
    if date_of_birth_from and date_of_birth_to and date_of_birth_from > date_of_birth_to:
        raise HTTPException(status_code=400, detail="date_of_birth_from cannot be later than date_of_birth_to")

    # Build query with filters
    query = db.query(User)

    # Text-based filters (case-insensitive partial matching)
    if name:
        query = query.filter(User.name.ilike(f"%{name}%"))

    if surname:
        query = query.filter(User.surname.ilike(f"%{surname}%"))

    if email:
        query = query.filter(User.email.ilike(f"%{email}%"))

    # Exact gender match
    if gender:
        query = query.filter(User.gender == gender.lower())

    # Date of birth filters
    if date_of_birth:
        # Exact date match
        query = query.filter(User.date_of_birth == date_of_birth)
    else:
        # Date range filters
        if date_of_birth_from:
            query = query.filter(User.date_of_birth >= date_of_birth_from)

        if date_of_birth_to:
            query = query.filter(User.date_of_birth <= date_of_birth_to)

    # Apply pagination
    users = query.offset(offset).limit(limit).all()

    # Get detailed user information
    result = []
    for user in users:
        user_details = get_user_with_details(db, user.id)
        if user_details:
            result.append(user_details)

    return result

@app.get("/v1/users", response_model=List[UserResponse])
def get_all_users(db: Session = Depends(get_db)):
    """Get all users"""
    users = db.query(User).all()
    result = []

    for user in users:
        user_details = get_user_with_details(db, user.id)
        if user_details:
            result.append(user_details)

    return result

@app.get("/v1/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID"""
    user_details = get_user_with_details(db, user_id)

    if not user_details:
        raise HTTPException(status_code=404, detail="User not found")

    return user_details

@app.post("/v1/users", response_model=UserResponse, status_code=201)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = User(
        name=user_data.name,
        surname=user_data.surname,
        email=user_data.email,
        phone=user_data.phone,
        date_of_birth=user_data.date_of_birth,
        gender=user_data.gender,
        company=user_data.company,
        salary=user_data.salary
    )
    db.add(db_user)
    db.flush()

    db_address = Address(
        user_id=db_user.id,
        country=user_data.address.country,
        city=user_data.address.city,
        street=user_data.address.street,
        flat_house=user_data.address.flat_house
    )
    db.add(db_address)

    db_credit_card = CreditCard(
        user_id=db_user.id,
        num=user_data.credit_card.num,
        cvv=user_data.credit_card.cvv,
        exp_date=user_data.credit_card.exp_date
    )
    db.add(db_credit_card)

    db.commit()

    return get_user_with_details(db, db_user.id)

@app.put("/v1/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db)):
    """Update user by ID"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if user_data.name is not None:
        db_user.name = user_data.name
    if user_data.surname is not None:
        db_user.surname = user_data.surname
    if user_data.email is not None:
        existing_user = db.query(User).filter(User.email == user_data.email, User.id != user_id).first()
        if existing_user:
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

    if user_data.credit_card is not None:
        db_credit_card = db.query(CreditCard).filter(CreditCard.user_id == user_id).first()
        if db_credit_card:
            db_credit_card.num = user_data.credit_card.num
            db_credit_card.cvv = user_data.credit_card.cvv
            db_credit_card.exp_date = user_data.credit_card.exp_date

    db.commit()

    return get_user_with_details(db, user_id)

@app.delete("/v1/users/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete user by ID"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db.query(Address).filter(Address.user_id == user_id).delete()
    db.query(CreditCard).filter(CreditCard.user_id == user_id).delete()

    db.delete(db_user)
    db.commit()

    return {"message": "User deleted successfully"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.datetime.utcnow()}

@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """Get database statistics"""
    total_users = db.query(User).count()
    total_addresses = db.query(Address).count()
    total_credit_cards = db.query(CreditCard).count()

    # Get some additional stats
    users_with_company = db.query(User).filter(User.company.isnot(None)).count()
    male_users = db.query(User).filter(User.gender == 'male').count()
    female_users = db.query(User).filter(User.gender == 'female').count()
    other_users = db.query(User).filter(User.gender == 'other').count()

    return {
        "total_users": total_users,
        "total_addresses": total_addresses,
        "total_credit_cards": total_credit_cards,
        "users_with_company": users_with_company,
        "gender_distribution": {
            "male": male_users,
            "female": female_users,
            "other": other_users
        },
        "timestamp": datetime.datetime.utcnow()
    }

if __name__ == "__main__":
    import uvicorn
    print("Starting server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)