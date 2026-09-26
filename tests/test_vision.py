import numpy as np
from ml.vision.preprocessing import image_statistics, normalize_image

def test_image_normalization():
    x=normalize_image(np.array([[0,255]], dtype=np.uint8))
    assert x.min() == 0 and x.max() == 1

def test_image_statistics():
    stats=image_statistics(np.zeros((4,4,3)))
    assert stats["mean"] == 0 and stats["std"] == 0
