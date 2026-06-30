import os
import json
import csv

base_dir = "candidate-ai-engine/sample_data"
os.makedirs(base_dir, exist_ok=True)

# Create mock ATS JSON
ats_data = {
    "id": "12345",
    "fullName": "Jane Doe",
    "contact": {
        "email": "jane.doe@example.com",
        "phone": "+1-555-0198"
    },
    "skills": ["JavaScript", "Python", "React"]
}
with open(f"{base_dir}/ats_export.json", "w") as f:
    json.dump(ats_data, f, indent=2)

# Create mock Recruiter CSV
csv_data = [
    {"name": "Jane Doe", "email": "jane@gmail.com", "phone": "555-0198", "current_company": "Tech Corp"}
]
with open(f"{base_dir}/recruiter_notes.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=csv_data[0].keys())
    writer.writeheader()
    writer.writerows(csv_data)

# Create sample projection config
proj_config = {
    "fields": [
        {"path": "full_name", "type": "string", "required": True},
        {"path": "primary_email", "from": "emails[0]"},
        {"path": "phone", "from": "phones[0]", "normalize": "E164"}
    ],
    "include_confidence": True,
    "on_missing": "null"
}
with open(f"{base_dir}/projection_config.json", "w") as f:
    json.dump(proj_config, f, indent=2)
