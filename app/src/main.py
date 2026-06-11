from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from database import init_pool, init_db, init_redis, get_labels_cloud, toggle_fav
from fastapi.templating import Jinja2Templates
from search import interpret_search


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting FastAPI for Image-Search...")
    init_pool()
    init_db()
    init_redis()
    yield
    # no shutdown cmds

app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory="templates")


@app.get("/")
def index(request: Request, q: str = None, show_cloud: str = None, fav: str = None):
    images, total = interpret_search(q, None, fav)
    label_cloud = get_labels_cloud()
    return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"images": images, "total": total, "label_cloud": label_cloud, "fav": fav}
    )


@app.post("/favourite/{image_id}")
def favourite(image_id: int):
    toggle_fav(image_id)
    return {"status": "ok"}
