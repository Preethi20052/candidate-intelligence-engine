import csv
import io
from typing import List, Dict, Any
from app.normalizers.base import Normalizer
from loguru import logger

# ---------------------------------------------------------------------------
# Column alias maps — covers every real-world variation of field names
# ---------------------------------------------------------------------------
FIELD_ALIASES = {
    "full_name": [
        "full_name", "name", "candidate_name", "fullname", "applicant_name",
        "candidate", "contact_name", "person_name", "employee_name"
    ],
    "first_name": ["first_name", "firstname", "fname", "given_name"],
    "last_name":  ["last_name", "lastname", "lname", "surname", "family_name"],
    "middle_name":["middle_name", "middlename", "mname"],
    "emails": [
        "email", "emails", "email_address", "e_mail", "e-mail",
        "contact_email", "work_email", "personal_email", "mail"
    ],
    "phones": [
        "phone", "phones", "phone_number", "mobile", "mobile_number",
        "contact", "contact_number", "cell", "cell_number",
        "telephone", "tel", "phone_no", "ph_no", "ph"
    ],
    "skills": [
        "skills", "skill_set", "skillset", "key_skills", "technical_skills",
        "competencies", "expertise", "technologies", "tech_stack"
    ],
    "experience_years": [
        "experience_years", "years_of_experience", "exp_years", "total_exp",
        "experience", "work_experience", "years_exp", "yoe", "exp"
    ],
    "current_role": [
        "current_role", "designation", "job_title", "title", "position",
        "current_title", "role", "current_position", "current_designation"
    ],
    "current_company": [
        "current_company", "company", "employer", "organization",
        "organisation", "current_employer", "firm", "company_name"
    ],
    "location": [
        "location", "city", "address", "current_location", "place",
        "residence", "city_state", "region", "base_location"
    ],
    "expected_salary": [
        "expected_salary", "salary", "ctc", "expected_ctc", "salary_expectation",
        "package", "expected_package", "compensation", "pay"
    ],
    "recruiter_rating": [
        "recruiter_rating", "rating", "score", "candidate_score",
        "assessment_score", "evaluation", "rank"
    ],
    "notes": [
        "notes", "comments", "remarks", "feedback", "recruiter_notes",
        "additional_info", "description", "summary", "observations"
    ],
    "notice_period": [
        "notice_period", "notice", "availability", "joining_availability",
        "available_from", "notice_days"
    ],
    "preferred_role": [
        "preferred_role", "desired_role", "target_role", "job_preference",
        "preferred_position", "looking_for"
    ],
    "education": [
        "education", "qualification", "degree", "highest_qualification",
        "academic_background"
    ],
    "source": [
        "source", "lead_source", "referral", "how_did_you_hear",
        "candidate_source"
    ],
    "candidate_id": [
        "candidate_id", "id", "applicant_id", "emp_id", "candidate_code",
        "ref_id", "ats_id"
    ],
    "linkedin_url": [
        "linkedin_url", "linkedin", "linkedin_profile", "li_url"
    ],
    "github_url": [
        "github_url", "github", "github_profile", "gh_url"
    ],
}

# Reverse lookup: alias -> canonical key
ALIAS_TO_CANONICAL = {}
for canonical, aliases in FIELD_ALIASES.items():
    for alias in aliases:
        ALIAS_TO_CANONICAL[alias.lower()] = canonical


