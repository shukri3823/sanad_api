from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
 return {"message": "Sanad API is working!"}

@app.get("/test")
def read_test():
 return {"status": "ok", "note": "This is a test endpoint"}
