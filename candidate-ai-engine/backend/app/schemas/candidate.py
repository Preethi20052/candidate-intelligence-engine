from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr
from datetime import date

class Provenance(BaseModel):
    source: str = Field(..., description="Source of the data (e.g., 'resume.pdf', 'recruiter.csv')")
    extraction_method: str = Field(..., description="Method used (e.g., 'regex', 'llm', 'spacy')")
    transformation: str = Field(default="", description="Transformations applied")
    normalization: str = Field(default="", description="Normalizations applied")
    timestamp: str = Field(..., description="ISO timestamp of extraction")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score for this field")

class FieldWithProvenance(BaseModel):
    value: Any
    provenance: Provenance

class Skill(BaseModel):
    name: str
    category: Optional[str] = None
    confidence: float = 1.0

class Experience(BaseModel):
    title: str
    company: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None
    is_current: bool = False

class Education(BaseModel):
    degree: str
    institution: str
    graduation_year: Optional[int] = None

class CandidateProfile(BaseModel):
    candidate_id: str
    full_name: Optional[str] = None
    emails: List[str] = Field(default_factory=list)
    phones: List[str] = Field(default_factory=list)
    location: Optional[str] = None
    links: List[str] = Field(default_factory=list)
    headline: Optional[str] = None
    years_experience: float = 0.0
    skills: List[Skill] = Field(default_factory=list)
    experience: List[Experience] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    
    # Global metadata
    overall_confidence: float = 0.0
    field_provenance: Dict[str, Provenance] = Field(default_factory=dict)
