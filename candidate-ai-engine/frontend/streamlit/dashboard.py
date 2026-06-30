import streamlit as st
import pandas as pd
import json
import os
import sys
import tempfile
import pathlib
import importlib

# Add backend to path — always insert fresh so reloads work
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend'))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Force reload all backend modules so Streamlit never uses stale cache
import app.extractors.resume_parser as _rp; importlib.reload(_rp)
import app.extractors.csv_extractor as _ce; importlib.reload(_ce)
import app.extractors.json_extractor as _je; importlib.reload(_je)
import app.merge_engine.merger as _me; importlib.reload(_me)
import app.normalizers.base as _nb; importlib.reload(_nb)
import app.projection.projector as _pp; importlib.reload(_pp)

from app.extractors.resume_parser import ResumeParser
from app.extractors.csv_extractor import CSVExtractor
from app.extractors.json_extractor import JSONExtractor
from app.merge_engine.merger import MergeEngine
from app.projection.projector import ProjectionEngine

st.set_page_config(
    page_title="Eightfold AI | Candidate Intelligence Engine",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded"
)

if 'canonical_profile' not in st.session_state:
    st.session_state.canonical_profile = None

# PREMIUM UI INJECTION (HTML/CSS)
st.markdown("""
<style>
    /* Main Background with subtle gradient */
    .stApp {
        background: linear-gradient(135deg, #E0F2FE 0%, #F0F9FF 100%);
        color: #1E3A8A;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Glassmorphism Sidebar */
    section[data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255,255,255,0.5);
    }
    
    /* Unique HTML Cards for Metrics/Headers */
    .custom-html-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.05);
        border-left: 5px solid #2563EB;
        transition: transform 0.3s ease;
        margin-bottom: 20px;
    }
    .custom-html-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 25px rgba(0,0,0,0.1);
    }
    
    /* Buttons Primary Blue */
    .stButton>button { 
        background: linear-gradient(90deg, #2563EB, #3B82F6);
        color: white; 
        border-radius: 8px; 
        border: none;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(37, 99, 235, 0.2);
    }
    .stButton>button:hover { 
        background: linear-gradient(90deg, #1D4ED8, #2563EB);
        transform: scale(1.02);
    }
    
    /* Navigation Selectbox */
    div[data-baseweb="select"] > div {
        background-color: #F8FAFC; 
        color: #1E3A8A;
        border: 1px solid #93C5FD;
        border-radius: 10px;
    }
    
    /* Text elements */
    p, div, h1, h2, h3, h4, h5, h6 {
        color: #1E3A8A; 
    }
    
    /* Sidebar Navigation Font Size */
    section[data-testid="stSidebar"] .stRadio p {
        font-size: 1.25rem !important;
        font-weight: 500;
        padding-top: 5px;
        padding-bottom: 5px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="custom-html-card" style="border-left: 5px solid #06B6D4;">
    <h1 style="margin:0; font-size: 2.2rem;">Candidate Intelligence Engine</h1>
    <p style="margin:0; color: #64748B;">Multi-Source Deterministic Data Transformer</p>
</div>
""", unsafe_allow_html=True)

menu = ["Home", "Upload & Process", "Results & Analytics", "Configuration"]
choice = st.sidebar.radio("Navigation", menu)

