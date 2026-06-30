import sys
sys.path.append("candidate-ai-engine/backend")

from app.extractors.resume_parser import ResumeParser
from app.extractors.csv_extractor import CSVExtractor
from app.merge_engine.merger import MergeEngine
import tempfile, pathlib, os

# --- Simulate: Resume = Naveen, CSV = Preethi (completely different person) ---

resume_text = """Naveen V
Email: naveen.v@gmail.com
Phone: +91 9876543210
Skills: Python, FastAPI, Machine Learning
Location: Bangalore
"""

csv_text = """full_name,email,phone,skills,current_role
Preethi S,preethi.s@gmail.com,9123456789,Java;Spring Boot,Backend Developer
"""

print("=" * 60)
print("SCENARIO: Resume = Naveen | CSV = Preethi (different people)")
print("=" * 60)

# Parse resume
with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode='w', encoding='utf-8') as f:
    f.write(resume_text)
    resume_path = f.name

parser = ResumeParser()
resume_profile = parser.parse_file(resume_path, ".txt")
resume_profile['source_type'] = 'resume'
os.unlink(resume_path)

print(f"\n[RESUME CANDIDATE] => {resume_profile.get('full_name')}")

# Parse CSV
with tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode='w', encoding='utf-8') as f:
    f.write(csv_text)
    csv_path = f.name

csv_records = CSVExtractor.extract(csv_path)
os.unlink(csv_path)

print(f"[CSV CANDIDATES]   => {[r.get('full_name') for r in csv_records]}")

# --- Try to match CSV row to resume candidate ---
resume_name = resume_profile.get('full_name', '').lower().strip()
matched_csv = []
unmatched_csv = []

for r in csv_records:
    row_name = (r.get('full_name') or '').lower().strip()
    name_parts_resume = set(resume_name.split())
    name_parts_row    = set(row_name.split())
    # Match if any significant word overlaps (ignoring single initials)
    overlap = [p for p in name_parts_resume & name_parts_row if len(p) > 1]
    if overlap:
        r['source_type'] = 'recruiter_csv'
        matched_csv.append(r)
    else:
        unmatched_csv.append(r)

print(f"\n[MATCHING RESULT]")
print(f"  Resume name     : '{resume_name}'")
print(f"  CSV row name    : '{csv_records[0].get('full_name', '').lower()}'")
print(f"  Name overlap    : {set(resume_name.split()) & set(csv_records[0].get('full_name','').lower().split())}")
print(f"  Matched rows    : {len(matched_csv)}")
print(f"  Unmatched rows  : {len(unmatched_csv)} (IGNORED - different person)")

profiles = [resume_profile] + matched_csv
merger = MergeEngine(config_priority=["resume", "recruiter_csv"])
merged = merger.merge(profiles)

print(f"\n[FINAL MERGED OUTPUT]")
for k, v in merged.items():
    if k != 'field_provenance':
        print(f"  {k:<25}: {v}")

print("\n--- CONCLUSION ---")
if not matched_csv:
    print("NO CSV ROW MATCHED the resume candidate.")
    print("System used ONLY the resume data.")
    print("Preethi's data was completely IGNORED.")
else:
    print("WARNING: A CSV row was incorrectly matched!")
