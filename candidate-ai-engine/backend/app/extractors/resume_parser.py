import re
from typing import Dict, Any, List, Optional
from app.extractors.pdf_extractor import PDFExtractor
from app.normalizers.base import Normalizer
from loguru import logger


class ResumeParser:
    """
    Extracts structured data from unstructured resume files.
    Supports: PDF, DOCX, TXT
    Edge cases handled:
    - All-caps names (NAVEEN KUMAR)
    - Single-initial surnames (Naveen V)
    - Honorific prefixes (Dr., Mr., Ms., Prof., Er., Smt.)
    - Objective/summary/motivated lines falsely matching as names
    - Indian phone numbers (10-digit, +91, with/without spaces)
    - Multiple emails in resume
    - Salary in LPA/k/crore format
    - Fresher / entry-level experience detection
    - City extraction from Indian cities list
    """

    # Name pattern: supports single-char initials like "Naveen V" or "R K Sharma"
    NAME_PATTERN = re.compile(
        r'^[A-Z][a-zA-Z]+([\s][A-Z][a-zA-Z]*\.?){1,4}$'
    )

    # Hard skip words — lines containing these are NEVER a candidate name
    HARD_SKIP = re.compile(
        r'\b(objective|summary|profile|career|about|contact|address'
        r'|seeking|looking|motivated|dedicated|passionate|enthusiastic'
        r'|graduate|fresher|professional|experienced|skilled|aspiring'
        r'|engineer|developer|analyst|manager|designer|consultant'
        r'|curriculum|vitae|resume|bba|bca|bsc|mca|mba|msc|btech|mtech'
        r'|university|college|institute|school|bangalore|mumbai|delhi'
        r'|chennai|hyderabad|pune|noida|coimbatore|india)\b'
        r'|[@:/\\|•●\[\]{}]|http',
        re.IGNORECASE
    )

    def parse_file(self, file_path: str, ext: str,
                   filename_hint: str = "") -> Dict[str, Any]:
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

        return self._parse_text(text, filename_hint=filename_hint)

    # ------------------------------------------------------------------
    # Main Parse
    # ------------------------------------------------------------------
    def _parse_text(self, text: str, filename_hint: str = "") -> Dict[str, Any]:
        name    = self._extract_name(text, filename_hint)
        emails  = Normalizer.extract_emails(text)
        phones  = Normalizer.extract_phones(text)
        skills  = Normalizer.extract_skills_from_text(text)
        exp_yrs = self._extract_experience_years(text)
        location = self._extract_location(text)
        salary  = self._extract_expected_salary(text)
        links   = self._extract_links(text)

        profile: Dict[str, Any] = {
            "source_type": "resume",
            "full_name":   name,
            "emails":      emails,
            "phones":      phones,
            "skills":      skills,
        }
        if exp_yrs is not None:
            profile["experience_years"] = exp_yrs
        if location:
            profile["location"] = location
        if salary is not None:
            profile["expected_salary"] = salary
        if links:
            profile["links"] = links

        logger.info(
            f"Resume parsed — name={name!r}, emails={emails}, "
            f"phones={phones}, skills={len(skills)}, exp={exp_yrs}, loc={location}"
        )
        return profile

    # ------------------------------------------------------------------
    # Name Extraction — Most Critical
    # ------------------------------------------------------------------
    def _extract_name(self, text: str, filename_hint: str = "") -> str:
        """
        Multi-strategy name extraction:
        1. Try filename hint (e.g. "Naveen_V.pdf" → "Naveen V")
        2. Scan first 40 lines for a clean name-like line
        3. Return "Unknown" if all strategies fail
        """
        # Strategy 1: Extract from filename (most reliable signal)
        if filename_hint:
            name_from_file = self._name_from_filename(filename_hint)
            if name_from_file and name_from_file != "Unknown":
                logger.info(f"Name extracted from filename: {name_from_file!r}")
                return name_from_file

        # Strategy 2: Scan top lines of resume text
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        for line in lines[:40]:
            # Skip very long lines (paragraphs)
            if len(line) > 50:
                continue
            # Skip lines matching hard-skip patterns
            if self.HARD_SKIP.search(line):
                continue
            # Skip if too many digits (phone/ID/year)
            digit_count = len(re.sub(r'\D', '', line))
            if digit_count > 4:
                continue
            # Skip lines with non-name punctuation
            if any(c in line for c in [',', ';', '(', ')', '+', '=', '_', '"', "'"]):
                continue
            # Skip very short words (likely single-word section headers)
            words = line.split()
            if len(words) < 2:
                continue

            # Normalize casing: all-caps → title case
            candidate = line.title() if line.isupper() else line
            candidate_clean = Normalizer.normalize_name(candidate)
            if not candidate_clean or len(candidate_clean) < 5:
                continue

            # Check name pattern (allows single-char initials)
            if self.NAME_PATTERN.match(candidate_clean):
                logger.info(f"Name extracted from text: {candidate_clean!r}")
                return candidate_clean

        logger.warning("Could not extract name from resume text or filename")
        return "Unknown"

    def _name_from_filename(self, filename: str) -> str:
        """
        Extract candidate name from filename.
        e.g. "Naveen_V.pdf" → "Naveen V"
             "naveen_kumar_resume.pdf" → "Naveen Kumar"
             "Resume_2024.pdf" → skip (generic filename)
        """
        # Remove extension
        stem = re.sub(r'\.[a-zA-Z0-9]+$', '', filename).strip()
        # Replace underscores, hyphens, dots with spaces
        stem = re.sub(r'[_\-.]', ' ', stem)
        # Remove common generic words and job titles
        stem = re.sub(
            r'\b(resume|cv|curriculum|vitae|updated|new|final|copy'
            r'|engineer|developer|designer|manager|intern|fresher|analyst'
            r'|software|backend|frontend|fullstack|data|ai|ml|tech'
            r'|flowcv|novoresume|canva|zety|europass'
            r'|\d{4}|\d{2}|\d{8})\b',
            '', stem, flags=re.IGNORECASE
        ).strip()
        # Clean up extra spaces
        stem = ' '.join(stem.split())
        if not stem or len(stem) < 4:
            return "Unknown"
        # Must look like a name
        candidate = Normalizer.normalize_name(stem)
        if candidate and self.NAME_PATTERN.match(candidate):
            return candidate
        return "Unknown"

    # ------------------------------------------------------------------
    # Experience Years
    # ------------------------------------------------------------------
    def _extract_experience_years(self, text: str) -> Optional[float]:
        """
        Handles: "2 years", "2+ years", "2.5 years exp",
                 "Fresher", "Entry Level", "0-1 years", "Less than 1 year"
        """
        text_l = text.lower()
        if re.search(r'\b(fresher|fresh graduate|entry.?level|no experience'
                     r'|0 year|less than 1)\b', text_l):
            return 0.0

        m = re.search(r'(\d+\.?\d*)\s*\+?\s*years?\s*(of\s*)?(experience|exp)',
                      text, re.IGNORECASE)
        if m:
            return float(m.group(1))

        m = re.search(r'(experience|exp)[:\s]+(\d+\.?\d*)', text, re.IGNORECASE)
        if m:
            return float(m.group(2))

        return None

    # ------------------------------------------------------------------
    # Location
    # ------------------------------------------------------------------
    def _extract_location(self, text: str) -> str:
        """
        Extract city/location from resume.
        Checks explicit labels first, then scans for Indian city names.
        """
        # Explicit: "Location: Bangalore" or "City: Mumbai, India"
        m = re.search(
            r'(location|city|address|place|based\s*at)[:\s]+([A-Za-z][a-zA-Z\s,]{2,30}?)(?:\n|,|$)',
            text, re.IGNORECASE
        )
        if m:
            loc = m.group(2).strip().rstrip(',').strip()
            if 4 <= len(loc) <= 40:
                return loc.title()

        # Scan for known Indian cities
        CITIES = [
            'Bangalore', 'Bengaluru', 'Mumbai', 'Delhi', 'New Delhi',
            'Hyderabad', 'Chennai', 'Pune', 'Kolkata', 'Ahmedabad',
            'Jaipur', 'Noida', 'Gurugram', 'Gurgaon', 'Kochi',
            'Coimbatore', 'Surat', 'Vadodara', 'Bhopal', 'Indore',
            'Nagpur', 'Visakhapatnam', 'Mysore', 'Mangalore',
            'Thiruvananthapuram', 'Bhubaneswar', 'Patna', 'Lucknow',
        ]
        for city in CITIES:
            if re.search(r'\b' + re.escape(city) + r'\b', text, re.IGNORECASE):
                return city
        return ""

    # ------------------------------------------------------------------
    # Expected Salary
    # ------------------------------------------------------------------
    def _extract_expected_salary(self, text: str) -> Optional[float]:
        """
        Handles: "Expected Salary: 7 LPA", "CTC: 8.5L",
                 "Salary: 7,00,000", "Expected: 85k"
        """
        patterns = [
            r'(expected|desired|target|current)\s*(?:ctc|salary|package)[:\s]*([\d,.\s]+(?:lpa|l|cr|lakhs?|crore|k)?)',
            r'(?:ctc|salary|package)[:\s]*([\d,.\s]+(?:lpa|l|cr|lakhs?|crore|k)?)',
            r'([\d,.\s]+(?:lpa|l))\s*(?:per annum|pa\b)',
        ]
        for pat in patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                raw = m.group(m.lastindex)
                result = Normalizer.normalize_salary(raw)
                if result and result > 0:
                    return result
        return None

    # ------------------------------------------------------------------
    # Links (GitHub / LinkedIn)
    # ------------------------------------------------------------------
    def _extract_links(self, text: str) -> List[str]:
        """Extract GitHub and LinkedIn profile URLs from resume."""
        url_pattern = re.compile(
            r'https?://(?:www\.)?(?:github\.com|linkedin\.com)/[^\s\n,;>"\']+'
        )
        return list(set(url_pattern.findall(text)))
