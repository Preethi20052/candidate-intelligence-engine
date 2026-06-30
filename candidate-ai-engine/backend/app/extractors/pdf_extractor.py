import fitz  # PyMuPDF
from loguru import logger
from typing import Optional

class PDFExtractor:
    @staticmethod
    def extract_text(file_path: str) -> Optional[str]:
        """Extracts raw text from a PDF file."""
        try:
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text("text") + "\n"
            doc.close()
            return text
        except Exception as e:
            logger.error(f"Failed to extract text from PDF {file_path}: {e}")
            return None
