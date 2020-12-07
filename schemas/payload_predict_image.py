from pathlib import Path

import uuid

import pickle

import os

from pydantic import BaseModel, AnyUrl

from core.download import download_file, get_hash_by_url
from core.config import settings
from schemas.response_single_label import ResponseSingleLabel


class PayloadPredictImage(BaseModel):
    file_url: AnyUrl
    file_path: Path = None
    file_path_pkl: Path = None
    predicted: ResponseSingleLabel = None

    def download(self):
        if self.file_url:
            self.file_path = download_file(self.file_url, self.hash)
        return self.file_path

    @property
    def hash(self):
        return uuid.uuid3(uuid.NAMESPACE_URL, name=self.file_url).hex

    @property
    def file_hash_path(self, dir=settings.PREDICTED_STORE) -> Path:
        return get_hash_by_url(self.file_url, self.hash, dir=dir)[1]

    @property
    def file_hash_path_pkl(self) -> Path:
        if not self.file_path_pkl:
            self.file_path_pkl = Path(f'{self.file_hash_path}.pkl')
            return self.file_path_pkl
        else:
            return self.file_path_pkl

    @property
    def check_predicted_file_exist(self) -> bool:
        if self.file_hash_path_pkl.exists():
            return True

    def export(self, file_path=None) -> Path:
        """
        Save to disk pkl file with predicted vector and other metadata
        :param file_path:
        :return:
        """
        if (not file_path) and self.file_path:
            file_path = self.file_path
        else:
            raise FileNotFoundError

        with open(self.file_hash_path_pkl, 'wb') as f:
            print(f'export predicted: {self.file_hash_path_pkl}')
            pickle.dump(self, f)

        return self.file_hash_path_pkl

    def load(self, file_path=None):
        """
        Load pkl file into SuperClass with vector from hashed path genereated from "file_url"
        :param file_path:
        :return:
        """
        if not file_path:
            file_path = self.file_hash_path_pkl

        print(file_path)
        assert os.path.exists(file_path), f"Not founded {file_path} to load"
        with open(file_path, 'rb') as f:
            loaded: PayloadPredictImage = pickle.load(f)
        print(f'load predicted: {loaded.predicted.label}')
        super().__init__(**loaded.dict())
