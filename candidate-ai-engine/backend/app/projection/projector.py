from typing import Dict, Any
from app.normalizers.base import Normalizer

class ProjectionEngine:
    @staticmethod
    def project(canonical: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dynamically reshapes the canonical profile based on a runtime JSON configuration.
        Config structure example:
        {
            "fields": [
                {"path": "full_name", "type": "string", "required": True},
                {"path": "primary_email", "from": "emails[0]"},
                {"path": "phone", "from": "phones[0]", "normalize": "E164"}
            ],
            "include_confidence": True,
            "on_missing": "null" # null, omit, error
        }
        """
        projected = {}
        missing_policy = config.get("on_missing", "null")
        
        for field in config.get("fields", []):
            target_key = field.get("path")
            source_key = field.get("from", target_key)
            
            # Simple list index parsing like "emails[0]"
            val = None
            if "[" in source_key and source_key.endswith("]"):
                base_key, idx_str = source_key[:-1].split("[")
                idx = int(idx_str)
                lst = canonical.get(base_key, [])
                if isinstance(lst, list) and len(lst) > idx:
                    val = lst[idx]
            else:
                val = canonical.get(source_key)
                
            # Handle Missing
            if not val:
                if field.get("required") and missing_policy == "error":
                    raise ValueError(f"Required field {source_key} is missing.")
                elif missing_policy == "omit":
                    continue
                else:
                    val = None
                    
            # Apply dynamic normalization
            norm_rule = field.get("normalize")
            if norm_rule == "E164" and val:
                val = Normalizer.normalize_phone(val)
                
            projected[target_key] = val
            
        if config.get("include_confidence"):
            projected["overall_confidence"] = canonical.get("overall_confidence", 0.0)
            
        if config.get("include_provenance", True):
            prov = {}
            raw_prov = canonical.get("field_provenance", {})
            for field in config.get("fields", []):
                target_key = field.get("path")
                source_key = field.get("from", target_key)
                base_key = source_key.split("[")[0] if "[" in source_key else source_key
                if base_key in raw_prov and target_key in projected and projected[target_key] is not None:
                    prov[target_key] = raw_prov[base_key]
            if prov:
                projected["provenance"] = prov
            
        return projected
