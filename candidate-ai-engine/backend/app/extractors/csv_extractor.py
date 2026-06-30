import csv
from typing import List, Dict, Any

class CSVExtractor:
    @staticmethod
    def extract(file_path: str) -> List[Dict[str, Any]]:
        records = []
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append(row)
        return records