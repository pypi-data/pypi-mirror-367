#!/usr/bin/env python3
"""
Basic tests for annex4nlp package
"""

import pytest
from annex4nlp import analyze_text, review_documents
from pathlib import Path


def test_analyze_text_basic():
    """Test basic text analysis functionality."""
    text = "This AI system processes personal data."
    
    issues = analyze_text(text, "test_doc.pdf")
    
    # Should return a list of issues
    assert isinstance(issues, list)
    
    # Each issue should be a dictionary with required fields
    for issue in issues:
        assert isinstance(issue, dict)
        assert "type" in issue
        assert "message" in issue
        assert "file" in issue
        assert issue["type"] in ["error", "warning"]


def test_analyze_text_missing_sections():
    """Test detection of missing Annex IV sections."""
    text = "This is a high-risk AI system."
    
    issues = analyze_text(text, "test_doc.pdf")
    
    # Should find missing sections as errors
    error_issues = [issue for issue in issues if issue["type"] == "error"]
    assert len(error_issues) > 0
    
    # Should find missing section 1 (system overview)
    section_1_errors = [
        issue for issue in error_issues 
        if issue.get("section") == "1" and "system overview" in issue["message"].lower()
    ]
    assert len(section_1_errors) > 0


def test_analyze_text_gdpr_issues():
    """Test GDPR compliance detection."""
    text = "Personal data is stored without consent or legal basis."
    
    issues = analyze_text(text, "test_doc.pdf")
    
    # Should find GDPR-related warnings
    gdpr_warnings = [
        issue for issue in issues 
        if issue["type"] == "warning" and "gdpr" in issue["message"].lower()
    ]
    assert len(gdpr_warnings) > 0


def test_review_documents_function_exists():
    """Test that review_documents function is available."""
    # This test just ensures the function exists and is callable
    assert callable(review_documents)


if __name__ == "__main__":
    pytest.main([__file__]) 