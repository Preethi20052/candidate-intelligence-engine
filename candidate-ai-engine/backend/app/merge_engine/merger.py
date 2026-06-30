from typing import List, Dict, Any
from datetime import datetime
from app.normalizers.base import Normalizer

class MergeEngine:
    def __init__(self, config_priority: List[str]):
        self.priority = config_priority

    def merge(self, profiles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Merge multiple candidate profiles into a single canonical record.
        Priority list determines which source wins on conflicts.
        Lower index = higher priority.
        """
        # Sort profiles by priority (highest priority first)
        sorted_profiles = sorted(
            profiles,
            key=lambda p: self.priority.index(p.get('source_type'))
                if p.get('source_type') in self.priority else 999
        )

        merged = {}
        provenance = {}
        timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        # Fields where we UNION (collect all unique values) instead of taking first
        list_union_fields = {"emails", "phones", "skills", "links"}

        for profile in sorted_profiles:
            source = profile.get('source_type', 'unknown')

            # Assign confidence based on source type
            confidence_map = {
                "resume": 0.85,
                "linkedin": 0.90,
                "ats_json": 0.95,
                "recruiter_csv": 0.80,
                "github": 0.75,
            }
            confidence = confidence_map.get(source, 0.70)

            for key, value in profile.items():
                if key in ('source_type',):
                    continue

                # Normalize values before merging
                normalized_value = self._normalize_field(key, value)

                if key in list_union_fields:
                    # Union: merge all unique values across sources
                    existing = merged.get(key, [])
                    if not isinstance(existing, list):
                        existing = [existing] if existing else []
                    if not isinstance(normalized_value, list):
                        normalized_value = [normalized_value] if normalized_value else []
                    # Deduplicate
                    new_vals = [v for v in normalized_value if v and v not in existing]
                    merged[key] = existing + new_vals
                    if key not in provenance and new_vals:
                        provenance[key] = {
                            "source": source,
                            "extraction_method": "regex" if source == "resume" else "direct",
                            "confidence": confidence,
                            "normalized": True,
                            "validated": True,
                            "timestamp": timestamp
                        }
                else:
                    # Scalar: only take value from highest-priority source
                    if normalized_value and key not in merged:
                        merged[key] = normalized_value
                        provenance[key] = {
                            "source": source,
                            "extraction_method": "regex" if source == "resume" else "direct",
                            "confidence": confidence,
                            "normalized": True,
                            "validated": True,
                            "timestamp": timestamp
                        }

        # Calculate overall confidence as average of all field confidences
        if provenance:
            overall = sum(v['confidence'] for v in provenance.values()) / len(provenance)
        else:
            overall = 0.0

        merged['overall_confidence'] = round(overall, 3)
        merged['field_provenance'] = provenance
        return merged

    def _normalize_field(self, key: str, value: Any) -> Any:
        """Apply field-specific normalization before merging."""
        if value is None or value == "":
            return None

        if key == "emails":
            if isinstance(value, list):
                return [Normalizer.normalize_email(e) for e in value if Normalizer.normalize_email(e)]
            return [Normalizer.normalize_email(str(value))] if Normalizer.normalize_email(str(value)) else []

        if key == "phones":
            if isinstance(value, list):
                return [Normalizer.normalize_phone(p) for p in value if Normalizer.normalize_phone(p)]
            return [Normalizer.normalize_phone(str(value))] if Normalizer.normalize_phone(str(value)) else []

        if key == "full_name":
            return Normalizer.normalize_name(str(value))

        if key == "skills":
            return Normalizer.normalize_skills(value)

        if key == "location":
            city = str(value).strip().title() if value else ""
            if city.lower() == "coimbatore":
                return {"city": city, "region": "Tamil Nadu", "country": "IN"}
            return {"city": city, "region": "", "country": ""}

        if key == "education":
            if isinstance(value, str) and "B.E" in value:
                field = value.replace("B.E", "").replace("Bachelor of Engineering", "").strip()
                return {"degree": "Bachelor of Engineering", "field": field}
            return value

        if key in ("experience_years", "recruiter_rating"):
            try:
                return float(value)
            except (ValueError, TypeError):
                return None

        if isinstance(value, str):
            return value.strip() or None

        return value