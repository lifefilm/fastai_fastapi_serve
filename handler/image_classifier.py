from abc import ABC

from functools import lru_cache
from fastai.vision.all import *
from .base import BaseHandler
from schemas.response_single_label import ResponseSingleLabel


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

        assert img, "Where you image file?"

        features_hook = SaveFeatures(self.model.model[1][4])

        # img = PILImage.create(image_path)

        predicted =  self.model.predict(img)[0]

        print(predicted)

        features_array = np.array(features_hook.features)

        features_hook.remove()

        return predicted, features_array

    def postprocess(self, data) -> ResponseSingleLabel:

        pred, features_array = data
        item = ResponseSingleLabel()
        item.label = pred
        item.vector = features_array.tolist()

        return item





