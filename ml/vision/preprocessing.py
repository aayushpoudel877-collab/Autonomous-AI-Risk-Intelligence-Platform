import numpy as np

def normalize_image(image: np.ndarray) -> np.ndarray:
    array=np.asarray(image, dtype=np.float32)
    if array.ndim not in (2,3): raise ValueError("image must be 2D or 3D")
    if array.max() > 1: array=array/255.0
    return np.clip(array,0,1)

def image_statistics(image: np.ndarray) -> dict[str,float]:
    x=normalize_image(image)
    return {"mean":float(x.mean()),"std":float(x.std()),"max":float(x.max()),"min":float(x.min())}
