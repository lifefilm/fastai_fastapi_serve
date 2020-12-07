import sys

from fastapi.testclient import TestClient

sys.path.append("/app")

from main import app

client = TestClient(app)


def test_post_predict():
    response = client.post(
        url="/predictions/efficientnet",
        json={"file_url": "https://s3.posred.pro/media/order_image/82673/order_kQLUjia.jpeg"}
    )
    print(response.json())

    assert response.status_code == 200



def test_ping():
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"ping": "pong"}