if choice == "Home":

    # ── 1. OVERVIEW ─────────────────────────────────────────────────
    st.markdown("""
<div style="background:white; padding:28px 32px; border-radius:14px;
            box-shadow:0 2px 12px rgba(0,0,0,0.06); margin-bottom:24px;">
    <h2 style="margin:0 0 10px 0; color:#1E3A8A; font-size:1.3rem; font-weight:700;
               letter-spacing:0.3px;">Overview</h2>
    <p style="margin:0; color:#475569; font-size:1rem; line-height:1.75;">
        <b>Candidate Intelligence Engine</b> is a deterministic AI engineering application that
        transforms structured and unstructured candidate data into a unified canonical profile
        using configurable projection, provenance tracking, confidence scoring, and validation.
    </p>
</div>
""", unsafe_allow_html=True)

    # ── 2. PROCESSING PIPELINE ───────────────────────────────────────
    st.markdown("""
<div style="background:white; padding:28px 32px; border-radius:14px;
            box-shadow:0 2px 12px rgba(0,0,0,0.06); margin-bottom:24px;">
    <h2 style="margin:0 0 20px 0; color:#1E3A8A; font-size:1.3rem; font-weight:700;">
        Processing Pipeline
    </h2>
    <div style="display:flex; flex-direction:column; align-items:flex-start; gap:0;">
""", unsafe_allow_html=True)

    pipeline_steps = [
        ("🔎", "Source Detection",    "Identifies file types and URL sources"),
        ("📄", "Extraction",          "Parses entities using deterministic regex"),
        ("⚙️", "Normalization",       "E.164 · lowercase · YYYY-MM · ISO-3166"),
        ("🔗", "Entity Resolution",   "Matches candidates across sources by name"),
        ("🔀", "Conflict Resolution", "Priority ranking resolves conflicting values"),
        ("🗄️", "Canonical Profile",   "Immutable master record with full provenance"),
        ("🎛️", "Projection",          "Runtime config reshapes the output schema"),
        ("✅", "Validation",          "Pydantic validates every projected output"),
    ]

    for i, (icon, title, desc) in enumerate(pipeline_steps):
        connector = "" if i == len(pipeline_steps) - 1 else """
<div style="width:2px; height:18px; background:#BFDBFE; margin-left:19px;"></div>"""
        st.markdown(f"""
<div style="display:flex; align-items:center; gap:14px;">
    <div style="width:38px; height:38px; border-radius:50%; background:#EFF6FF;
                border:2px solid #3B82F6; display:flex; align-items:center;
                justify-content:center; font-size:1rem; flex-shrink:0;">{icon}</div>
    <div>
        <span style="font-weight:700; color:#1E3A8A; font-size:0.95rem;">{title}</span>
        <span style="color:#64748B; font-size:0.85rem; margin-left:10px;">{desc}</span>
    </div>
</div>{connector}
""", unsafe_allow_html=True)

    st.markdown("</div></div>", unsafe_allow_html=True)

    # ── 3. SUPPORTED INPUT SOURCES ───────────────────────────────────
    st.markdown("""
<h2 style="color:#1E3A8A; font-size:1.3rem; font-weight:700; margin-bottom:14px;">
    Supported Input Sources
</h2>
""", unsafe_allow_html=True)

    src_col1, src_col2 = st.columns(2)
    with src_col1:
        st.markdown("""
<div style="background:white; padding:24px 28px; border-radius:14px;
            box-shadow:0 2px 12px rgba(0,0,0,0.06); height:100%;">
    <div style="font-size:0.7rem; font-weight:700; letter-spacing:1.5px;
                color:#3B82F6; margin-bottom:12px; text-transform:uppercase;">
        Structured Sources
    </div>
    <ul style="margin:0; padding-left:18px; color:#334155; line-height:2.0; font-size:0.95rem;">
        <li>Recruiter CSV</li>
        <li>ATS JSON Export</li>
    </ul>
</div>
""", unsafe_allow_html=True)

    with src_col2:
        st.markdown("""
<div style="background:white; padding:24px 28px; border-radius:14px;
            box-shadow:0 2px 12px rgba(0,0,0,0.06); height:100%;">
    <div style="font-size:0.7rem; font-weight:700; letter-spacing:1.5px;
                color:#06B6D4; margin-bottom:12px; text-transform:uppercase;">
        Unstructured Sources
    </div>
    <ul style="margin:0; padding-left:18px; color:#334155; line-height:2.0; font-size:0.95rem;">
        <li>Resume PDF</li>
        <li>Resume DOCX</li>
        <li>Recruiter Notes TXT</li>
        <li>GitHub Profile URL</li>
    </ul>
</div>
""", unsafe_allow_html=True)

    # ── 4. SYSTEM HIGHLIGHTS ─────────────────────────────────────────
    st.markdown("""
<h2 style="color:#1E3A8A; font-size:1.3rem; font-weight:700;
           margin-top:28px; margin-bottom:14px;">
    System Highlights
</h2>
""", unsafe_allow_html=True)

    highlights = [
        ("🔁", "Deterministic Processing",
         "Same input always produces identical output. No randomness, no LLMs."),
        ("🎛️", "Runtime Configurable Projection",
         "Rename fields, subset, and toggle provenance — zero code changes."),
        ("🎯", "Confidence Scoring",
         "Weighted confidence computed per-field and aggregated as an overall score."),
        ("📜", "Provenance Tracking",
         "Every value carries its source, method, confidence, and timestamp."),
        ("✅", "Pydantic Validation",
         "Strict schema validation on every projected output before it is served."),
        ("💡", "Explainable Decisions",
         "Every conflict resolution decision is auditable and fully traceable."),
    ]

    h_col1, h_col2, h_col3 = st.columns(3)
    cols = [h_col1, h_col2, h_col3]
    for i, (icon, title, desc) in enumerate(highlights):
        with cols[i % 3]:
            st.markdown(f"""
<div style="background:white; padding:22px 20px; border-radius:14px;
            box-shadow:0 2px 12px rgba(0,0,0,0.06); margin-bottom:16px;
            border-top:3px solid #3B82F6;">
    <div style="font-size:1.6rem; margin-bottom:10px;">{icon}</div>
    <div style="font-weight:700; color:#1E3A8A; font-size:0.95rem;
                margin-bottom:6px;">{title}</div>
    <div style="color:#64748B; font-size:0.83rem; line-height:1.6;">{desc}</div>
</div>
""", unsafe_allow_html=True)

