from typing import List, Dict, Any
import cv2
from pipelines.filters import ImagePipelineFilters

class PipelineExecutor:
    """Последовательный конвейерный обработчик."""

    FILTER_DISPATCH = {
        "denoise_gaussian": ImagePipelineFilters.denoise_gaussian,
        "denoise_nlmeans": ImagePipelineFilters.denoise_nlmeans,
        "grayscale": ImagePipelineFilters.to_grayscale,
        "clahe": ImagePipelineFilters.clahe,
        "kmeans": ImagePipelineFilters.kmeans_quantization,
        "canny": ImagePipelineFilters.edge_canny,
        "sobel": ImagePipelineFilters.edge_sobel,
    }

    @classmethod
    def process(cls, input_path: str, output_path: str, steps: List[Dict[str, Any]]) -> None:
        image = cv2.imread(input_path)
        if image is None:
            raise FileNotFoundError(f"Файл не найден или поврежден: {input_path}")

        current_img = image.copy()

        for step in steps:
            name = step.get("name")
            params = step.get("params", {})
            
            if name not in cls.FILTER_DISPATCH:
                raise ValueError(f"Неизвестный шаг конвейера: {name}")

            filter_func = cls.FILTER_DISPATCH[name]
            current_img = filter_func(current_img, **params)

        if not cv2.imwrite(output_path, current_img):
            raise IOError(f"Не удалось записать файл: {output_path}")
