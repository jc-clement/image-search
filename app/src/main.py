from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import init_pool, init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting FastAPI for Image-Search...")
    init_pool()
    init_db()
    yield
    # no shutdown cmds

app = FastAPI(lifespan=lifespan)

@app.get("/")
def root():
    return {"status": "ok"}
