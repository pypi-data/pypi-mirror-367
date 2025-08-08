
import cv2
import numpy as np
from typing import Tuple, Optional

class NeighborhoodOperations:   
    def __init__(self, image: np.ndarray):
        self.image = image
        
    def averaging_filter(self, ksize: Tuple[int, int] = (3, 3)) -> np.ndarray:
        return cv2.blur(self.image, ksize)
    
    def gaussian_filter(self, ksize: Tuple[int, int] = (5, 5), sigma: float = 0) -> np.ndarray:
        return cv2.GaussianBlur(self.image, ksize, sigma)
    
    def median_filter(self, ksize: int = 3) -> np.ndarray:
        return cv2.medianBlur(self.image, ksize)
    
    def bilateral_filter(self, d: int = 9, sigma_color: float = 75, sigma_space: float = 75) -> np.ndarray:
        return cv2.bilateralFilter(self.image, d, sigma_color, sigma_space)
    
    def custom_filter(self, kernel: np.ndarray) -> np.ndarray:
        return cv2.filter2D(self.image, -1, kernel)
    
    def sharpen(self) -> np.ndarray:
        kernel = np.array([[0, -1, 0],
                          [-1, 5, -1],
                          [0, -1, 0]])
        return self.custom_filter(kernel)
    
    def edge_detect_sobel(self) -> np.ndarray:
        grad_x = cv2.Sobel(self.image, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(self.image, cv2.CV_64F, 0, 1, ksize=3)
        return np.uint8(np.sqrt(grad_x**2 + grad_y**2))
    
    def edge_detect_laplacian(self) -> np.ndarray:
        return cv2.Laplacian(self.image, cv2.CV_64F).astype(np.uint8)
    
    def emboss(self) -> np.ndarray:
        kernel = np.array([[-2, -1, 0],
                          [-1, 1, 1],
                          [0, 1, 2]])
        return self.custom_filter(kernel)

class LowPassFilters:
    
    @staticmethod
    def ideal_lowpass(image: np.ndarray, cutoff: int = 30) -> np.ndarray:
        dft = np.fft.fft2(image)
        dft_shift = np.fft.fftshift(dft)
        
        rows, cols = image.shape
        crow, ccol = rows // 2, cols // 2
        
        mask = np.zeros((rows, cols), np.uint8)
        mask[crow-cutoff:crow+cutoff, ccol-cutoff:ccol+cutoff] = 1
        
        fshift = dft_shift * mask
        img_back = np.fft.ifft2(np.fft.ifftshift(fshift))
        return np.uint8(np.abs(img_back))

class HighPassFilters:
    @staticmethod
    def ideal_highpass(image: np.ndarray, cutoff: int = 30) -> np.ndarray:
        dft = np.fft.fft2(image)
        dft_shift = np.fft.fftshift(dft)
        
        rows, cols = image.shape
        crow, ccol = rows // 2, cols // 2
        
        mask = np.ones((rows, cols), np.uint8)
        mask[crow-cutoff:crow+cutoff, ccol-cutoff:ccol+cutoff] = 0
        
        fshift = dft_shift * mask
        img_back = np.fft.ifft2(np.fft.ifftshift(fshift))
        return np.uint8(np.abs(img_back))

def apply_filter(image: np.ndarray, filter_type: str, **kwargs) -> np.ndarray:

    operations = NeighborhoodOperations(image)
    
    filter_map = {
        'averaging': operations.averaging_filter,
        'gaussian': operations.gaussian_filter,
        'median': operations.median_filter,
        'bilateral': operations.bilateral_filter,
        'sharpen': operations.sharpen,
        'sobel': operations.edge_detect_sobel,
        'laplacian': operations.edge_detect_laplacian,
        'emboss': operations.emboss
    }
    
    if filter_type in filter_map:
        return filter_map[filter_type](**kwargs)
    else:
        raise ValueError(f"Unknown filter type: {filter_type}")
