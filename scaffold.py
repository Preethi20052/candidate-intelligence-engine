import os

base_dir = "candidate-ai-engine/backend/app"

files = {
    f"{base_dir}/canonicalizers/skills.py": """
import re

class SkillCanonicalizer:
    skill_map = {
        "python3": "Python",
        "js": "JavaScript",
        "ml": "Machine Learning",
        "react.js": "React",
        "node.js": "Node.js",
        "aws": "Amazon Web Services"
    }

    @staticmethod
    def canonicalize(skill: str) -> str:
        clean_skill = skill.strip().lower()
        return SkillCanonicalizer.skill_map.get(clean_skill, skill.strip())
""",
    f"{base_dir}/canonicalizers/titles.py": """
class TitleCanonicalizer:
    title_map = {
        "software developer": "Software Engineer",
        "backend engineer": "Software Engineer",
        "frontend engineer": "Software Engineer",
        "sr software engineer": "Senior Software Engineer"
    }

    @staticmethod
    def canonicalize(title: str) -> str:
        clean_title = title.strip().lower()
        return TitleCanonicalizer.title_map.get(clean_title, title.strip())
""",
    f"{base_dir}/extractors/csv_extractor.py": """
import pandas as pd
from typing import List, Dict, Any

class CSVExtractor:
    @staticmethod
    def extract(file_path: str) -> List[Dict[str, Any]]:
        df = pd.read_csv(file_path)
        return df.to_dict('records')
""",
    f"{base_dir}/merge_engine/merger.py": """
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
""",
    f"{base_dir}/api/main.py": """
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Eightfold AI Candidate Intelligence Engine")

@app.get("/health")
def health_check():
    return {"status": "ok"}
"""
}

for filepath, content in files.items():
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f:
        f.write(content.strip())

print("Scaffolded python files successfully.")
