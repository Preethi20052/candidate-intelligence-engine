# ⚡ Candidate Intelligence Engine
**Eightfold AI Engineering Assignment**

This repository contains a purely deterministic, multi-source data transformer that ingests messy candidate records (PDF Resumes, ATS JSONs, Recruiter CSVs) and deterministically merges them into a single, highly-confident canonical profile.

## 🛠️ System Requirements
To run this project on your local machine, you will need:
* **Operating System:** Windows, macOS, or Linux
* **Python Version:** Python 3.9 or higher (Tested on 3.12/3.14)
* **Memory:** Minimum 4GB RAM (lightweight extraction)

## 🚀 How to Run Locally

1. **Clone the Repository**
   ```bash
   git clone https://github.com/<your-username>/<your-repo-name>.git
   cd <your-repo-name>/candidate-ai-engine
   ```

2. **Create a Virtual Environment**
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch the Dashboard UI**
   ```bash
   streamlit run frontend/streamlit/dashboard.py
   ```
   The engine will automatically open in your default browser at `http://localhost:8501`.

## 🧪 How to Test the Pipeline
This repository includes a `sample_data/` folder containing an ATS JSON export, a Recruiter CSV, and a Projection Configuration JSON. 

1. Open the UI at `http://localhost:8501`.
2. Navigate to the **"Upload & Process"** tab.
3. Upload any combinations of structured data (CSV/JSON) from the `sample_data/` folder, or upload any PDF Resume you have locally.
4. Click **"Process Pipeline"**.
5. Navigate to the **"Results & Analytics"** tab to see the side-by-side comparison of the raw Canonical Profile vs. the dynamically Projected JSON output.

## ✅ Running Unit Tests
To verify the determinism of the Normalizers and Merge Engine, you can run the pytest suite:
```bash
pytest tests/
```

## 🏗️ Architecture & Edge Cases
Please refer to the `Eightfold_Design_Document.pdf` included in the root directory for a full architectural breakdown, schema mapping rules, and edge case handling documentation.
