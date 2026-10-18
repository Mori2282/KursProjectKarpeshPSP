from typing import List, Dict, Any
import requests

class APIClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url

    def upload_images(self, file_paths: List[str], pipeline_config: List[Dict[str, Any]]) -> Dict[str, Any]:
        url = f"{self.base_url}/tasks/upload"
        opened_files = [("files", open(p, "rb")) for p in file_paths]
        data = {"pipeline_config": requests.compat.json.dumps(pipeline_config)}
        try:
            response = requests.post(url, data=data, files=opened_files, timeout=30)
            response.raise_for_status()
            return response.json()
        finally:
            for _, f in opened_files:
                f.close()

    def get_all_tasks(self) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/tasks"
        response = requests.get(url, timeout=4)
        response.raise_for_status()
        return response.json()

    def download_image(self, task_id: str, destination_path: str) -> None:
        url = f"{self.base_url}/tasks/{task_id}/download"
        with requests.get(url, stream=True, timeout=30) as r:
            r.raise_for_status()
            with open(destination_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
