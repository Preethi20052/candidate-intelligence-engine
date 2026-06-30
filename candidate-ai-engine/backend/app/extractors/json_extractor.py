import json
from typing import List, Dict, Any

class JSONExtractor:
    @staticmethod
    def extract(file_path: str) -> List[Dict[str, Any]]:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return [data]
                elif isinstance(data, list):
                    return data
                return []
        except Exception:
            return []
