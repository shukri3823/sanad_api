from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String, or_
from sqlalchemy.orm import sessionmaker, declarative_base, Session
import os

# 1. إعداد قاعدة البيانات
DATABASE_URL = "postgresql://sanad_db_g2je_user:55a9KIecqyh8SfznzU0WEZmsj71r7Eej@dpg-d5d3miggjchc73dfdhkg-a:5432/sanad_db_g2je"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. الجدول
class UserDB(Base):
    __tablename__ = "users_test" # غيرنا الاسم للتأكد من إنشاء جدول جديد نظيف
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

Base.metadata.create_all(bind=engine)

# 3. النماذج (Schemas)
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    class Config:
        from_attributes = True

# 4. التطبيق والاتصال
app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 5. المسارات (تأكد من الأسماء)

@app.get("/")
def home():
    return {"status": "Online"}

@app.post("/register", response_model=UserResponse) # غيرنا الاسم لـ register للتجربة
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # التحقق من وجود المستخدم
    chk = db.query(UserDB).filter(or_(UserDB.username == user.username, UserDB.email == user.email)).first()
    if chk:
        raise HTTPException(status_code=400, detail="Exists")
    
    db_user = UserDB(username=user.username, email=user.email, password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/all_users", response_model=List[UserResponse])
def get_users_list(db: Session = Depends(get_db)):
    return db.query(UserDB).all()
