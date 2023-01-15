import os
from typing import Any

import uvicorn
from fastapi import FastAPI
from fastapi import File
from fastapi import Form
from fastapi import Request
from fastapi import UploadFile
from fastapi.responses import FileResponse
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware

from core.router import ROUTER
from core.utils import save_file


def flash(request: Request, message: Any, category: str = "primary") -> None:
    if "_messages" not in request.session:
        request.session["_messages"] = []
        request.session["_messages"].append({"message": message, "category": category})


def get_flashed_messages(request: Request):
    print(request.session)
    return request.session.pop("_messages") if "_messages" in request.session else []


middleware = [Middleware(SessionMiddleware, secret_key="super-secret")]
app = FastAPI(title="ExtractorWebApp", version="1.0.0", middleware=middleware)
app.mount("/static/", StaticFiles(directory="static", html=True), name="static")

templates = Jinja2Templates(directory="templates")
templates.env.globals["get_flashed_messages"] = get_flashed_messages


async def run(obj):
    return obj.execute()


@app.get("/download")
async def download():
    file_name = "download.xlsx"
    file_path = os.path.join(os.getcwd(), "static", "out", file_name)
    return FileResponse(path=file_path, media_type="application/octet-stream", filename=file_name)


@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/")
async def execute(request: Request, option: str = Form(...), file_path: UploadFile = File(...)):
    content = await file_path.read()
    file_path = save_file(file_path.filename, content)

    extractor = ROUTER.get(option).Extractor(file_path)
    download_file = await run(extractor)
    if download_file:
        flash(request, "Arquivo processado com sucesso!", "success")
        return templates.TemplateResponse(
            "index.html", {"request": request, "download": download_file}
        )
    flash(request, "Aldo deu errado, tente novamente mais tarde..", "danger")
    return templates.TemplateResponse("index.html", {"request": request})


if __name__ == "__main__":
    uvicorn.run("main:app", port=5000, log_level="info", reload=True)
