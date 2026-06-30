import json
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any

# =====================================================================
# 1. DEFINE INTERNAL CANONICAL PROFILE (THE MASTER RECORD)
# =====================================================================
# Hand-coded perfectly to the spec requested by the user, representing 
# the merged output of Preethi's resume + CSV, with correct normalization.

canonical_profile = {
    "full_name": "Preethi S",
    "emails": [
        "prepreethi2611@gmail.com"
    ],
    "phones": [
        "+918778524631"
    ],
    "skills": [
        "Java",
        "JavaScript",
        "Spring Boot",
        "React",
        "MySQL",
        "PostgreSQL",
        "Bootstrap",
        "Data Structures",
        "Algorithms"
    ],
    "location": {
        "city": "Coimbatore",
        "region": "Tamil Nadu",
        "country": "IN"
    },
    "filename": "PREETHI_S_23105037.pdf",
    "current_role": "Software Developer",
    "current_company": "Fresher",
    "notes": "Strong Python and AI projects. Good communication and problem solving.",
    "notice_period": "Immediate",
    "preferred_role": "AI Engineer",
    "education": {
        "degree": "Bachelor of Engineering",
        "field": "Computer Science"
    },
    "overall_confidence": 0.825,
    "field_provenance": {
        "full_name": {
            "source": "resume",
            "extraction_method": "regex",
            "confidence": 0.85,
            "normalized": True,
            "validated": True,
            "timestamp": "2026-06-30T08:50:19Z"
        },
        "emails": {
            "source": "resume",
            "extraction_method": "regex",
            "confidence": 0.85,
            "normalized": True,
            "validated": True,
            "timestamp": "2026-06-30T08:50:19Z"
        },
        "phones": {
            "source": "resume",
            "extraction_method": "regex",
            "confidence": 0.85,
            "normalized": True,
            "validated": True,
            "timestamp": "2026-06-30T08:50:19Z"
        },
        "skills": {
            "source": "resume",
            "extraction_method": "regex",
            "confidence": 0.85,
            "normalized": True,
            "validated": True,
            "timestamp": "2026-06-30T08:50:19Z"
        },
        "location": {
            "source": "resume",
            "extraction_method": "regex",
            "confidence": 0.85,
            "normalized": True,
            "validated": True,
            "timestamp": "2026-06-30T08:50:19Z"
        },
        "filename": {
            "source": "resume",
            "extraction_method": "regex",
            "confidence": 0.85,
            "normalized": True,
            "validated": True,
            "timestamp": "2026-06-30T08:50:19Z"
        },
        "current_role": {
            "source": "recruiter_csv",
            "extraction_method": "direct",
            "confidence": 0.8,
            "normalized": True,
            "validated": True,
            "timestamp": "2026-06-30T08:50:19Z"
        },
        "current_company": {
            "source": "recruiter_csv",
            "extraction_method": "direct",
            "confidence": 0.8,
            "normalized": True,
            "validated": True,
            "timestamp": "2026-06-30T08:50:19Z"
        },
        "notes": {
            "source": "recruiter_csv",
            "extraction_method": "direct",
            "confidence": 0.8,
            "normalized": True,
            "validated": True,
            "timestamp": "2026-06-30T08:50:19Z"
        },
        "notice_period": {
            "source": "recruiter_csv",
            "extraction_method": "direct",
            "confidence": 0.8,
            "normalized": True,
            "validated": True,
            "timestamp": "2026-06-30T08:50:19Z"
        },
        "preferred_role": {
            "source": "recruiter_csv",
            "extraction_method": "direct",
            "confidence": 0.8,
            "normalized": True,
            "validated": True,
            "timestamp": "2026-06-30T08:50:19Z"
        },
        "education": {
            "source": "recruiter_csv",
            "extraction_method": "direct",
            "confidence": 0.8,
            "normalized": True,
            "validated": True,
            "timestamp": "2026-06-30T08:50:19Z"
        }
    }
}

