# FastAi server for models


* FastAI 2.1
* Pytorch 1.7  
* FastApi 0.6
* Docker (docker-compose)
* Python 3.8 (conda)

on GPU Cuda 10.1



## install && run

```python

docker-compose build 
docker-compose up 

```

Download from docker hub https://hub.docker.com/repository/docker/lifefilm/fastai2_fastapi

## testing


```bash

docker-compose run --rm neural pytest -s

#or manual

curl -i --data '{"file_url":"https://github.com/lifefilm/fastai_fastapi_serve/raw/master/tests/test.jpg"}' http://localhost:8001/predictions/efficientnet

#or https://httpie.io/
apt-get install httpie  
http --json POST  http://localhost:8001/predictions/efficientnet file_url=https://github.com/lifefilm/fastai_fastapi_serve/raw/master/tests/test.jpg

```

## Based on ideas

* https://github.com/muellerzr/fastai-v3-Render
* https://github.com/pytorch/serve