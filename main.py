from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String, or_
from sqlalchemy.orm import sessionmaker, declarative_base, Session
import os

# --- إعداد قاعدة البيانات ---
# الرابط الخاص بك
DATABASE_URL = "postgresql://sanad_db_g2je_user:55a9KIecqyh8SfznzU0WEZmsj71r7Eej@dpg-d5d3miggjchc73dfdhkg-a:5432/sanad_db_g2je"

# تحسين الاتصال لبيئة Render (تجنب انقطاع الاتصال)
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- نموذج الجدول في قاعدة البيانات ---
class UserDB(Base):
    __tablename__ = "users_v5" # تغيير الاسم لضمان إنشاء جدول جديد نظيف
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=True)
    password = Column(String, nullable=False)

# إنشاء الجداول
Base.metadata.create_all(bind=engine)

# --- نماذج البيانات (Schemas) لـ FastAPI ---
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

# --- تعريف التطبيق ---
app = FastAPI(title="Sanad System API")

# دالة الحصول على الجلسة
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- المسارات (Endpoints) ---

# 1. مسار تجريبي للتأكد من أن السيرفر يعمل
@app.get("/")
def read_root():
    return {"status": "success", "message": "Welcome to Sanad API - Check /docs for POST"}

# 2. مسار الـ POST لإنشاء مستخدم (هذا الذي لم يكن يظهر)
@app.post("/users", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # التحقق من وجود المستخدم مسبقاً
    existing_user = db.query(UserDB).filter(
        or_(UserDB.username == user.username, UserDB.email == user.email)
    ).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or Email already exists")
    
    # إضافة المستخدم الجديد
    db_user = UserDB(
        username=user.username,
        email=user.email,
        password=user.password,
        phone=user.phone
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# 3. مسار الـ GET لجلب قائمة المستخدمين
@app.get("/users", response_model=List[UserResponse])
def get_all_users(db: Session = Depends(get_db)):
    return db.query(UserDB).all()
