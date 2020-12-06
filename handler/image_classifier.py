from abc import ABC

from functools import lru_cache
from fastai.vision.all import *
from .base import BaseHandler


class SaveFeatures:
    """
    Features hook for fastai
    Todo: exclude in features, rewrite
    """
    features = None

    def __init__(self, m):
        self.hook = m.register_forward_hook(self.hook_fn)
        self.features = None

    def hook_fn(self, module, input, output):
        device: str = "cuda:0" if torch.cuda.is_available() else "cpu"

        if device != 'cpu':
            out = output.detach().cpu().numpy()
        else:
            out = output.numpy()
        if isinstance(self.features, type(None)):
            self.features = out
        else:
            self.features = np.row_stack((self.features, out))

    def remove(self):
        del self.features
        self.hook.remove()


class ImageClassifier(BaseHandler, ABC):

    model_name: str = None
    device: str = "cuda:0" if torch.cuda.is_available() else "cpu"
    properties: dict = {}

    max_result_classes: int = 3

    def inference(self, img):
        """
        Предсказания для новой картинки его класса и вытаскивание вектора-фичи
        из нижнего слоя длиной 512, через хук SaveFeatures
        """

        assert img


        features_hook = SaveFeatures(self.model.model[1][4])

        # img = PILImage.create(image_path)

        predicted, _, _ = self.model.predict(img)

        print(predicted)

        features_array = np.array(features_hook.features)

        features_hook.remove()

        return predicted, features_array


