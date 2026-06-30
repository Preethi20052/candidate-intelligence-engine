# Candidate Intelligence Engine
### Multi-Source Deterministic Candidate Data Transformer

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-red?style=for-the-badge&logo=streamlit)
![Pydantic](https://img.shields.io/badge/Pydantic-2.x-green?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)
![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen?style=for-the-badge)

---

## Overview

The **Candidate Intelligence Engine** is a purely **deterministic**, multi-source data transformer that ingests messy, conflicting candidate records from multiple real-world sources — PDF Resumes, ATS JSON exports, and Recruiter CSV files — and merges them into a single, highly-confident, traceable **Canonical Profile**.

Every field in the output is traceable to its exact source. The same inputs will always produce the same output — **guaranteed**.

---

## Features

- **Multi-Source Ingestion** — Accepts PDF Resumes, DOCX files, ATS JSON exports, and Recruiter CSVs simultaneously
- **Deterministic Conflict Resolution** — Priority-based merge engine resolves conflicts without guessing or hallucination
- **E.164 Phone Normalization** — All phone numbers are standardized to international format
- **Field-Level Provenance** — Every output field tracks exactly which source it came from and with what confidence score
- **Configurable Projection Layer** — Dynamically reshape the output JSON at runtime without changing backend logic
- **Interactive Dashboard** — Premium Streamlit UI with side-by-side Canonical vs Projected JSON comparison
- **Zero LLM Dependency** — 100% deterministic pipeline using pure Python — no API keys required

---

## System Requirements

| Requirement | Minimum | Recommended |
|---|---|---|
| **Operating System** | Windows 10 / macOS 11 / Ubuntu 20.04 | Windows 11 / macOS 13 / Ubuntu 22.04 |
| **Python Version** | 3.9 | 3.12+ |
| **RAM** | 4 GB | 8 GB |
| **Disk Space** | 500 MB | 1 GB |
| **Internet** | Required for `pip install` only | — |

> **No Docker required.** Runs directly with Python and a virtual environment.

---

## Project Structure

```
candidate-intelligence-engine/
│
├── backend/
│   └── app/
│       ├── extractors/          # PDF, DOCX, CSV, JSON parsers
│       ├── normalizers/         # Phone, email, date formatters
│       ├── merge_engine/        # Priority-based conflict resolution
│       ├── projection/          # Runtime output configuration layer
│       ├── canonicalizers/      # Skills & job title standardization
│       └── schemas/             # Pydantic validation models
│
├── frontend/
│   └── streamlit/
│       └── dashboard.py         # Premium interactive UI
│
├── sample_data/
│   ├── ats_export.json          # Sample ATS data
│   ├── recruiter_notes.csv      # Sample recruiter CSV
│   └── projection_config.json   # Sample projection config
│
├── tests/
│   └── test_pipeline.py         # Unit tests for all pipeline layers
│
├── requirements.txt             # All Python dependencies
└── README.md
```

---

## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/Preethi20052/candidate-intelligence-engine.git
cd candidate-intelligence-engine
```

### 2. Create a Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Launch the Dashboard
```bash
streamlit run frontend/streamlit/dashboard.py
```

The app will automatically open at **http://localhost:8501**

---

## How to Use

1. **Home Tab** — Overview of the engine and pipeline steps
2. **Upload & Process Tab** — Upload any combination of:
   - PDF / DOCX Resume (Unstructured)
   - ATS JSON export (Structured)
   - Recruiter CSV (Structured)
3. **Results & Analytics Tab** — View the side-by-side comparison:
   - **Left Panel:** Full Internal Canonical Profile with provenance tracking
   - **Right Panel:** Dynamically projected output (renamed keys, omitted fields)
4. **Configuration Tab** — Set the source priority order for conflict resolution

---

## Running Tests

```bash
pytest tests/
```

All 3 unit tests cover:
- `Normalizer` — Phone and email formatting accuracy
- `MergeEngine` — Priority-based conflict resolution correctness
- `ProjectionEngine` — Dynamic field renaming and missing-value policies

---

## Architecture

```
┌──────────────┐    ┌────────────┐    ┌────────────┐    ┌──────────────┐    ┌────────────┐
│   Ingest     │───▶│  Extract   │───▶│ Normalize  │───▶│    Merge     │───▶│  Project   │
│ PDF/CSV/JSON │    │  Parsers   │    │ E.164/ISO  │    │ Priority     │    │  Layer     │
└──────────────┘    └────────────┘    └────────────┘    │ Resolution   │    └─────┬──────┘
                                                         └──────────────┘          │
                                                                                   ▼
                                                                         ┌──────────────────┐
                                                                         │  Canonical JSON  │
                                                                         │  + Provenance    │
                                                                         └──────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12 |
| UI Framework | Streamlit |
| PDF Parsing | PyMuPDF (fitz) |
| DOCX Parsing | python-docx |
| Phone Normalization | Google phonenumbers |
| Schema Validation | Pydantic v2 |
| Charts | Plotly |
| Testing | Pytest |

---

## Edge Cases Handled

- ✅ Conflicting field values across multiple sources
- ✅ Missing required fields (null / omit / error policies)
- ✅ Mismatched phone number formats → forced to E.164
- ✅ Case sensitivity and whitespace in emails
- ✅ Corrupt or unreadable file encoding

---

## License

This project is licensed under the **MIT License**.

---

<p align="center">Built with Python · Streamlit · Pydantic</p>
