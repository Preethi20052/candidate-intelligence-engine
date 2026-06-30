from typing import List, Dict, Any, Literal
from pydantic import BaseModel, Field

class FieldConfig(BaseModel):
    rename_to: str = ""
    include: bool = True
    missing_value_policy: Literal["null", "omit", "error"] = "null"

class PipelineConfig(BaseModel):
    source_priority: List[str] = Field(
        default=["resume", "linkedin", "recruiter_csv", "github", "recruiter_notes"],
        description="Priority order for merging conflicting fields"
    )
    fields: Dict[str, FieldConfig] = Field(default_factory=dict)
    toggle_provenance: bool = True
    toggle_confidence: bool = True
