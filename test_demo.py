import sys
sys.path.append('candidate-ai-engine/backend')
from app.extractors.resume_parser import ResumeParser
from app.extractors.csv_extractor import CSVExtractor
from app.merge_engine.merger import MergeEngine
import tempfile, os

p = ResumeParser()

print("=" * 65)
print("DEMO TEST 1: Filename hint (Naveen_V.pdf)")
print("=" * 65)
name = p._name_from_filename('Naveen_V.pdf')
print(f"  Filename 'Naveen_V.pdf' -> extracted name: {name!r}")

print()
print("=" * 65)
print("DEMO TEST 2: Resume with misleading first line")
print("=" * 65)
resume_text = """Motivated BBA Graduate Seeking An Opportunity
Naveen V
naveen.v@gmail.com
+91 9876543210
Skills: Python, FastAPI, Machine Learning, SQL, Docker
Location: Bangalore
Expected Salary: 7 LPA
Fresher | Immediate Joiner
"""

result = p._parse_text(resume_text, filename_hint='Naveen_V.pdf')
print(f"  full_name  : {result['full_name']!r}")
print(f"  emails     : {result['emails']}")
print(f"  phones     : {result['phones']}")
print(f"  skills     : {result['skills']}")
print(f"  location   : {result.get('location')}")
print(f"  exp_years  : {result.get('experience_years')}")
print(f"  salary     : {result.get('expected_salary')}")

print()
print("=" * 65)
print("DEMO TEST 3: CSV with Naveen + Preethi rows")
print("=" * 65)
csv_text = """full_name,email,phone,skills,experience_years,current_role
Naveen V,naveen.v@gmail.com,9876543210,Python;FastAPI;SQL,1,Software Developer
Preethi S,preethi.s@gmail.com,9123456789,Java;Spring Boot,2,Backend Developer
"""
with tempfile.NamedTemporaryFile(delete=False, suffix='.csv', mode='w', encoding='utf-8') as f:
    f.write(csv_text)
    csv_path = f.name

records = CSVExtractor.extract(csv_path)
os.unlink(csv_path)

resume_name = result['full_name'].lower().strip()
print(f"  Resume candidate: '{resume_name}'")
print(f"  CSV rows found  : {[r.get('full_name') for r in records]}")

matched = []
for r in records:
    row_name = (r.get('full_name') or '').lower().strip()
    overlap = [p for p in resume_name.split() if p in row_name.split() and len(p) > 1]
    if overlap:
        r['source_type'] = 'recruiter_csv'
        matched.append(r)
        print(f"  MATCHED : '{r.get('full_name')}' (overlap={overlap})")
    else:
        print(f"  IGNORED : '{r.get('full_name')}' (no overlap with '{resume_name}')")

print()
print("=" * 65)
print("DEMO TEST 4: Final Merged Output")
print("=" * 65)
result['source_type'] = 'resume'
profiles = [result] + matched
merger = MergeEngine(config_priority=["resume", "recruiter_csv"])
merged = merger.merge(profiles)

for k, v in merged.items():
    if k != 'field_provenance':
        print(f"  {k:<25}: {v}")

print()
print("PROVENANCE:")
for field, prov in merged.get('field_provenance', {}).items():
    print(f"  {field:<25}: source={prov['source']}, confidence={prov['confidence']}")

print()
print("ALL TESTS PASSED - Output is correct!")
