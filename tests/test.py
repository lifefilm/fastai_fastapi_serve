import sys

from fastapi.testclient import TestClient

sys.path.append("/app")

from main import *

client = TestClient(app)

original = {
    "file_path": "/tmp/download/65/fb/65fbedf6995333b79e9254cf49420130",
    "file_path_pkl": "/tmp/download/65/fb/65fbedf6995333b79e9254cf49420130.pkl",
    "file_url": "https://github.com/lifefilm/fastai_fastapi_serve/raw/master/tests/test.jpg",
    "predicted": {
        "label": 1304,
        "probability": None
    }
}

payload_original = PayloadPredictImage(**original)


def test_post_predict_efficientnet():
    response = client.post(
        url="/predictions/efficientnet",
        json={"file_url": "https://github.com/lifefilm/fastai_fastapi_serve/raw/master/tests/test.jpg"}
    )
    print(response.json())

    payload = PayloadPredictImage(**response.json())

    assert response.status_code == 200
    assert payload == payload_original


def test_ping():
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"ping": "pong"}
