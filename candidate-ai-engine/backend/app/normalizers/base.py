import re
import phonenumbers
import pycountry
from loguru import logger
from datetime import datetime

class Normalizer:
    @staticmethod
    def normalize_email(email: str) -> str:
        if not email:
            return ""
        return email.strip().lower()

    @staticmethod
    def normalize_phone(phone: str, region: str = "US") -> str:
        if not phone:
            return ""
        try:
            parsed = phonenumbers.parse(phone, region)
            if phonenumbers.is_valid_number(parsed):
                return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        except phonenumbers.NumberParseException:
            logger.warning(f"Failed to parse phone number: {phone}")
        return phone.strip()

    @staticmethod
    def normalize_country(country: str) -> str:
        if not country:
            return ""
        try:
            # Try exact match
            result = pycountry.countries.lookup(country)
            return result.alpha_2
        except LookupError:
            logger.warning(f"Failed to normalize country: {country}")
        return country.strip()

    @staticmethod
    def normalize_date(date_str: str) -> str:
        if not date_str:
            return ""
        # Simple heuristic for YYYY-MM
        match = re.search(r'(\d{4})[-/]?(\d{1,2})', date_str)
        if match:
            year = match.group(1)
            month = match.group(2).zfill(2)
            return f"{year}-{month}"
        
        match_year = re.search(r'(\d{4})', date_str)
        if match_year:
            return match_year.group(1)
        
        return date_str.strip()
