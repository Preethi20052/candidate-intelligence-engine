import re
from typing import Dict, Any, List
from app.extractors.pdf_extractor import PDFExtractor
from app.normalizers.base import Normalizer
from loguru import logger


class ResumeParser:
    """
    Extracts structured data from unstructured resume files.
    Supports: PDF, DOCX, TXT
    Handles edge cases: all-caps names, various phone/email formats,
    honorific prefixes, multi-format skill lists.
    """

    # Regex: name-like line — 2 to 5 words, each starting with a capital
    NAME_PATTERN = re.compile(r'^[A-Z][a-zA-Z]+([\s][A-Z][a-zA-Z.]+){1,4}$')

    # Lines to skip when looking for the candidate name
    SKIP_PATTERNS = re.compile(
        r'(@|http|linkedin|github|://'
        r'|curriculum|vitae|resume|cv\b'
        r'|objective|summary|profile|skills'
        r'|experience|education|contact|address'
        r'|[|/\\:+•●])',
        re.IGNORECASE
    )

    def parse_file(self, file_path: str, ext: str) -> Dict[str, Any]:
        text = ""
        ext = ext.lower()
        try:
            if ext == '.pdf':
                text = PDFExtractor.extract_text(file_path)
            elif ext == '.docx':
                from app.extractors.docx_extractor import DOCXExtractor
                text = DOCXExtractor.extract_text(file_path)
            elif ext in ('.txt', '.text'):
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read()
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            return {}

        if not text or not text.strip():
            logger.warning(f"Empty text extracted from: {file_path}")
            return {}

        return self._parse_text(text)

    def _parse_text(self, text: str) -> Dict[str, Any]:
        emails  = Normalizer.extract_emails(text)
        phones  = Normalizer.extract_phones(text)
        name    = self._extract_name(text)
        skills  = Normalizer.extract_skills_from_text(text)
        exp_yrs = self._extract_experience_years(text)
        location= self._extract_location(text)
        salary  = self._extract_expected_salary(text)

        profile = {
            "source_type"     : "resume",
            "full_name"       : name,
            "emails"          : emails,
            "phones"          : phones,
            "skills"          : skills,
        }
        if exp_yrs is not None:
            profile["experience_years"] = exp_yrs
        if location:
            profile["location"] = location
        if salary is not None:
            profile["expected_salary"] = salary

        logger.info(
            f"Resume parsed — name={name!r}, emails={emails}, "
            f"phones={phones}, skills={len(skills)}, exp={exp_yrs}"
        )
        return profile

    # ------------------------------------------------------------------
    # Name Extraction
    # ------------------------------------------------------------------
    def _extract_name(self, text: str) -> str:
        """
        Heuristic name extraction from the top of a resume.
        - Skips lines with emails, phones, URLs, section headings
        - Handles all-caps names (NAVEEN KUMAR)
        - Strips honorifics (Dr., Mr., Ms.)
        - Matches 2–5 capitalized words
        """
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        for line in lines[:20]:
            if self.SKIP_PATTERNS.search(line):
                continue
            # Skip if mostly digits (phone/zip)
            if len(re.sub(r'\D', '', line)) > 5:
                continue
            # Normalize all-caps line before matching
            candidate = line.title() if line.isupper() else line
            # Remove honorifics
            candidate_clean = Normalizer.normalize_name(candidate)
            if not candidate_clean:
                continue
            # Check it looks like a name
            if self.NAME_PATTERN.match(candidate_clean):
                return candidate_clean
        return Normalizer.normalize_name(lines[0]) if lines else "Unknown"

    # ------------------------------------------------------------------
    # Experience Years
    # ------------------------------------------------------------------
    def _extract_experience_years(self, text: str) -> Any:
        """
        Extract years of experience from resume text.
        Handles: "2 years experience", "2+ years", "Fresher", "Entry Level"
        """
        # Fresher / Entry level
        if re.search(r'\b(fresher|fresh graduate|entry.?level|no experience)\b', text, re.IGNORECASE):
            return 0.0

        # Explicit mention: "5 years of experience"
        m = re.search(r'(\d+\.?\d*)\s*\+?\s*years?\s*(of\s*)?(experience|exp)', text, re.IGNORECASE)
        if m:
            return float(m.group(1))

        # "Experience: 3 years"
        m = re.search(r'(experience|exp)[:\s]+(\d+\.?\d*)', text, re.IGNORECASE)
        if m:
            return float(m.group(2))

        return None

    # ------------------------------------------------------------------
    # Location
    # ------------------------------------------------------------------
    def _extract_location(self, text: str) -> str:
        """Extract city/location from resume."""
        # Look for "Location: Bangalore" or "City: Mumbai"
        m = re.search(r'(location|city|address)[:\s]+([A-Z][a-zA-Z\s,]+?)(?:\n|$)',
                      text, re.IGNORECASE)
        if m:
            return m.group(2).strip().split('\n')[0].strip()

        # Common Indian cities mentioned in resume
        cities = [
            'Bangalore', 'Bengaluru', 'Mumbai', 'Delhi', 'Hyderabad',
            'Chennai', 'Pune', 'Kolkata', 'Ahmedabad', 'Jaipur',
            'Noida', 'Gurugram', 'Gurgaon', 'Kochi', 'Coimbatore',
        ]
        for city in cities:
            if re.search(r'\b' + city + r'\b', text, re.IGNORECASE):
                return city
        return ""

    # ------------------------------------------------------------------
    # Expected Salary
    # ------------------------------------------------------------------
    def _extract_expected_salary(self, text: str) -> Any:
        """Extract expected salary from resume text."""
        m = re.search(
            r'(expected|desired|current|ctc)[^\n]*salary[:\s]*([\d,.\s]+(?:lpa|l|lakhs?|k)?)',
            text, re.IGNORECASE
        )
        if m:
            return Normalizer.normalize_salary(m.group(2))

        m = re.search(
            r'salary[:\s]*([\d,.\s]+(?:lpa|l|lakhs?|k)?)',
            text, re.IGNORECASE
        )
        if m:
            return Normalizer.normalize_salary(m.group(1))

        return None
