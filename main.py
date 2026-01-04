from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String, or_
from sqlalchemy.orm import sessionmaker, declarative_base, Session
import os

# إعداد رابط قاعدة البيانات من متغير البيئة أو ثابتًا مؤقتًا
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
 DATABASE_URL = "postgresql://sanad_db_g2je_user:55a9KIecqyh8SfznzU0WEZmsj71r7Eej@dpg-d5d3miggjchc73dfdhkg-a:5432/sanad_db_g2je"

# إعداد SQLAlchemy
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# نموذج جدول المستخدمين في قاعدة البيانات
class UserDB(Base):
 __tablename__ = "users"

 id = Column(Integer, primary_key=True, index=True)
 username = Column(String, unique=True, index=True, nullable=False)
 email = Column(String, unique=True, index=True, nullable=False)
 password = Column(String, nullable=False)

# إنشاء الجداول
Base.metadata.create_all(bind=engine)

# نماذج Pydantic
class UserCreate(BaseModel):
 username: str
 email: str
 password: str

class UserResponse(BaseModel):
 id: int
 username: str
 email: str

 class Config:
 orm_mode = True

class LoginRequest(BaseModel):
 username: str
 password: str

# تطبيق FastAPI
app = FastAPI()

# دالة الحصول على جلسة قاعدة البيانات
def get_db():
 db = SessionLocal()
 try:
 yield db
 finally:
 db.close()

# المسارات الأساسية
@app.get("/")
def read_root():
 return {"message": "Sanad API is working!"}

@app.get("/test")
def read_test():
 return {"status": "ok", "note": "This is a test endpoint"}

# إنشاء مستخدم جديد
@app.post("/users", response_model=UserResponse)
def create_user(user: UserCreate):
 db: Session = next(get_db())
 existing_user = db.query(UserDB).filter(
 or_(UserDB.username == user.username, UserDB.email == user.email)
 ).first()
 if existing_user:
 raise HTTPException(status_code=400, detail="Username or email already exists")

 new_user = UserDB(
 username=user.username,
 email=user.email,
 password=user.password
 )
 db.add(new_user)
 db.commit()
 db.refresh(new_user)
 return new_user

# جلب جميع المستخدمين
@app.get("/users", response_model=List[UserResponse])
def list_users():
 db: Session = next(get_db())
 users = db.query(UserDB).all()
 return users

# جلب مستخدم حسب id
@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
 db: Session = next(get_db())
 user = db.query(UserDB).filter(UserDB.id == user_id).first()
 if not user:
 raise HTTPException(status_code=404, detail="User not found")
 return user

# حذف مستخدم
@app.delete("/users/{user_id}")
def delete_user(user_id: int):
 db: Session = next(get_db())
 user = db.query(UserDB).filter(UserDB.id == user_id).first()
 if not user:
 raise HTTPException(status_code=404, detail="User not found")
 db.delete(user)
 db.commit()
 return {"message": "User deleted"}

# تسجيل دخول
@app.post("/login")
def login(data: LoginRequest):
 db: Session = next(get_db())
 user = db.query(UserDB).filter(UserDB.username == data.username).first()
 if not user or user.password != data.password:
 raise HTTPException(status_code=401, detail="Invalid username or password")
 return {"message": "Login successful", "user_id": user.id}
