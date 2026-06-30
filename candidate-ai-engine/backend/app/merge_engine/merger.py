from typing import List, Dict, Any
from app.schemas.candidate import CandidateProfile, Provenance

class MergeEngine:
    def __init__(self, config_priority: List[str]):
        self.priority = config_priority

    def merge(self, profiles: List[Dict[str, Any]]) -> Dict[str, Any]:
        # Sort profiles based on priority
        sorted_profiles = sorted(
            profiles, 
            key=lambda p: self.priority.index(p.get('source_type')) if p.get('source_type') in self.priority else 999
        )
        
        merged = {}
        provenance = {}
        
        for profile in sorted_profiles:
            source = profile.get('source_type', 'unknown')
            for key, value in profile.items():
                if key == 'source_type':
                    continue
                if key not in merged or not merged[key]:
                    if value:
                        merged[key] = value
                        provenance[key] = {
                            "source": source,
                            "extraction_method": "direct",
                            "confidence": 0.9,
                            "timestamp": "2026-06-29"
                        }
        
        merged['field_provenance'] = provenance
        return merged