from typing import Any

import numpy
from pydantic import BaseModel


class NumpyNDArray(numpy.ndarray):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v: Any) -> str:
        return v


class ResponseSingleLabel(BaseModel):
    label: int = None
    # vector: List[List[float]] = []
    vector: NumpyNDArray = None
    probability: float = None

