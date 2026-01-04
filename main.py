from fastapi import FastAPI

app = FastAPI()

@app.get("/test-file")
def read_test_file():
with open("test_sanad.txt", "r", encoding="utf-8") as f:
content = f.read()
return {"content": content}
