import sys
sys.path.append('candidate-ai-engine/backend')
from app.extractors.resume_parser import ResumeParser
from app.extractors.csv_extractor import CSVExtractor
from app.merge_engine.merger import MergeEngine
from app.projection.projector import ProjectionEngine
import tempfile, os

resume_text = """PREETHI S
prepreethi2611@gmail.com 8778524631 Coimbatore,Tamil Nadu linkedin.com/in/preethi-s-945054364
github.com/Preethi20052
CAREER OBJECTIVE
Enthusiastic Java learner with hands-on knowledge of core Java, OOP concepts, and backend development, looking for an
entry-levelsoftware role to build scalable applications and grow as a Java developer.
"""

csv_text = """full_name,email,phone,skills,experience_years,current_role
Preethi S,preethi.s@gmail.com,9123456789,Java;Spring Boot,2,Backend Developer
"""

p = ResumeParser()
resume_profile = p._parse_text(resume_text, filename_hint='Preethi_S.pdf')
resume_profile['source_type'] = 'resume'

with tempfile.NamedTemporaryFile(delete=False, suffix='.csv', mode='w', encoding='utf-8') as f:
    f.write(csv_text)
    csv_path = f.name
csv_records = CSVExtractor.extract(csv_path)
os.unlink(csv_path)
csv_profile = csv_records[0]
csv_profile['source_type'] = 'recruiter_csv'

print("--- RAW PROFILES BEFORE MERGE ---")
print("RESUME EMAILS:", resume_profile.get('emails'))
print("RESUME PHONES:", resume_profile.get('phones'))
print("CSV EMAILS:", csv_profile.get('emails'))
print("CSV PHONES:", csv_profile.get('phones'))

profiles = [resume_profile, csv_profile]
merger = MergeEngine(config_priority=["resume", "recruiter_csv"])
merged = merger.merge(profiles)

print("\n--- AFTER MERGE (Internal Profile) ---")
print("MERGED EMAILS:", merged.get('emails'))
print("MERGED PHONES:", merged.get('phones'))

proj_config = {
    "fields": [
        {"path": "candidate_full_name", "from": "full_name"},
        {"path": "primary_contact_email", "from": "emails[0]"},
        {"path": "verified_phone", "from": "phones[0]"}
    ],
    "on_missing": "omit"
}
projected = ProjectionEngine.project(merged, proj_config)

print("\n--- AFTER PROJECTION (What you see on screen) ---")
for k, v in projected.items():
    print(f"{k}: {v}")
