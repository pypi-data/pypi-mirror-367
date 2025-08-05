#!/usr/bin/env python3
"""
Test script to analyze real PDF files with annex4nlp
"""

from pathlib import Path
from annex4nlp import review_documents, review_single_document
import json

def test_single_document():
    """Test analysis of a single PDF document"""
    print("=== Testing Single Document Analysis ===")
    
    pdf_file = Path("test_doc1.pdf")
    if not pdf_file.exists():
        print(f"Error: {pdf_file} not found!")
        return
    
    print(f"Analyzing: {pdf_file}")
    issues = review_single_document(pdf_file)
    
    print(f"Found {len(issues)} issues:")
    for i, issue in enumerate(issues, 1):
        print(f"{i}. [{issue['type'].upper()}] {issue['message']}")
        if issue.get('section'):
            print(f"   Section: {issue['section']}")
        if issue.get('file'):
            print(f"   File: {issue['file']}")
        print()

def test_multiple_documents():
    """Test analysis of multiple PDF documents"""
    print("=== Testing Multiple Documents Analysis ===")
    
    pdf_files = [
        Path("test_doc1.pdf"),
        Path("test_doc2.pdf"),
        Path("test_doc3.pdf"),
        Path("test_doc4.pdf")
    ]
    
    # Check which files exist
    existing_files = [f for f in pdf_files if f.exists()]
    if not existing_files:
        print("Error: No PDF files found!")
        return
    
    print(f"Analyzing {len(existing_files)} documents:")
    for f in existing_files:
        print(f"  - {f}")
    
    issues = review_documents(existing_files)
    
    print(f"\nFound {len(issues)} total issues:")
    
    # Group issues by type
    errors = [i for i in issues if i['type'] == 'error']
    warnings = [i for i in issues if i['type'] == 'warning']
    
    print(f"  Errors: {len(errors)}")
    print(f"  Warnings: {len(warnings)}")
    
    # Show cross-document issues first
    cross_doc_issues = [i for i in issues if i.get('file') == '']
    if cross_doc_issues:
        print("\nCross-document issues:")
        for i, issue in enumerate(cross_doc_issues, 1):
            print(f"{i}. [{issue['type'].upper()}] {issue['message']}")
    
    # Show file-specific issues
    file_issues = [i for i in issues if i.get('file') != '']
    if file_issues:
        print("\nFile-specific issues:")
        for i, issue in enumerate(file_issues, 1):
            print(f"{i}. [{issue['type'].upper()}] {issue['message']}")
            print(f"   File: {issue['file']}")
            if issue.get('section'):
                print(f"   Section: {issue['section']}")

def test_specific_scenarios():
    """Test specific scenarios with different combinations"""
    print("\n=== Testing Specific Scenarios ===")
    
    # Test 1: Contradictory documents (doc1 vs doc2)
    print("\n1. Testing contradictory documents (doc1 vs doc2):")
    files = [Path("test_doc1.pdf"), Path("test_doc2.pdf")]
    if all(f.exists() for f in files):
        issues = review_documents(files)
        cross_doc = [i for i in issues if i.get('file') == '']
        print(f"   Cross-document issues found: {len(cross_doc)}")
        for issue in cross_doc:
            print(f"   - {issue['message']}")
    
    # Test 2: Incomplete document (doc3)
    print("\n2. Testing incomplete document (doc3):")
    file = Path("test_doc3.pdf")
    if file.exists():
        issues = review_single_document(file)
        missing_sections = [i for i in issues if 'Missing content for Annex IV section' in i['message']]
        print(f"   Missing sections found: {len(missing_sections)}")
        for issue in missing_sections[:3]:  # Show first 3
            print(f"   - {issue['message']}")
    
    # Test 3: GDPR violations (doc4)
    print("\n3. Testing GDPR violations (doc4):")
    file = Path("test_doc4.pdf")
    if file.exists():
        issues = review_single_document(file)
        gdpr_issues = [i for i in issues if 'GDPR' in i['message'] or 'personal data' in i['message'].lower()]
        print(f"   GDPR-related issues found: {len(gdpr_issues)}")
        for issue in gdpr_issues:
            print(f"   - {issue['message']}")

def save_results():
    """Save analysis results to JSON file"""
    print("\n=== Saving Results ===")
    
    all_files = [Path(f"test_doc{i}.pdf") for i in range(1, 5)]
    existing_files = [f for f in all_files if f.exists()]
    
    if not existing_files:
        print("No PDF files found for analysis!")
        return
    
    issues = review_documents(existing_files)
    
    results = {
        "files_analyzed": [str(f) for f in existing_files],
        "total_issues": len(issues),
        "issues": issues,
        "summary": {
            "errors": len([i for i in issues if i['type'] == 'error']),
            "warnings": len([i for i in issues if i['type'] == 'warning']),
            "cross_document_issues": len([i for i in issues if i.get('file') == ''])
        }
    }
    
    with open("analysis_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"Results saved to analysis_results.json")
    print(f"Total issues: {results['summary']['errors']} errors, {results['summary']['warnings']} warnings")

if __name__ == "__main__":
    test_single_document()
    test_multiple_documents()
    test_specific_scenarios()
    save_results() 