from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from database import init_pool, init_db
from fastapi.templating import Jinja2Templates
from search import interpret_search


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting FastAPI for Image-Search...")
    init_pool()
    init_db()
    yield
    # no shutdown cmds

app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory="templates")


@app.get("/")
def index(request: Request, q: str = None):
    images, total = interpret_search(q, None)
    return templates.TemplateResponse(request=request, name="index.html", context={"images": images, "total": total})
