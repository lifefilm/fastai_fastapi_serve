from pathlib import Path
import os
import time
from functools import lru_cache
from fastai.learner import load_learner

import torch
from abc import ABC

from pydantic import BaseModel

import logging

logger = logging.getLogger(__name__)


class BaseHandler(BaseModel, ABC):
    """
    Based on: https://github.com/pytorch/serve/blob/0956059a0037de4f74915d252a2b6bc8bd4dd505/ts/torch_handler/base_handler.py#L17
    Base default handler to load torchscript or eager mode [state_dict] models
    Also, provides handle method per torch serve custom model specification
    """

    model: str = None
    model_store: Path = Path("/app/models")
    model_name: str = None
    device: str = "cuda:0" if torch.cuda.is_available() else "cpu"
    initialized: bool = False
    properties: dict = {}
    # context: str = None

    def initialize(self):
        """
        Initialize function loads the model file and initialized the model object.
        """

        model_path_full = self.model_store / self.model_name

        if not os.path.isfile(model_path_full):
            raise RuntimeError(f"Missing the model file {model_path_full}")

        self.model = load_learner(model_path_full)
        self.model.dls.device = self.device
        print(self.model)

        logger.debug('Model file %s loaded successfully', model_path_full)

        self.initialized = True

    def inference(self, data, *args, **kwargs):
        """
        The Inference Function is used to make a prediction call on the given input request.
        """

        @lru_cache()
        def __predict(_data):
            return self.model.predict(_data)

        return __predict(data)

    def preprocess(self, data):
        """
        Preprocess function to convert the request input.
        """

        return data

    def postprocess(self, data):
        """
        The post process function makes use of the output from the inference and converts into
        """
        return data

    def handle(self, data):
        """
        Entry point for default handler. It takes the data from the input request and returns
           the predicted outcome for the input.
        """

        start_time = time.time()

        data = self.preprocess(data)
        data = self.inference(data)
        data = self.postprocess(data)

        duration = round((time.time() - start_time) * 1000, 2)
        logger.info(f'HandlerTime {duration}')

        return data