elif choice == "Upload & Process":
    st.header("Upload Sources")
    st.write("Upload any combination of structured or unstructured data sources.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Unstructured Sources")
        unstruct_file = st.file_uploader("Upload Resume/Notes", type=["pdf", "docx", "txt"])
        github_url = st.text_input("GitHub URL")
        linkedin_url = st.text_input("LinkedIn URL")
        
    with col2:
        st.subheader("Structured Sources")
        struct_file = st.file_uploader("Upload ATS/Recruiter Data", type=["csv", "json"])
        
    if st.button("Process Pipeline"):
        st.session_state.canonical_profile = None  # Clear previous data
        if unstruct_file or struct_file or github_url or linkedin_url:
            with st.spinner("Executing Deterministic Pipeline..."):
                profiles = []
                
                # Unstructured File
                if unstruct_file:
                    ext = pathlib.Path(unstruct_file.name).suffix.lower()
                    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                        tmp.write(unstruct_file.getvalue())
                        tmp_path = tmp.name
                    parser = ResumeParser()
                    profile = parser.parse_file(tmp_path, ext,
                                                filename_hint=unstruct_file.name)
                    if profile:
                        profile['source_type'] = 'resume'
                        profile['filename'] = unstruct_file.name
                        profiles.append(profile)
                
                # Structured File
                if struct_file:
                    ext = pathlib.Path(struct_file.name).suffix.lower()
                    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                        tmp.write(struct_file.getvalue())
                        tmp_path = tmp.name
                    if ext == '.csv':
                        records = CSVExtractor.extract(tmp_path)
                        # Get resume candidate name for matching
                        resume_name = None
                        for p in profiles:
                            if p.get('source_type') == 'resume' and p.get('full_name') and p.get('full_name') != 'Unknown':
                                resume_name = p['full_name'].lower().strip()
                                break
                        
                        matched = []
                        for r in records:
                            row_name = (r.get('full_name') or r.get('name') or '').lower().strip()
                            # If resume name found, only add matching CSV rows
                            if resume_name:
                                overlap = [p for p in resume_name.split() if p in row_name.split() and len(p) > 1]
                                if overlap:
                                    r['source_type'] = 'recruiter_csv'
                                    matched.append(r)
                            else:
                                # No resume — take all rows
                                r['source_type'] = 'recruiter_csv'
                                matched.append(r)
                        
                        if not matched and records:
                            # No match found — do NOT blindly add first row
                            # Show a clear warning to the user instead
                            st.warning(
                                f"No CSV row matched the resume candidate "
                                f"**'{resume_name or 'Unknown'}'**. "
                                f"Found these names in CSV: "
                                f"{[r.get('full_name','?') for r in records]}. "
                                f"Only resume data will be used."
                            )
                        
                        profiles.extend(matched)
                    elif ext == '.json':
                        records = JSONExtractor.extract(tmp_path)
                        for r in records:
                            r['source_type'] = 'ats_json'
                            profiles.append(r)
                
                # URLs
                if github_url:
                    profiles.append({"source_type": "github", "links": [github_url], "skills": ["GitHub User"]})
                if linkedin_url:
                    profiles.append({"source_type": "linkedin", "links": [linkedin_url], "headline": "LinkedIn Profile Extracted"})
                
                # Merge Profiles
                if profiles:
                    priority = st.session_state.get("config_priority", ["resume", "linkedin", "ats_json", "recruiter_csv", "github"])
                    merger = MergeEngine(config_priority=priority)
                    merged_profile = merger.merge(profiles)
                    st.session_state.canonical_profile = merged_profile
                    
                    # Apply Projection Config (The Required Twist)
                    sample_proj_config = {
                        "fields": [
                            {"path": "candidate_full_name", "from": "full_name"},
                            {"path": "primary_contact_email", "from": "emails[0]"},
                            {"path": "verified_phone", "from": "phones[0]"}
                        ],
                        "include_provenance": False,
                        "include_confidence": False,
                        "on_missing": "omit"
                    }
                    st.session_state.projected_profile = ProjectionEngine.project(merged_profile, sample_proj_config)
                    
                st.progress(100)
                st.success("Pipeline executed successfully!")
                st.info("Navigate to 'Results & Analytics' to view the canonical profile.")
                
                # Debug: show what each source produced
                with st.expander("🔍 Debug: Raw Profiles Before Merge"):
                    for p in profiles:
                        st.write(f"**Source:** `{p.get('source_type')}`")
                        st.json({k: v for k, v in p.items() if k != 'source_type'})
        else:
            st.warning("Please upload at least one file or provide a URL.")