class CSVExtractor:
    """
    Extracts and normalizes candidate records from CSV files.
    Handles:
    - Diverse column name aliases
    - first_name + last_name -> full_name combination
    - Phone normalization to E.164
    - Email normalization
    - Skills parsing (comma/semicolon/pipe separated)
    - Salary normalization
    - Experience years normalization
    - BOM in UTF-8 files
    - Tab, comma, semicolon delimiters
    """

    @staticmethod
    def extract(file_path: str) -> List[Dict[str, Any]]:
        records = []
        try:
            # Read raw bytes to detect delimiter and encoding
            with open(file_path, mode='rb') as raw:
                content = raw.read()

            # Decode — strip BOM if present
            try:
                text = content.decode('utf-8-sig')
            except UnicodeDecodeError:
                text = content.decode('latin-1', errors='ignore')

            # Detect delimiter
            delimiter = CSVExtractor._detect_delimiter(text)

            reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)

            for row_num, row in enumerate(reader, start=2):
                try:
                    cleaned = CSVExtractor._normalize_row(row)
                    if cleaned:
                        records.append(cleaned)
                except Exception as e:
                    logger.warning(f"Skipping CSV row {row_num} due to error: {e}")
                    continue

        except Exception as e:
            logger.error(f"Failed to read CSV file {file_path}: {e}")

        logger.info(f"CSV extracted {len(records)} records from {file_path}")
        return records

    @staticmethod
    def _detect_delimiter(text: str) -> str:
        """Detect CSV delimiter from first line."""
        first_line = text.split('\n')[0] if '\n' in text else text
        counts = {
            ',': first_line.count(','),
            ';': first_line.count(';'),
            '\t': first_line.count('\t'),
            '|': first_line.count('|'),
        }
        return max(counts, key=counts.get)

    @staticmethod
    def _normalize_row(row: Dict[str, str]) -> Dict[str, Any]:
        """Map raw CSV columns to canonical keys and normalize values."""
        # First, remap all column headers to canonical names
        remapped = {}
        for raw_key, value in row.items():
            if raw_key is None:
                continue
            key_lower = raw_key.strip().lower().replace(' ', '_').replace('-', '_')
            canonical = ALIAS_TO_CANONICAL.get(key_lower, key_lower)
            val = value.strip() if isinstance(value, str) else value
            if val:
                # If multiple aliases map to the same canonical (e.g., two email cols),
                # keep whichever has a non-empty value
                if canonical not in remapped or not remapped[canonical]:
                    remapped[canonical] = val

        result = {}

        # ---- NAME: combine first + last if full_name missing ----
        if 'full_name' in remapped and remapped['full_name']:
            result['full_name'] = Normalizer.normalize_name(remapped['full_name'])
        elif 'first_name' in remapped or 'last_name' in remapped:
            result['full_name'] = Normalizer.combine_name_parts(
                remapped.get('first_name', ''),
                remapped.get('last_name', ''),
                remapped.get('middle_name', ''),
            )

        # ---- EMAILS ----
        raw_email = remapped.get('emails', '')
        # Could be multiple emails separated by comma or semicolon
        email_parts = re.split(r'[;,\s]', raw_email) if raw_email else []
        normalized_emails = []
        for ep in email_parts:
            norm = Normalizer.normalize_email(ep)
            if norm and norm not in normalized_emails:
                normalized_emails.append(norm)
        if normalized_emails:
            result['emails'] = normalized_emails

        # ---- PHONES ----
        raw_phone = remapped.get('phones', '')
        phone_parts = re.split(r'[;,/]', raw_phone) if raw_phone else []
        normalized_phones = []
        for pp in phone_parts:
            norm = Normalizer.normalize_phone(pp.strip())
            if norm and norm not in normalized_phones:
                normalized_phones.append(norm)
        if normalized_phones:
            result['phones'] = normalized_phones

        # ---- SKILLS ----
        if 'skills' in remapped:
            result['skills'] = Normalizer.normalize_skills(remapped['skills'])

        # ---- EXPERIENCE YEARS ----
        if 'experience_years' in remapped:
            result['experience_years'] = Normalizer.normalize_experience_years(
                remapped['experience_years']
            )

        # ---- EXPECTED SALARY ----
        if 'expected_salary' in remapped:
            result['expected_salary'] = Normalizer.normalize_salary(remapped['expected_salary'])

        # ---- RECRUITER RATING ----
        if 'recruiter_rating' in remapped:
            try:
                result['recruiter_rating'] = float(remapped['recruiter_rating'])
            except (ValueError, TypeError):
                pass

        # ---- SIMPLE STRING FIELDS ----
        simple_fields = [
            'current_role', 'current_company', 'location', 'notes',
            'notice_period', 'preferred_role', 'education',
            'candidate_id', 'source', 'linkedin_url', 'github_url'
        ]
        for field in simple_fields:
            if field in remapped and remapped[field]:
                result[field] = remapped[field].strip()

        return result