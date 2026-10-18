from typing import Any, Dict
import cv2
import numpy as np

class ImagePipelineFilters:
    """Атомарные операции компьютерного зрения."""

    @staticmethod
    def denoise_gaussian(image: np.ndarray, kernel_size: int = 5, sigma: float = 1.0) -> np.ndarray:
        k = kernel_size if kernel_size % 2 != 0 else kernel_size + 1
        return cv2.GaussianBlur(image, (k, k), sigmaX=sigma)

    @staticmethod
    def denoise_nlmeans(image: np.ndarray, h: float = 10.0) -> np.ndarray:
        if len(image.shape) == 2:
            return cv2.fastNlMeansDenoising(image, None, h=h)
        return cv2.fastNlMeansDenoisingColored(image, None, h=h, hColor=h)

    @staticmethod
    def to_grayscale(image: np.ndarray) -> np.ndarray:
        if len(image.shape) == 2:
            return image
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

    @staticmethod
    def clahe(image: np.ndarray, clip_limit: float = 2.0, tile_grid_size: int = 8) -> np.ndarray:
        clahe_obj = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(tile_grid_size, tile_grid_size))
        if len(image.shape) == 3:
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            l_clahe = clahe_obj.apply(l)
            merged = cv2.merge((l_clahe, a, b))
            return cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)
        return clahe_obj.apply(image)

    @staticmethod
    def kmeans_quantization(image: np.ndarray, k: int = 8) -> np.ndarray:
        data = image.reshape((-1, 3)).astype(np.float32)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 0.2)
        _, labels, centers = cv2.kmeans(data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        centers = np.uint8(centers)
        quantized = centers[labels.flatten()]
        return quantized.reshape(image.shape)

    @staticmethod
    def edge_canny(image: np.ndarray, low_threshold: int = 50, high_threshold: int = 150) -> np.ndarray:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        edges = cv2.Canny(gray, threshold1=low_threshold, threshold2=high_threshold)
        return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

    @staticmethod
    def edge_sobel(image: np.ndarray, kernel_size: int = 3) -> np.ndarray:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        k = kernel_size if kernel_size % 2 != 0 else 3
        grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=k)
        grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=k)
        magnitude = cv2.magnitude(grad_x, grad_y)
        sobel_edges = np.uint8(np.clip(magnitude, 0, 255))
        return cv2.cvtColor(sobel_edges, cv2.COLOR_GRAY2BGR)
