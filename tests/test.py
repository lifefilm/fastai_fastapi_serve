import sys

from fastapi.testclient import TestClient

sys.path.append("/app")

from main import *

client = TestClient(app)


def test_post_predict_efficientnet():
    response = client.post(
        url="/predictions/efficientnet",
        json={"file_url": "https://github.com/lifefilm/fastai_fastapi_serve/raw/master/tests/test.jpg"}
    )
    print(response.json())

    assert response.status_code == 200
    assert str(response.text) == '"1304"'


def test_ping():
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"ping": "pong"}
