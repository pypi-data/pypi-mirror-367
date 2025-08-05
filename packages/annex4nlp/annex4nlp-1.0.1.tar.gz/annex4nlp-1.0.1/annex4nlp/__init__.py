"""
annex4nlp - NLP-based compliance analysis for EU AI Act Annex IV documents.

This package provides advanced natural language processing capabilities
for analyzing technical documentation for compliance with EU AI Act Annex IV
and GDPR requirements.
"""

from .review import (
    review_documents,
    review_single_document,
    analyze_text,
    extract_text_from_pdf,
    extract_pdf_pages,
    analyze_documents,
    handle_multipart_review_request,
    handle_text_review_request,
    create_review_response,
    analyze_annex_payload
)

__all__ = [
    'review_documents',
    'review_single_document', 
    'analyze_text',
    'extract_text_from_pdf',
    'extract_pdf_pages',
    'analyze_documents',
    'handle_multipart_review_request',
    'handle_text_review_request',
    'create_review_response',
    'analyze_annex_payload'
]

__version__ = "1.0.0" 