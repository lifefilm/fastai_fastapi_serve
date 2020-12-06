from pathlib import Path

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

import uvicorn
import asyncio

from fastapi.middleware.cors import CORSMiddleware
from pydantic import AnyUrl
from starlette.responses import JSONResponse

from schemas.predict_response import ResponseSingleLabel, PayloadPredictImage
from handler.image_classifier import ImageClassifier

app = FastAPI()
app.mount("/static", StaticFiles(directory="html"), name="static")

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


@app.on_event("startup")
async def startup_event():
    """Setup the learner on server start"""
    global learner
    loop = asyncio.get_event_loop()  # get event loop
    tasks = [asyncio.ensure_future(setup_learner())]  # assign some task
    learner = (await asyncio.gather(*tasks))[0]  # get tasks


@app.get('/')
async def homepage():
    html_content = (path / 'html/index.html').open().read()
    return HTMLResponse(content=html_content, status_code=200)


@app.post("/analyze")
async def analyze(file: bytes = File(...)):
    pred, features_array = learner.predict(file)

    item = ResponseSingleLabel()
    item.label = pred
    item.vector = features_array.tolist()

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

    pred, features_array = learner.predict(file_path)

    item = ResponseSingleLabel()
    item.label = pred
    item.vector = features_array.tolist()

    if item.label:
        return item.label
    else:
        return JSONResponse(status_code=404, content={"message": "Item not predicted"})


