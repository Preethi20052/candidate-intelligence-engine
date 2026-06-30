# Candidate Intelligence Engine (Eightfold AI Engineering Assignment)

An enterprise-grade, deterministic data pipeline that ingests candidate profiles from multiple unstructured and structured sources (Resumes, CSVs, LinkedIn/GitHub URLs), normalizes the data, resolves conflicts via a configurable priority engine, and projects the final output into a customizable JSON schema.

Built specifically to handle the messy reality of recruiting data: missing fields, OCR glitches, ambiguous names, and conflicting source information.

---

## 🎯 Architecture & Pipeline Flow

The system is built on a strictly deterministic pipeline to guarantee reproducibility and explainability:

1. **Ingestion Layer:** Accepts unstructured files (PDF, DOCX, TXT) and structured files (CSV, JSON).
2. **Extraction Layer:** Uses Regex and heuristics (not LLMs) to deterministically extract entities. Features aggressive filtering to prevent extracting filler text ("Objective", "Motivated") as candidate names.
3. **Normalization Layer:**
   - **Phones:** Uses `phonenumbers` to validate and convert to `E.164` format.
   - **Emails:** Lowercased, stripped of PDF OCR glitches (e.g., zero-width spaces `\u200b`).
   - **Dates:** Normalized to `YYYY-MM`.
   - **Skills:** Aliased (e.g., `ml` -> `Machine Learning`) and deduplicated.
   - **Location:** Normalized to ISO-3166 alpha-2 country codes.
4. **Merge Engine (Conflict Resolution):** 
   - Uses a configurable static priority ranking (e.g., `Resume > LinkedIn > ATS CSV`).
   - Mathematically merges arrays (deduplicated union of skills/emails/phones).
   - Generates comprehensive **Field-Level Provenance** tracking the source, confidence, and timestamp for every single data point.
5. **Projection Layer:** A dynamic, configuration-driven output layer that safely reshapes the internal canonical record into any required JSON schema (handling renaming, flattening, and missing-field policies) without mutating the master record.

---

## 🛡️ Edge Cases Handled

This pipeline is battle-tested against real-world data corruption:

- **Cross-Candidate Data Bleeding:** Implements exact-word intersection matching to prevent "John S" from maliciously or accidentally merging with "John Smith".
- **Invisible OCR Glitches:** Pre-processes PDF text to strip zero-width spaces (`\u200b`) and malformed `mailto:` tags before regex extraction.
- **URL False Positives:** Strips URLs prior to phone number extraction to prevent 9-digit LinkedIn IDs from being parsed as international phone numbers.
- **Filename Heuristics:** Intelligently extracts names from filenames (`Preethi_Resume.pdf` -> `Preethi`) while explicitly blacklisting common job titles (`AI`, `Engineer`, `Developer`) to prevent hallucinated names.
- **Graceful Degradation:** Malformed CSV rows are skipped individually rather than crashing the ingestion batch.

---

## ⚙️ System Requirements

- **OS:** Windows / macOS / Linux
- **Python:** 3.9+
- **Memory:** 2GB RAM minimum

---

## 🚀 Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Preethi20052/candidate-intelligence-engine.git
   cd candidate-intelligence-engine
   ```

2. **Create a Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Streamlit Dashboard**
   ```bash
   streamlit run frontend/streamlit/dashboard.py
   ```

---

## 🧪 Running the Test Suite

The project includes a comprehensive suite of 40+ unit tests covering all edge cases in the Normalization and Merge engines.

```bash
pytest tests/ -v
```

---

## 📊 Configurable Output (The Projection Layer)

The system maintains a massive **Internal Canonical Record** containing every piece of data and its provenance. You can shape the final output dynamically using a YAML/JSON configuration.

**Example Projection Config:**
```json
{
  "fields": [
    {"path": "candidate_name", "from": "full_name"},
    {"path": "primary_contact", "from": "emails[0]"}
  ],
  "include_provenance": false,
  "on_missing": "omit"
}
```

This ensures the downstream API gets exactly the schema it expects, while the system retains full historical data integrity.
