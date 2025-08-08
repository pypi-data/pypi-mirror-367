
import cv2
import numpy as np
from typing import Union, Tuple, Optional

def load_image(image_path: str, grayscale: bool = False) -> np.ndarray:
    flag = cv2.IMREAD_GRAYSCALE if grayscale else cv2.IMREAD_COLOR
    image = cv2.imread(image_path, flag)
    if image is None:
        raise FileNotFoundError(f"Image not found: {image_path}")
    return image

def save_image(image: np.ndarray, output_path: str) -> bool:
    return cv2.imwrite(output_path, image)

def show_image(title: str, image: np.ndarray, wait: bool = True) -> None:
    cv2.imshow(title, image)
    if wait:
        cv2.waitKey(0)
        cv2.destroyAllWindows()

def resize_image(image: np.ndarray, width: int = None, height: int = None) -> np.ndarray:
    if width is None and height is None:
        return image
    
    h, w = image.shape[:2]
    if width is None:
        ratio = height / float(h)
        width = int(w * ratio)
    elif height is None:
        ratio = width / float(w)
        height = int(h * ratio)
    
    return cv2.resize(image, (width, height))

def get_image_info(image: np.ndarray) -> dict:
    if len(image.shape) == 3:
        height, width, channels = image.shape
    else:
        height, width = image.shape
        channels = 1
    
    return {
        'width': width,
        'height': height,
        'channels': channels,
        'dtype': str(image.dtype),
        'min_value': np.min(image),
        'max_value': np.max(image),
        'mean_value': np.mean(image)
    }
