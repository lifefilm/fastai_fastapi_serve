from pathlib import Path

import os
import uuid

from iopath.common.download import download
from pydantic import AnyUrl
from core.config import settings

import hashlib
import requests


def get_hash_by_url(file_url, file_hash, dir=settings.PREDICTED_STORE):
    """
    File path hash function
    """

    assert file_url

    if not file_hash:
        file_hash = uuid.uuid3(uuid.NAMESPACE_URL, name=file_url).hex

    dir_hash = Path(f'{dir}/{file_hash[:2]}/{file_hash[2:4]}')
    file_hash = dir_hash / file_hash

    os.makedirs(dir_hash, exist_ok=True)

    return dir_hash, file_hash


def download_s3(image_url,
                dir=settings.PREDICTED_STORE,
                s3_url=''
                ):
    os.makedirs(dir, exist_ok=True)

    img_data = requests.get(s3_url + image_url)
    assert img_data

    m = hashlib.md5()
    for data in img_data.iter_content(8192):
        m.update(data)

    image_name = m.hexdigest()

    fpath = os.path.join(dir, image_name)

    if os.path.isfile(fpath):
        print("File {} exists! Skipping download.".format(image_url))
        return fpath

    with open(fpath, 'wb') as handler:
        handler.write(img_data.content)

    return image_name


def download_file(file_url: AnyUrl, new_file_name=None, dir=settings.PREDICTED_STORE):
    # print(f"Start download {file_url}")

    dir_hash, hash = get_hash_by_url(file_url, new_file_name, dir)
    _filename = dir_hash / hash

    # print(_filename)

    x = download(file_url, dir_hash, filename=_filename, progress=False)
    print('downloaded', x)

    assert os.path.isfile(_filename), f"File not downloaded {file_url}"

    return _filename
