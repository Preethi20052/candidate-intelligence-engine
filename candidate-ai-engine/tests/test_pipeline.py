import pytest
import sys
import os

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from app.normalizers.base import Normalizer
from app.merge_engine.merger import MergeEngine
from app.projection.projector import ProjectionEngine


# ===========================================================================
# EMAIL NORMALIZATION
# ===========================================================================
class TestEmailNormalization:
    def test_standard_email(self):
        assert Normalizer.normalize_email("John.Doe@Example.COM") == "john.doe@example.com"

    def test_strips_whitespace(self):
        assert Normalizer.normalize_email("  naveen@gmail.com  ") == "naveen@gmail.com"

    def test_angle_brackets(self):
        assert Normalizer.normalize_email("<naveen@gmail.com>") == "naveen@gmail.com"

    def test_plus_addressing(self):
        assert Normalizer.normalize_email("user+work@gmail.com") == "user+work@gmail.com"

    def test_invalid_email_returns_empty(self):
        assert Normalizer.normalize_email("not-an-email") == ""
        assert Normalizer.normalize_email("@example.com") == ""
        assert Normalizer.normalize_email("user@") == ""

    def test_extract_multiple_emails(self):
        text = "Contact: john@example.com or jane+work@gmail.com for details"
        emails = Normalizer.extract_emails(text)
        assert "john@example.com" in emails
        assert "jane+work@gmail.com" in emails

    def test_deduplication(self):
        text = "Email: naveen@gmail.com. Also: naveen@gmail.com"
        emails = Normalizer.extract_emails(text)
        assert emails.count("naveen@gmail.com") == 1


# ===========================================================================
# PHONE NORMALIZATION
# ===========================================================================
class TestPhoneNormalization:
    def test_indian_10_digit(self):
        assert Normalizer.normalize_phone("9876543210") == "+919876543210"

    def test_indian_with_country_code(self):
        assert Normalizer.normalize_phone("+91-9876543210") == "+919876543210"

    def test_indian_with_spaces(self):
        assert Normalizer.normalize_phone("+91 98765 43210") == "+919876543210"

    def test_us_number(self):
        result = Normalizer.normalize_phone("+1-555-123-4567")
        assert result == "+15551234567"

    def test_number_with_extension_stripped(self):
        result = Normalizer.normalize_phone("+91 9876543210 x123")
        assert result == "+919876543210"

    def test_extract_phones_from_text(self):
        text = "Call me at +91 9876543210 or 080-12345678"
        phones = Normalizer.extract_phones(text)
        assert any("9876543210" in p for p in phones)

    def test_invalid_short_number_returns_empty(self):
        result = Normalizer.normalize_phone("123")
        assert result == ""


# ===========================================================================
# NAME NORMALIZATION
# ===========================================================================
class TestNameNormalization:
    def test_all_caps(self):
        assert Normalizer.normalize_name("NAVEEN KUMAR") == "Naveen Kumar"

    def test_all_lower(self):
        assert Normalizer.normalize_name("naveen kumar") == "Naveen Kumar"

    def test_strips_honorific_dr(self):
        assert Normalizer.normalize_name("Dr. Naveen Kumar") == "Naveen Kumar"

    def test_strips_honorific_mr(self):
        assert Normalizer.normalize_name("Mr. John Doe") == "John Doe"

    def test_combine_first_last(self):
        result = Normalizer.combine_name_parts("Naveen", "Kumar", "V")
        assert result == "Naveen V Kumar"

    def test_strips_whitespace(self):
        assert Normalizer.normalize_name("  Naveen  Kumar  ") == "Naveen Kumar"


# ===========================================================================
# SKILLS NORMALIZATION
# ===========================================================================
class TestSkillsNormalization:
    def test_comma_separated(self):
        result = Normalizer.normalize_skills("Python, Java, SQL")
        assert "Python" in result and "Java" in result

    def test_semicolon_separated(self):
        result = Normalizer.normalize_skills("Python; FastAPI; Docker")
        assert "FastAPI" in result

    def test_pipe_separated(self):
        result = Normalizer.normalize_skills("Python | React | Node.js")
        assert "React" in result

    def test_alias_ml(self):
        result = Normalizer.normalize_skills("ML, DL, NLP")
        assert "Machine Learning" in result
        assert "Deep Learning" in result

    def test_list_input(self):
        result = Normalizer.normalize_skills(["Python", "Java", "SQL"])
        assert "Python" in result

    def test_deduplication(self):
        result = Normalizer.normalize_skills("Python, python, PYTHON")
        assert len([r for r in result if r.lower() == "python"]) == 1


