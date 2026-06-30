import re
from typing import Dict, Any, List
from app.extractors.pdf_extractor import PDFExtractor
from app.normalizers.base import Normalizer
from loguru import logger

class ResumeParser:
    def __init__(self):
        # Basic regex patterns for extraction
        self.email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        # Simple phone pattern matching E.164-like and US formats roughly
        self.phone_pattern = re.compile(r'\+?\d{1,3}?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')

    def parse_file(self, file_path: str, ext: str) -> Dict[str, Any]:
        text = ""
        if ext == '.pdf':
            text = PDFExtractor.extract_text(file_path)
        elif ext == '.docx':
            from app.extractors.docx_extractor import DOCXExtractor
            text = DOCXExtractor.extract_text(file_path)
        elif ext == '.txt':
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()

        if not text:
            return {}
        
        return self._parse_text(text, source_name=file_path)

    def _parse_text(self, text: str, source_name: str) -> Dict[str, Any]:
        emails = self._extract_emails(text)
        phones = self._extract_phones(text)
        
        # In a real system, we would use SpaCy or LLM for extracting skills, experience, etc.
        # Here we mock basic extractions to keep it deterministic and fast
        
        profile = {
            "source_type": "resume",
            "emails": [Normalizer.normalize_email(e) for e in emails],
            "phones": [Normalizer.normalize_phone(p) for p in phones],
            # Mocking name extraction for demonstration
            "full_name": "Extracted Name", 
            "skills": [] 
        }
        
        return profile

    def _extract_emails(self, text: str) -> List[str]:
        return list(set(self.email_pattern.findall(text)))

    def _extract_phones(self, text: str) -> List[str]:
        return list(set(self.phone_pattern.findall(text)))
