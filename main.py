from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
 return {"message": "Hello from sanad_api on Render"}

@app.get("/products")
def get_products():
 return [
 {"id": 1, "name": "Product A", "price": 10},
 {"id": 2, "name": "Product B", "price": 20},
 ]