elif choice == "Results & Analytics":
    st.header("Canonical Profile & Insights")
    if st.session_state.canonical_profile:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.subheader("Internal Canonical Profile")
            st.info("The rigid internal record containing all parsed fields and provenance tracking.")
            st.json(st.session_state.canonical_profile)
        with col2:
            st.subheader("Projected JSON (The Twist)")
            st.warning("Dynamic runtime output: Renamed keys, omitted provenance, strict subsetting.")
            
            proj_mode = st.radio(
                "Select Runtime Configuration:", 
                ["Output A (Default Schema)", "Output B (Custom Twist)"], 
                horizontal=True
            )
            
            if proj_mode == "Output A (Default Schema)":
                current_proj_config = {
                    "fields": [
                        {"path": "candidate_name", "from": "full_name"},
                        {"path": "primary_email", "from": "emails[0]"},
                        {"path": "contact_number", "from": "phones[0]"},
                        {"path": "core_skills", "from": "skills"}
                    ],
                    "include_provenance": True,
                    "include_confidence": True,
                    "on_missing": "null"
                }
            else:
                current_proj_config = {
                    "fields": [
                        {"path": "candidate_full_name", "from": "full_name"},
                        {"path": "primary_contact_email", "from": "emails[0]"},
                        {"path": "verified_phone", "from": "phones[0]"}
                    ],
                    "include_provenance": False,
                    "include_confidence": False,
                    "on_missing": "omit"
                }
            
            # Project dynamically based on UI selection
            dynamic_projection = ProjectionEngine.project(st.session_state.canonical_profile, current_proj_config)
            st.json(dynamic_projection)
            
            st.divider()
            st.subheader("🧠 AI Insights")

            canonical = st.session_state.canonical_profile
            provenance = canonical.get("field_provenance", {})
            overall_confidence = canonical.get("overall_confidence", 0.0)

            # --- Sources Processed ---
            sources_seen = set()
            for prov in provenance.values():
                src = prov.get("source", "")
                if src:
                    sources_seen.add(src)
            sources_count = max(len(sources_seen), 1)

            # --- Total Fields Extracted ---
            total_fields = len(provenance)

            # --- Overall Confidence as % ---
            confidence_pct = int(round(overall_confidence * 100))

            # --- Validation Status ---
            required_fields = ["full_name", "emails", "phones"]
            all_present = all(canonical.get(f) for f in required_fields)
            validation_status = "Passed" if all_present else "Failed"

            # --- Data Quality (deterministic) ---
            optional_fields_all = [
                "skills", "location", "education", "current_role",
                "current_company", "notice_period", "preferred_role",
                "experience_years", "expected_salary", "notes"
            ]
            filled_optional = sum(1 for f in optional_fields_all if canonical.get(f))
            completeness = (filled_optional / len(optional_fields_all)) * 100
            if completeness >= 80 and confidence_pct >= 85:
                data_quality = "Excellent"
            elif completeness >= 60 and confidence_pct >= 70:
                data_quality = "Good"
            elif completeness >= 40:
                data_quality = "Fair"
            else:
                data_quality = "Poor"

            # --- Missing Optional Fields ---
            optional_display = {
                "linkedin_url": "LinkedIn URL",
                "github_url": "GitHub URL",
                "certifications": "Certifications",
                "expected_salary": "Expected Salary",
                "experience_years": "Experience Years",
                "notice_period": "Notice Period",
            }
            missing_optional = [
                label for key, label in optional_display.items()
                if not canonical.get(key)
            ]
            missing_text = ", ".join(missing_optional) if missing_optional else "None"

            # --- Render the card ---
            val_icon = "✅" if validation_status == "Passed" else "❌"
            quality_colors = {
                "Excellent": "🟢", "Good": "🔵", "Fair": "🟡", "Poor": "🔴"
            }
            quality_icon = quality_colors.get(data_quality, "⚪")

            st.markdown(f"""
| Metric | Value |
|---|---|
| 📄 Sources Processed | {sources_count} |
| 📋 Total Fields Extracted | {total_fields} |
| 🎯 Overall Confidence | {confidence_pct}% |
| {val_icon} Validation Status | {validation_status} |
| {quality_icon} Data Quality | {data_quality} |
| ⚠️ Missing Optional Fields | {missing_text} |
""")
    else:
        st.info("No profile processed yet. Please upload files in 'Upload & Process'.")

elif choice == "Configuration":
    st.header("Pipeline Configuration")
    
    st.markdown("Drag and drop to reorder the priority of sources when resolving conflicts.")
    priority = st.multiselect(
        "Source Merge Priority",
        ["resume", "linkedin", "ats_json", "recruiter_csv", "github"],
        default=st.session_state.get("config_priority", ["resume", "linkedin", "ats_json", "recruiter_csv", "github"])
    )
    
    if st.button("Save Configuration"):
        st.session_state.config_priority = priority
        st.success("✅ Configuration saved! The pipeline will now use this priority order for entity resolution.")
