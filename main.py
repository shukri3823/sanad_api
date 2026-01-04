from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

# إنشاء التطبيق
app = FastAPI()

# نموذج بيانات المستخدم
class User(BaseModel):
 id: int
 username: str
 email: str
 password: str # للتجربة فقط

# "قاعدة بيانات" مؤقتة في الذاكرة
users_db: List[User] = []


@app.get("/")
def read_root():
 return {"message": "Hello from sanad_api on Render with users!"}


# تسجيل مستخدم جديد
@app.post("/users", response_model=User)
def create_user(user: User):
 # التأكد أن اسم المستخدم غير مكرر
 for u in users_db:
 if u.username == user.username:
 raise HTTPException(status_code=400, detail="Username already exists")
 users_db.append(user)
 return user


# عرض جميع المستخدمين
@app.get("/users", response_model=List[User])
def list_users():
 return users_db


# عرض مستخدم واحد حسب id
@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int):
 for u in users_db:
 if u.id == user_id:
 return u
 raise HTTPException(status_code=404, detail="User not found")


# حذف مستخدم
@app.delete("/users/{user_id}")
def delete_user(user_id: int):
 for index, u in enumerate(users_db):
 if u.id == user_id:
 users_db.pop(index)
 return {"message": "User deleted"}
 raise HTTPException(status_code=404, detail="User not found")


# نموذج طلب تسجيل الدخول
class LoginRequest(BaseModel):
 username: str
 password: str

# تسجيل دخول
@app.post("/login")
def login(data: LoginRequest):
 for u in users_db:
 if u.username == data.username and u.password == data.password:
 return {"message": "Login successful", "user_id": u.id}
 raise HTTPException(status_code=401, detail="Invalid username or password")
