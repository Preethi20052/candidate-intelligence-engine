import re
import phonenumbers
import pycountry
from loguru import logger
from typing import List, Optional

# ---------------------------------------------------------------------------
# SKILL ALIASES – maps common abbreviations to canonical names
# ---------------------------------------------------------------------------
SKILL_ALIASES = {
    "ml": "Machine Learning",
    "dl": "Deep Learning",
    "ai": "Artificial Intelligence",
    "nlp": "Natural Language Processing",
    "cv": "Computer Vision",
    "js": "JavaScript",
    "ts": "TypeScript",
    "py": "Python",
    "k8s": "Kubernetes",
    "tf": "TensorFlow",
    "pt": "PyTorch",
    "gcp": "Google Cloud Platform",
    "aws": "Amazon Web Services",
    "az": "Microsoft Azure",
    "pg": "PostgreSQL",
    "mongo": "MongoDB",
    "rb": "Ruby",
    "oop": "Object Oriented Programming",
    "dsa": "Data Structures & Algorithms",
    "rest": "REST API",
    "ci/cd": "CI/CD",
    "devops": "DevOps",
    "llm": "Large Language Models",
}

# Canonical skill keyword list (case-insensitive match in resume text)
SKILL_KEYWORDS = [
    "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Go", "Rust",
    "PHP", "Ruby", "Swift", "Kotlin", "Scala", "R", "MATLAB", "Shell",
    "FastAPI", "Flask", "Django", "Spring Boot", "React", "Angular", "Vue",
    "Node.js", "Streamlit", "Next.js", "Express",
    "SQL", "MySQL", "PostgreSQL", "MongoDB", "Redis", "SQLite", "Cassandra",
    "Oracle", "DynamoDB", "Elasticsearch", "Neo4j",
    "Machine Learning", "Deep Learning", "NLP", "Computer Vision",
    "Data Science", "Data Engineering", "Artificial Intelligence",
    "Large Language Models", "LLM", "Generative AI", "Prompt Engineering",
    "Docker", "Kubernetes", "AWS", "GCP", "Azure", "CI/CD", "Jenkins",
    "Terraform", "Ansible", "GitHub Actions",
    "TensorFlow", "PyTorch", "Scikit-learn", "Pandas", "NumPy",
    "Matplotlib", "Seaborn", "Hugging Face", "LangChain",
    "Git", "GitHub", "Linux", "REST API", "GraphQL", "Kafka",
    "Spark", "Hadoop", "Airflow", "dbt",
    "HTML", "CSS", "Bootstrap", "Tailwind",
    "Power BI", "Tableau", "Excel", "Looker",
    "Agile", "Scrum", "JIRA", "DevOps",
    "Object Oriented Programming", "Data Structures", "Algorithms",
    "System Design", "Microservices", "Cloud Computing",
]


