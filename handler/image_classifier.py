from abc import ABC

from functools import lru_cache
from fastai.vision.all import *
from .base import BaseHandler
from schemas.response_single_label import ResponseSingleLabel


class ImageClassifier(BaseHandler, ABC):

    model_name: str = None

    def postprocess(self, data) -> ResponseSingleLabel:

        item = ResponseSingleLabel(label=data)

        return item