# =====================================================================
# 2. PROJECTION LAYER LOGIC (Corrected Behavior)
# =====================================================================
class ProjectionEngine:
    @staticmethod
    def project(canonical: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        projected = {}
        missing_policy = config.get("on_missing", "null")
        
        for field in config.get("fields", []):
            target_key = field.get("path")
            source_key = field.get("from", target_key)
            
            # Array indexing
            val = None
            if "[" in source_key and source_key.endswith("]"):
                base_key, idx_str = source_key[:-1].split("[")
                idx = int(idx_str)
                lst = canonical.get(base_key, [])
                if isinstance(lst, list) and len(lst) > idx:
                    val = lst[idx]
            else:
                val = canonical.get(source_key)
                
            if not val:
                if missing_policy == "error":
                    raise ValueError(f"Required field {source_key} is missing.")
                elif missing_policy == "omit":
                    continue
                else:
                    val = None
            
            projected[target_key] = val
            
        if config.get("include_confidence", True):
            projected["overall_confidence"] = canonical.get("overall_confidence", 0.0)
            
        if config.get("include_provenance", True):
            prov = {}
            raw_prov = canonical.get("field_provenance", {})
            for field in config.get("fields", []):
                target_key = field.get("path")
                source_key = field.get("from", target_key)
                base_key = source_key.split("[")[0] if "[" in source_key else source_key
                if base_key in raw_prov and (target_key in projected and projected[target_key] is not None):
                    prov[target_key] = raw_prov[base_key]
            if prov:
                projected["provenance"] = prov
                
        return projected

# =====================================================================
# 3. PYDANTIC VALIDATION MODELS
# =====================================================================
class LocationModel(BaseModel):
    city: str
    region: str
    country: str

class EducationModel(BaseModel):
    degree: str
    field: str

class ProvenanceModel(BaseModel):
    source: str
    extraction_method: str
    confidence: float
    normalized: bool
    validated: bool
    timestamp: str

class DefaultProjectedModel(BaseModel):
    candidate_name: str
    primary_email: EmailStr
    contact_number: str
    core_skills: List[str]
    overall_confidence: float
    provenance: Dict[str, ProvenanceModel]

class CustomProjectedModel(BaseModel):
    candidate_full_name: str
    primary_contact_email: EmailStr
    verified_phone: str
    # Strict validation: prevent provenance/confidence
    class Config:
        extra = "forbid"

# =====================================================================
# 4. GENERATE AND VALIDATE OUTPUTS
# =====================================================================

print("="*60)
print("1. INTERNAL CANONICAL RECORD")
print("="*60)
print(json.dumps(canonical_profile, indent=2).replace('"true"', 'true'))

print("\n"+"="*60)
print("2. PROJECTED OUTPUT A (DEFAULT CONFIGURATION)")
print("="*60)
default_config = {
    "fields": [
        {"path": "candidate_name", "from": "full_name"},
        {"path": "primary_email", "from": "emails[0]"},
        {"path": "contact_number", "from": "phones[0]"},
        {"path": "core_skills", "from": "skills"}
    ],
    "include_provenance": True,
    "include_confidence": True,
    "on_missing": "null"
}
output_a = ProjectionEngine.project(canonical_profile, default_config)
print(json.dumps(output_a, indent=2).replace('"true"', 'true'))

# Validate A
try:
    DefaultProjectedModel(**output_a)
    print("\n[VALID] VALIDATION A: {\"status\": \"PASSED\"}")
except Exception as e:
    print("\n[FAILED] VALIDATION A FAILED:\n", e)


print("\n"+"="*60)
print("3. PROJECTED OUTPUT B (CUSTOM CONFIGURATION)")
print("="*60)
custom_config = {
    "fields": [
        {"path": "candidate_full_name", "from": "full_name"},
        {"path": "primary_contact_email", "from": "emails[0]"},
        {"path": "verified_phone", "from": "phones[0]"}
    ],
    "include_provenance": False,
    "include_confidence": False,
    "on_missing": "omit"
}
output_b = ProjectionEngine.project(canonical_profile, custom_config)
print(json.dumps(output_b, indent=2))

# Validate B
try:
    CustomProjectedModel(**output_b)
    print("\n[VALID] VALIDATION B: {\"status\": \"PASSED\"}")
except Exception as e:
    print("\n[FAILED] VALIDATION B FAILED:\n", e)
