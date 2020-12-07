from pathlib import Path

import glob

import os
import typer
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

import asyncio

from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from schemas.predict_response import ResponseSingleLabel, PayloadPredictImage
from handler.image_classifier import ImageClassifier

app = FastAPI()
app.mount("/static", StaticFiles(directory="html"), name="static")

from api import ping
app.include_router(ping.router)


origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

path = Path(__file__).parent

learner: ImageClassifier = None


async def setup_learner():
    learner = ImageClassifier(model_name="efficientnet_b2.pkl")
    learner.initialize()
    return learner


def run_learner_predict(file_path, learner) -> ResponseSingleLabel:
    pred, features_array = learner.predict(file_path)
    item = ResponseSingleLabel()
    item.label = pred
    item.vector = features_array.tolist()
    return item


@app.on_event("startup")
async def startup_event():
    """Setup the learner on server start"""
    global learner
    loop = asyncio.get_event_loop()  # get event loop
    tasks = [asyncio.ensure_future(setup_learner())]  # assign some task
    learner = (await asyncio.gather(*tasks))[0]  # get tasks


@app.on_event("shutdown")
async def shutdown():
    files = glob.glob('/tmp/download/*')
    for f in files:
        os.remove(f)


@app.get('/')
async def homepage():
    html_content = (path / 'html/index.html').open().read()
    return HTMLResponse(content=html_content, status_code=200)


@app.post("/analyze")
async def analyze(file: bytes = File(...)):
    item = run_learner_predict(file, learner)

    if item.label:
        return item.label
    else:
        return JSONResponse(status_code=404, content={"message": "Item not predicted"})


@app.post("/predictions/efficientnet")
async def predictions(file_url: PayloadPredictImage):
    """
    curl -i --data '{"file_url":"https://s3.posred.pro/media/order_image/82673/order_kQLUjia.jpeg"}' http://localhost:8001/predictions/efficientnet
    :param file_url:
    :return:
    """

    print(file_url)
    file_path = file_url.download()

    item = run_learner_predict(file_path, learner)

    if item.label:
        return item.label
    else:
        return JSONResponse(status_code=404, content={"message": "Item not predicted"})


app_typer = typer.Typer()


@app_typer.command()
def predict(url: str):
    learner = ImageClassifier(model_name="efficientnet_b2.pkl")
    learner.initialize()

    file_url = PayloadPredictImage(file_url=url)

    file_path = file_url.download()

    item = run_learner_predict(file_path, learner)

    typer.echo(item.label)


if __name__ == "__main__":
    app_typer()
