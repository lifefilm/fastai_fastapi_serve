from functools import lru_cache
from typing import List

from fastapi import FastAPI, File, Form, UploadFile, Path
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastai.vision.all import *
import uvicorn
import asyncio
# import aiohttp
# import aiofiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.responses import JSONResponse

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
# REPLACE THIS WITH YOUR URL
export_url = ""
export_file_name = 'models/efficientnet_b2.pkl'


# async def download_file(url, dest):
#     if dest.exists():
#         return
#     async with aiohttp.ClientSession() as session:
#         async with session.get(url) as response:
#             if response.status == 200:
#                 f = await aiofiles.open(dest, mode='wb')
#                 await f.write(await response.read())
#                 await f.close()


class SaveFeatures:
    features = None

    def __init__(self, m):
        self.hook = m.register_forward_hook(self.hook_fn)
        self.features = None
        print('--- Start hook features extract!!! ---')

    def hook_fn(self, module, input, output):
        # out = output.detach().cpu().numpy()
        out = output.numpy()
        if isinstance(self.features, type(None)):
            self.features = out
        else:
            self.features = np.row_stack((self.features, out))

    def remove(self):
        del self.features
        self.hook.remove()


@lru_cache()
def feature_extractor(img):
    """
    Предсказания для новой картинки его класса и вытаскивание вектора-фичи
    из нижнего слоя длиной 512, через хук SaveFeatures
    """

    assert img

    features_hook = SaveFeatures(learn.model[1][4])

    # img = PILImage.create(image_path)

    predicted, _, _ = learn.predict(img)
    print(predicted)

    features_array = np.array(features_hook.features)
    print(features_array.shape)

    features_hook.remove()

    return predicted, features_array


async def setup_learner():
    # await download_file(export_url, path / export_file_name)
    try:
        learn = load_learner(path / export_file_name)
        learn.dls.device = 'cpu'
        return learn
    except RuntimeError as e:
        if len(e.args) > 0 and 'CPU-only machine' in e.args[0]:
            print(e)
            message = "\n\nThis model was trained with an old version of fastai and will not work in a CPU environment.\n\nPlease update the fastai library in your training environment and export your model again.\n\nSee instructions for 'Returning to work' at https://course.fast.ai."
            raise RuntimeError(message)
        else:
            raise


learn = None


@app.on_event("startup")
async def startup_event():
    """Setup the learner on server start"""
    global learn
    loop = asyncio.get_event_loop()  # get event loop
    tasks = [asyncio.ensure_future(setup_learner())]  # assign some task
    learn = (await asyncio.gather(*tasks))[0]  # get tasks


@app.get('/')
async def homepage():
    html_content = (path / 'html/index.html').open().read()
    return HTMLResponse(content=html_content, status_code=200)

from uuid import UUID, uuid4


class Predicted(BaseModel):
    label: int = 0
    vector: List[List[float]] = []



@app.post("/analyze")
async def analyze(file: bytes = File(...)):

    pred, features_array = feature_extractor(file)

    item = Predicted()
    item.label = pred
    item.vector = features_array.tolist()

    if item.label:
        return item.label
    else:
        return JSONResponse(status_code=404, content={"message": "Item not predicted"})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)
