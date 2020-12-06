FROM nvidia/cuda:10.1-cudnn7-devel-ubuntu16.04
ARG PYTHON_VERSION=3.8
ARG WITH_TORCHVISION=1
RUN apt-get update && apt-get install -y --no-install-recommends \
         build-essential \
         cmake \
         git \
         curl \
         ca-certificates \
         libjpeg-dev \
         libpng-dev && \
     rm -rf /var/lib/apt/lists/*


RUN curl -o ~/miniconda.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
     chmod +x ~/miniconda.sh && \
     ~/miniconda.sh -b -p /opt/conda && \
     rm ~/miniconda.sh && \
     /opt/conda/bin/conda install -y python=$PYTHON_VERSION numpy pyyaml scipy ipython mkl mkl-include ninja cython typing && \
     /opt/conda/bin/conda install -y -c pytorch magma-cuda100 && \
     /opt/conda/bin/conda clean -ya

ENV PATH /opt/conda/bin:$PATH
# This must be done before pip so that requirements.txt is available

RUN /opt/conda/bin/conda install -y -c pytorch -c fastai cudatoolkit=10.1
#RUN /opt/conda/bin/conda  uninstall -y --force pillow libjpeg-turbo
RUN /opt/conda/bin/conda  install -c fastai/label/test pillow

RUN pip install pipenv
RUN pipenv --python=/opt/conda/bin/python --site-packages

RUN /opt/conda/bin/conda install -y -c pytorch -c fastai fastai==2.1.8

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt
RUN mkdir /app && cd /app

#Error: What? packages already exists?
#COPY ./Pipfile /app/Pipfile
#COPY ./Pipfile.lock /app/Pipfile.lock
#RUN pipenv lock -r > requirements.txt
#RUN pip install -r /requirements.txt

#RUN pipenv install --python=/opt/conda/bin/python --system --deploy --clear

WORKDIR /app
