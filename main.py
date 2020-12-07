import sys
from pathlib import Path
import glob

import os
import typer
import urllib
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import asyncio

from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from schemas.payload_predict_image import PayloadPredictImage
from schemas.response_single_label import ResponseSingleLabel
from handler.image_classifier import ImageClassifier

sys.path.append("/app")

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

learner = ImageClassifier(model_name="efficientnet_b2.pkl")
learner.initialize()


# TODO: Вопрос, нафига нужна была ассинхронная инициализация?
# async def setup_learner():
#     learner = ImageClassifier(model_name="efficientnet_b2.pkl")
#     learner.initialize()
#     return learner

# @app.on_event("startup")
# async def startup_event():
#     """Setup the learner on server start"""
#     global learner
#     loop = asyncio.get_event_loop()  # get event loop
#     tasks = [asyncio.ensure_future(setup_learner())]  # assign some task
#     learner = (await asyncio.gather(*tasks))[0]  # get tasks


@app.on_event("shutdown")
async def shutdown():
    """
    todo: dont worked
    """
    print("Stop and delete /tmp/download/*")
    files = glob.glob('/tmp/download/*')
    for f in files:
        os.remove(f)


@app.get('/')
async def homepage():
    html_content = (path / 'html/index.html').open().read()
    return HTMLResponse(content=html_content, status_code=200)


@app.post("/analyze")
async def analyze(file: bytes = File(...)):
    """
    For HTML form in homepage
    :param file:
    :return:
    """

    item = learner.handle(file)

    if item.label:
        return item.label
    else:
        return JSONResponse(status_code=404, content={"message": "Item not predicted"})


@app.post("/predictions/efficientnet")
async def predictions(payload: PayloadPredictImage):
    """
    Main api for predict
    :param file_url:
    :return:
    """

    print(payload)
    if payload.check_predicted_file_exist:
        print('Load existed payload')
        payload.load()
    else:
        try:
            file_path = payload.download()
        except urllib.error.HTTPError:
            return JSONResponse(status_code=404, content={"message": "Item not downloaded"})

        item = learner.handle(file_path)

        payload.predicted = item
        payload.export()

    if payload.predicted.label:
        # return payload.dict(exclude={'predicted': {'vector'}})
        return payload.dict()
    else:
        return JSONResponse(status_code=404, content={"message": "Item not predicted"})


app_typer = typer.Typer()


@app_typer.command()
def predict(url: str):
    """
    Run local with typer
    :param url:
    :return:
    """

    file_url = PayloadPredictImage(file_url=url)

    file_path = file_url.download()

    item = learner.handle(file_path)

    typer.echo(item.label)


if __name__ == "__main__":
    app_typer()
