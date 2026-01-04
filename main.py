from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String, or_
from sqlalchemy.orm import sessionmaker, declarative_base, Session
import os

# 1. إعداد قاعدة البيانات (تأكد من صحة الرابط)
DATABASE_URL = "postgresql://sanad_db_g2je_user:55a9KIecqyh8SfznzU0WEZmsj71r7Eej@dpg-d5d3miggjchc73dfdhkg-a:5432/sanad_db_g2je"

# إضافة تحسينات للاتصال لبيئة Render
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. الجدول
class UserDB(Base):
    __tablename__ = "users_v4"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=True)
    password = Column(String, nullable=False)

# إنشاء الجداول عند التشغيل
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Database error: {e}")

# 3. نماذج البيانات
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    phone: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    phone: Optional[str] = None
    class Config:
        from_attributes = True

app = FastAPI(title="Sanad API Final")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 4. المسارات ---

@app.get("/")
def home():
    return {"message": "API IS LIVE", "check": "Go to /docs to see POST"}

@app.post("/users", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # التحقق من التكرار
    exists = db.query(UserDB).filter(or_(UserDB.username == user.username, UserDB.email == user.email)).first()
    if exists:
        raise HTTPException(status_code=400, detail="User or Email already exists")
    
    db_user = UserDB(
        username=user.username,
        email=user.email,
        phone=user.phone,
        password=user.password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users", response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db)):
    return db.query(UserDB).all()
