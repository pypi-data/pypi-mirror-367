#!/usr/bin/env python3
"""
Test different output formats for annex4nlp
"""

import json
from pathlib import Path
from annex4nlp.review import (
    review_documents, 
    review_single_document,
    handle_text_review_request,
    create_review_response
)

def test_single_document_api():
    """Test single document API output"""
    print("=" * 60)
    print("TESTING SINGLE DOCUMENT API")
    print("=" * 60)
    
    pdf_file = Path("tests/test_doc2.pdf")
    if not pdf_file.exists():
        print(f"Error: {pdf_file} not found!")
        return
    
    # Test without hide_info
    print("\n1. WITHOUT hide_info:")
    result = review_single_document(pdf_file)
    print(f"Total issues: {len(result)}")
    errors = [i for i in result if i['type'] == 'error']
    warnings = [i for i in result if i['type'] == 'warning']
    info = [i for i in result if i['type'] == 'info']
    print(f"  Errors: {len(errors)}, Warnings: {len(warnings)}, Info: {len(info)}")
    
    # Test with hide_info (using create_review_response)
    print("\n2. WITH hide_info:")
    issues = review_single_document(pdf_file)
    response = create_review_response(issues, [pdf_file.name], hide_info=True)
    print(f"Total issues: {response['summary']['total_issues']}")
    print(f"  Errors: {response['summary']['errors']}, Warnings: {response['summary']['warnings']}, Info: {response['summary']['info']}")

def test_multiple_documents_api():
    """Test multiple documents API output"""
    print("\n" + "=" * 60)
    print("TESTING MULTIPLE DOCUMENTS API")
    print("=" * 60)
    
    pdf_files = [Path("tests/test_doc1.pdf"), Path("tests/test_doc2.pdf")]
    existing_files = [f for f in pdf_files if f.exists()]
    
    if not existing_files:
        print("Error: No PDF files found!")
        return
    
    print(f"Testing with {len(existing_files)} files: {[f.name for f in existing_files]}")
    
    # Test without hide_info
    print("\n1. WITHOUT hide_info:")
    result = review_documents(existing_files)
    print(f"Total issues: {len(result)}")
    errors = [i for i in result if i['type'] == 'error']
    warnings = [i for i in result if i['type'] == 'warning']
    info = [i for i in result if i['type'] == 'info']
    print(f"  Errors: {len(errors)}, Warnings: {len(warnings)}, Info: {len(info)}")
    
    # Test with hide_info
    print("\n2. WITH hide_info:")
    issues = review_documents(existing_files)
    response = create_review_response(issues, [f.name for f in existing_files], hide_info=True)
    print(f"Total issues: {response['summary']['total_issues']}")
    print(f"  Errors: {response['summary']['errors']}, Warnings: {response['summary']['warnings']}, Info: {response['summary']['info']}")

def test_text_api():
    """Test text API output"""
    print("\n" + "=" * 60)
    print("TESTING TEXT API")
    print("=" * 60)
    
    test_text = """
    This system does not collect personal data. 
    We do not store user information.
    No personal data is processed.
    """
    
    # Test without hide_info
    print("\n1. WITHOUT hide_info:")
    result = handle_text_review_request(test_text, "test.txt")
    print(f"Total issues: {result['summary']['total_issues']}")
    print(f"  Errors: {result['summary']['errors']}, Warnings: {result['summary']['warnings']}, Info: {result['summary']['info']}")
    
    # Test with hide_info
    print("\n2. WITH hide_info:")
    issues = result['issues']  # Get issues from previous result
    response = create_review_response(issues, ["test.txt"], hide_info=True)
    print(f"Total issues: {response['summary']['total_issues']}")
    print(f"  Errors: {response['summary']['errors']}, Warnings: {response['summary']['warnings']}, Info: {response['summary']['info']}")

def test_json_output():
    """Test JSON output format"""
    print("\n" + "=" * 60)
    print("TESTING JSON OUTPUT")
    print("=" * 60)
    
    pdf_file = Path("tests/test_doc2.pdf")
    if not pdf_file.exists():
        print(f"Error: {pdf_file} not found!")
        return
    
    # Test without hide_info
    print("\n1. WITHOUT hide_info (JSON):")
    result = review_single_document(pdf_file)
    response = create_review_response(result, [pdf_file.name], hide_info=False)
    print(json.dumps(response, indent=2, ensure_ascii=False))
    
    # Test with hide_info
    print("\n2. WITH hide_info (JSON):")
    response = create_review_response(result, [pdf_file.name], hide_info=True)
    print(json.dumps(response, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    test_single_document_api()
    test_multiple_documents_api()
    test_text_api()
    test_json_output() 