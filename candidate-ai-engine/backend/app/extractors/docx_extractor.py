import docx
from loguru import logger
from typing import Optional

class DOCXExtractor:
    @staticmethod
    def extract_text(file_path: str) -> Optional[str]:
        try:
            doc = docx.Document(file_path)
            full_text = []
            for para in doc.paragraphs:
                full_text.append(para.text)
            return '\n'.join(full_text)
        except Exception as e:
            logger.error(f"Failed to extract text from DOCX {file_path}: {e}")
            return None
