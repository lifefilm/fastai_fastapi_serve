from typing import List

from pydantic import BaseModel, AnyUrl, FilePath

from core.utils import download_file


class ResponseSingleLabel(BaseModel):
    label: int = None
    vector: List[List[float]] = []
    probability: float = None


class PayloadPredictImage(BaseModel):
    file_url: AnyUrl
    file_path: FilePath = None

    def download(self):
        if self.file_url:
            self.file_path = download_file(self.file_url)
        return self.file_path

