import sys
import pathlib
sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
from fastapi import FastAPI

app = FastAPI()
import gunicorn

@app.get("/")
async def root():
    return {"message": "Hello World"}
