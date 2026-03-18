from fastapi import FastAPI
from app.core.database import Base, engine
from app.models import *

app = FastAPI()

Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root():
    return {"BIENVENIDO"}