# ===========================================================================
# DATE NORMALIZATION
# ===========================================================================
class TestDateNormalization:
    def test_year_month(self):
        assert Normalizer.normalize_date("2024-06") == "2024-06"

    def test_month_year_slash(self):
        assert Normalizer.normalize_date("06/2024") == "2024-06"

    def test_month_name(self):
        assert Normalizer.normalize_date("June 2024") == "2024-06"

    def test_abbreviated_month(self):
        assert Normalizer.normalize_date("Jun 2024") == "2024-06"

    def test_year_only(self):
        assert Normalizer.normalize_date("2024") == "2024"


# ===========================================================================
# SALARY NORMALIZATION
# ===========================================================================
class TestSalaryNormalization:
    def test_lpa(self):
        assert Normalizer.normalize_salary("7 LPA") == 700000.0

    def test_lakhs_shorthand(self):
        assert Normalizer.normalize_salary("8.5L") == 850000.0

    def test_k_shorthand(self):
        assert Normalizer.normalize_salary("85k") == 85000.0

    def test_plain_number(self):
        assert Normalizer.normalize_salary("700000") == 700000.0

    def test_with_commas(self):
        assert Normalizer.normalize_salary("7,00,000") == 700000.0


# ===========================================================================
# MERGE ENGINE
# ===========================================================================
class TestMergeEngine:
    def test_priority_resolution(self):
        """Higher priority source wins on scalar conflict."""
        profiles = [
            {"source_type": "resume",       "full_name": "Naveen V", "emails": ["naveen@resume.com"]},
            {"source_type": "recruiter_csv","full_name": "Naveen",   "emails": ["naveen@csv.com"]},
        ]
        merger = MergeEngine(config_priority=["resume", "recruiter_csv"])
        merged = merger.merge(profiles)
        assert merged["full_name"] == "Naveen V"  # resume wins

    def test_email_union(self):
        """Emails from all sources are unioned."""
        profiles = [
            {"source_type": "resume",       "emails": ["a@gmail.com"]},
            {"source_type": "recruiter_csv","emails": ["b@gmail.com"]},
        ]
        merger = MergeEngine(config_priority=["resume", "recruiter_csv"])
        merged = merger.merge(profiles)
        assert "a@gmail.com" in merged["emails"]
        assert "b@gmail.com" in merged["emails"]

    def test_phone_deduplication(self):
        """Same phone in different formats is deduplicated."""
        profiles = [
            {"source_type": "resume",       "phones": ["+919876543210"]},
            {"source_type": "recruiter_csv","phones": ["+919876543210"]},
        ]
        merger = MergeEngine(config_priority=["resume", "recruiter_csv"])
        merged = merger.merge(profiles)
        assert merged["phones"].count("+919876543210") == 1

    def test_overall_confidence_computed(self):
        profiles = [{"source_type": "resume", "full_name": "Test User"}]
        merger = MergeEngine(config_priority=["resume"])
        merged = merger.merge(profiles)
        assert "overall_confidence" in merged
        assert 0.0 <= merged["overall_confidence"] <= 1.0


# ===========================================================================
# PROJECTION LAYER
# ===========================================================================
class TestProjectionLayer:
    def test_field_remap(self):
        canonical = {"full_name": "Naveen V", "emails": ["naveen@gmail.com"]}
        config = {
            "fields": [
                {"path": "candidate_name", "from": "full_name"},
                {"path": "primary_email",  "from": "emails[0]"},
            ],
            "on_missing": "omit"
        }
        projected = ProjectionEngine.project(canonical, config)
        assert projected["candidate_name"] == "Naveen V"
        assert projected["primary_email"] == "naveen@gmail.com"

    def test_missing_field_omit(self):
        canonical = {"full_name": "Naveen V"}
        config = {
            "fields": [{"path": "primary_email", "from": "emails[0]"}],
            "on_missing": "omit"
        }
        projected = ProjectionEngine.project(canonical, config)
        assert "primary_email" not in projected

    def test_missing_field_null(self):
        canonical = {"full_name": "Naveen V"}
        config = {
            "fields": [{"path": "primary_email", "from": "emails[0]"}],
            "on_missing": "null"
        }
        projected = ProjectionEngine.project(canonical, config)
        assert projected.get("primary_email") is None

    def test_missing_required_raises(self):
        canonical = {"full_name": "Naveen V"}
        config = {
            "fields": [{"path": "primary_email", "from": "emails[0]", "required": True}],
            "on_missing": "error"
        }
        with pytest.raises(ValueError):
            ProjectionEngine.project(canonical, config)