class Normalizer:

    # -----------------------------------------------------------------------
    # EMAIL
    # -----------------------------------------------------------------------
    @staticmethod
    def normalize_email(email: str) -> str:
        """
        Normalize an email address:
        - Strip whitespace
        - Lowercase
        - Validate format (RFC 5322 simplified)
        Returns empty string for invalid emails.
        """
        if not email or not isinstance(email, str):
            return ""
        email = email.strip().lower()
        # Remove surrounding quotes or angle brackets e.g. <john@example.com>
        email = re.sub(r'^[<"\']|[>"\']\s*$', '', email)
        # Validate basic RFC format
        pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9._%+\-]*[a-zA-Z0-9])?@[a-zA-Z0-9\-]+(\.[a-zA-Z0-9\-]+)*\.[a-zA-Z]{2,}$'
        if re.match(pattern, email):
            return email
        logger.debug(f"Invalid email discarded: {email}")
        return ""

    @staticmethod
    def extract_emails(text: str) -> List[str]:
        """Extract and deduplicate all valid emails from arbitrary text."""
        pattern = r'[a-zA-Z0-9][a-zA-Z0-9._%+\-]*@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}'
        raw = re.findall(pattern, text)
        seen, result = set(), []
        for e in raw:
            norm = Normalizer.normalize_email(e)
            if norm and norm not in seen:
                seen.add(norm)
                result.append(norm)
        return result

    # -----------------------------------------------------------------------
    # PHONE
    # -----------------------------------------------------------------------
    @staticmethod
    def normalize_phone(phone: str, default_regions: List[str] = None) -> str:
        """
        Normalize phone number to E.164 format.
        Tries multiple regions: India first (most likely), then US, UK, UAE.
        Returns original stripped string if all parses fail.
        """
        if not phone or not isinstance(phone, str):
            return ""
        # Strip non-essential chars
        phone = phone.strip()
        # Remove extension fragments like "x123" or "ext 123"
        phone = re.sub(r'\s*(x|ext\.?)\s*\d+', '', phone, flags=re.IGNORECASE)
        # Remove spaces, common separators for clean parsing
        phone_clean = re.sub(r'[\s\-().\/]', '', phone)

        if not phone_clean or len(re.sub(r'\D', '', phone_clean)) < 7:
            return ""

        regions = default_regions or ["IN", "US", "GB", "AE", None]
        for region in regions:
            try:
                parsed = phonenumbers.parse(phone, region)
                if phonenumbers.is_valid_number(parsed):
                    return phonenumbers.format_number(
                        parsed, phonenumbers.PhoneNumberFormat.E164
                    )
            except phonenumbers.NumberParseException:
                continue

        logger.warning(f"Could not normalize phone to E.164: {phone}")
        return phone_clean  # Return cleaned raw as fallback

    @staticmethod
    def extract_phones(text: str) -> List[str]:
        """
        Extract all phone numbers from arbitrary text.
        Handles: Indian (10-digit), international (+CC), US, embedded in text.
        """
        patterns = [
            r'\+?\d{1,3}[\s\-.]?\(?\d{2,4}\)?[\s\-.]?\d{3,4}[\s\-.]?\d{3,4}',  # International
            r'\b[6-9]\d{9}\b',   # Indian 10-digit mobile (starts 6-9)
            r'\b0\d{10}\b',      # Indian with leading 0
        ]
        seen, result = set(), []
        for pattern in patterns:
            for match in re.finditer(pattern, text):
                raw = match.group().strip()
                norm = Normalizer.normalize_phone(raw)
                if norm and norm not in seen:
                    seen.add(norm)
                    result.append(norm)
        return result

    # -----------------------------------------------------------------------
    # NAME
    # -----------------------------------------------------------------------
    @staticmethod
    def normalize_name(name: str) -> str:
        """
        Normalize a candidate name:
        - Strip whitespace
        - Remove honorifics (Mr, Mrs, Ms, Dr, Prof)
        - Title-case
        - Handle all-caps (NAVEEN KUMAR -> Naveen Kumar)
        """
        if not name or not isinstance(name, str):
            return ""
        name = name.strip()
        # Remove honorifics
        name = re.sub(
            r'^(Mr\.?|Mrs\.?|Ms\.?|Miss\.?|Dr\.?|Prof\.?|Er\.?)\s+',
            '', name, flags=re.IGNORECASE
        ).strip()
        if not name:
            return ""
        # If all caps or all lower, title-case it
        if name.isupper() or name.islower():
            name = name.title()
        else:
            # Title-case each word preserving existing mixed-case
            name = " ".join(w[0].upper() + w[1:] if w else w for w in name.split())
        return name

    @staticmethod
    def combine_name_parts(first: str, last: str, middle: str = "") -> str:
        """Combine first/middle/last name fields into a single full name."""
        parts = [p.strip() for p in [first, middle, last] if p and p.strip()]
        return Normalizer.normalize_name(" ".join(parts))

    # -----------------------------------------------------------------------
    # SKILLS
    # -----------------------------------------------------------------------
    @staticmethod
    def normalize_skills(skills_raw) -> List[str]:
        """
        Accept: comma/semicolon/pipe/newline separated string, or list.
        Returns deduplicated canonical skill names.
        """
        if not skills_raw:
            return []
        # Convert list to string for uniform processing
        if isinstance(skills_raw, list):
            raw_list = skills_raw
        else:
            raw_list = re.split(r'[;,|\n]', str(skills_raw))

        seen, result = set(), []
        for item in raw_list:
            skill = item.strip().strip('"').strip("'")
            if not skill:
                continue
            # Check alias map first
            canonical = SKILL_ALIASES.get(skill.lower(), skill)
            # Remove version numbers for deduplication key: "Python 3.9" -> "Python"
            key = re.sub(r'\s*[\d.]+$', '', canonical).strip().lower()
            if key not in seen:
                seen.add(key)
                result.append(canonical)
        return result

    @staticmethod
    def extract_skills_from_text(text: str) -> List[str]:
        """Match known skill keywords from free-form resume text."""
        found, seen = [], set()
        text_lower = text.lower()
        for skill in SKILL_KEYWORDS:
            # Word-boundary aware matching
            if re.search(r'\b' + re.escape(skill.lower()) + r'\b', text_lower):
                key = skill.lower()
                if key not in seen:
                    seen.add(key)
                    found.append(skill)
        return found

    # -----------------------------------------------------------------------
    # COUNTRY
    # -----------------------------------------------------------------------
    @staticmethod
    def normalize_country(country: str) -> str:
        """Convert country name / code to ISO-3166 alpha-2."""
        if not country:
            return ""
        try:
            result = pycountry.countries.lookup(country.strip())
            return result.alpha_2
        except LookupError:
            logger.debug(f"Could not normalize country: {country}")
        return country.strip()

    # -----------------------------------------------------------------------
    # DATE
    # -----------------------------------------------------------------------
    @staticmethod
    def normalize_date(date_str: str) -> str:
        """
        Normalize diverse date formats to YYYY-MM.
        Handles: 2024-06, 06/2024, June 2024, Jun-24, 2024, etc.
        """
        if not date_str or not isinstance(date_str, str):
            return ""
        date_str = date_str.strip()

        MONTHS = {
            'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
            'may': '05', 'jun': '06', 'jul': '07', 'aug': '08',
            'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12',
        }

        # Format: "June 2024" or "Jun 2024" or "Jun-2024"
        m = re.search(r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*[\s\-,]*(\d{4})',
                      date_str, re.IGNORECASE)
        if m:
            return f"{m.group(2)}-{MONTHS[m.group(1).lower()[:3]]}"

        # Format: "2024-06" or "2024/06"
        m = re.search(r'(\d{4})[-/](\d{1,2})', date_str)
        if m:
            return f"{m.group(1)}-{m.group(2).zfill(2)}"

        # Format: "06/2024" or "06-2024"
        m = re.search(r'(\d{1,2})[-/](\d{4})', date_str)
        if m:
            return f"{m.group(2)}-{m.group(1).zfill(2)}"

        # Just a year
        m = re.search(r'\b(\d{4})\b', date_str)
        if m:
            return m.group(1)

        return date_str

    # -----------------------------------------------------------------------
    # SALARY
    # -----------------------------------------------------------------------
    @staticmethod
    def normalize_salary(salary_raw) -> Optional[float]:
        """
        Normalize salary to a float annual figure in INR/USD.
        Handles: "7 LPA", "700000", "7,00,000", "$85,000", "85k", "8.5L"
        """
        if not salary_raw:
            return None
        s = str(salary_raw).strip().replace(',', '')

        # Handle "7 LPA" or "7L" or "8.5 LPA" (Lakhs Per Annum)
        m = re.search(r'(\d+\.?\d*)\s*l(pa)?', s, re.IGNORECASE)
        if m:
            return float(m.group(1)) * 100000

        # Handle "85k" or "85K"
        m = re.search(r'(\d+\.?\d*)\s*k', s, re.IGNORECASE)
        if m:
            return float(m.group(1)) * 1000

        # Handle plain number
        m = re.search(r'(\d+\.?\d*)', s)
        if m:
            return float(m.group(1))

        return None

    # -----------------------------------------------------------------------
    # EXPERIENCE YEARS
    # -----------------------------------------------------------------------
    @staticmethod
    def normalize_experience_years(raw) -> Optional[float]:
        """
        Normalize experience years.
        Handles: "2", "2.5", "2 years", "2+ years", "Two years", "Fresher"
        """
        if raw is None:
            return None
        s = str(raw).strip().lower()

        if s in ('fresher', 'fresh', '0', 'na', 'n/a', ''):
            return 0.0

        m = re.search(r'(\d+\.?\d*)', s)
        if m:
            return float(m.group(1))

        return None
