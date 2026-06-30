import pytest
import sys
import os

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from app.normalizers.base import Normalizer
from app.merge_engine.merger import MergeEngine
from app.projection.projector import ProjectionEngine

def test_email_normalization():
    assert Normalizer.normalize_email(" Test@EXAMPLE.com ") == "test@example.com"

def test_merge_engine_priority():
    profiles = [
        {"source_type": "recruiter_csv", "phone": "555-1234"},
        {"source_type": "resume", "phone": "999-9999"}
    ]
    merger = MergeEngine(config_priority=["resume", "recruiter_csv"])
    merged = merger.merge(profiles)
    assert merged["phone"] == "999-9999"
    assert merged["field_provenance"]["phone"]["source"] == "resume"

def test_projection_layer_remap_and_omit():
    canonical = {
        "emails": ["jane@example.com"],
        "field_provenance": {}
    }
    config = {
        "fields": [
            {"path": "primary_email", "from": "emails[0]"},
            {"path": "missing_field"}
        ],
        "on_missing": "omit"
    }
    projected = ProjectionEngine.project(canonical, config)
    assert projected.get("primary_email") == "jane@example.com"
    assert "missing_field" not in projected
