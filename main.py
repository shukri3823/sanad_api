from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String, or_
from sqlalchemy.orm import sessionmaker, declarative_base, Session
import os

# 1. إعداد قاعدة البيانات (نفس الرابط الخاص بك)
DATABASE_URL = "postgresql://sanad_db_g2je_user:55a9KIecqyh8SfznzU0WEZmsj71r7Eej@dpg-d5d3miggjchc73dfdhkg-a:5432/sanad_db_g2je"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. نموذج الجدول (Database Model) - أضفنا حقل الهاتف phone
class UserDB(Base):
    __tablename__ = "users_final"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=True) # حقل إضافي للرقم
    password = Column(String, nullable=False)

Base.metadata.create_all(bind=engine)

# 3. نماذج Pydantic (المسؤولة عن استقبال البيانات من المستخدم)
class UserCreate(BaseModel):
    username: str
    email: str
    phone: Optional[str] = None # يستقبل رقم الهاتف (اختياري)
    password: str

# نموذج عرض البيانات (ما يرجع للمستخدم بعد النجاح)
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    phone: Optional[str] = None

    class Config:
        from_attributes = True

# 4. تطبيق FastAPI والاعتمادات
app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 5. المسارات المصححة تماماً

@app.get("/")
def home():
    return {"status": "Sanad API Online"}

@app.post("/users", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # التأكد من عدم تكرار اليوزر أو الإيميل
    check_exists = db.query(UserDB).filter(
        or_(UserDB.username == user.username, UserDB.email == user.email)
    ).first()
    
    if check_exists:
        raise HTTPException(status_code=400, detail="Username or Email already registered")
    
    # إنشاء الكائن وتخزينه
    new_user = UserDB(
        username=user.username,
        email=user.email,
        phone=user.phone,
        password=user.password # نصيحة: في المستقبل يفضل تشفيرها
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user) # لجلب الـ ID الذي تم إنشاؤه تلقائياً
    return new_user

@app.get("/users", response_model=List[UserResponse])
def list_all_users(db: Session = Depends(get_db)):
    return db.query(UserDB).all()
