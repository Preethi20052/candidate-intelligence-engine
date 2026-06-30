import sys, json
sys.path.append("candidate-ai-engine/backend")

from app.extractors.resume_parser import ResumeParser
from app.extractors.csv_extractor import CSVExtractor
from app.merge_engine.merger import MergeEngine

print("=" * 60)
print("TEST 1: Resume (TXT) + CSV")
print("=" * 60)

# Step 1: Parse resume
parser = ResumeParser()
resume_profile = parser.parse_file(
    "candidate-ai-engine/sample_data/naveen_resume.txt", ".txt"
)
resume_profile['source_type'] = 'resume'
resume_profile['filename'] = 'naveen_resume.txt'

print("\n[RESUME EXTRACTED]")
print(f"  full_name : {resume_profile.get('full_name')}")
print(f"  emails    : {resume_profile.get('emails')}")
print(f"  phones    : {resume_profile.get('phones')}")
print(f"  skills    : {resume_profile.get('skills')}")

# Step 2: Extract CSV and match to resume candidate
csv_records = CSVExtractor.extract("candidate-ai-engine/sample_data/recruiter_notes.csv")
resume_name = resume_profile.get('full_name', '').lower().strip()

matched_csv = []
for r in csv_records:
    row_name = (r.get('full_name') or '').lower().strip()
    if resume_name and (any(p in row_name for p in resume_name.split()) or
                        any(p in resume_name for p in row_name.split())):
        r['source_type'] = 'recruiter_csv'
        matched_csv.append(r)

print(f"\n[CSV MATCHED ROWS for '{resume_name}']")
for r in matched_csv:
    print(f"  full_name : {r.get('full_name')}")
    print(f"  emails    : {r.get('emails')}")
    print(f"  phones    : {r.get('phones')}")
    print(f"  skills    : {r.get('skills')}")

# Step 3: Merge
profiles = [resume_profile] + matched_csv
priority = ["resume", "linkedin", "ats_json", "recruiter_csv", "github"]
merger = MergeEngine(config_priority=priority)
merged = merger.merge(profiles)

print("\n[FINAL MERGED CANONICAL PROFILE]")
# Print everything except provenance for clarity
for k, v in merged.items():
    if k != 'field_provenance':
        print(f"  {k:<25}: {v}")

print("\n[PROVENANCE]")
for field, prov in merged.get('field_provenance', {}).items():
    print(f"  {field:<25}: source={prov['source']}, confidence={prov['confidence']}")

print("\n✅ Pipeline test complete!")
