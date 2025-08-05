"""
CLI interface for annex4nlp - NLP-based compliance analysis.
"""

import typer
from pathlib import Path
from typing import List
from .review import review_documents

app = typer.Typer(
    name="annex4nlp",
    help="NLP-based compliance analysis for EU AI Act Annex IV documents",
    add_completion=False
)

@app.command()
def review(
    files: List[Path] = typer.Argument(..., exists=True, readable=True, help="One or more PDF files of technical documentation"),
    hide_info: bool = typer.Option(False, "--hide-info", "-i", help="Hide informational messages (negated terms)")
):
    """
    Perform an automatic compliance review of technical documentation PDFs (Annex IV & GDPR).
    
    Analyzes PDF files for:
    - Missing required Annex IV sections
    - Compliance keyword coverage (risk, data protection, transparency, etc.)
    - Contradictions between multiple documents
    - Potential compliance issues
    
    Output includes:
    - ERRORS: Critical compliance issues that need immediate attention
    - WARNINGS: Potential issues that should be reviewed
    - INFO: Informational messages about negated terms (can be hidden with --hide-info)
    
    ⚠️  This is an automated analysis tool. Results should be reviewed by qualified legal professionals.
    """
    # Check if PDF processing libraries are available
    try:
        import PyPDF2
        PDF2_AVAILABLE = True
    except ImportError:
        PDF2_AVAILABLE = False

    try:
        import pdfplumber
        PDFPLUMBER_AVAILABLE = True
    except ImportError:
        PDFPLUMBER_AVAILABLE = False

    try:
        import fitz  # PyMuPDF
        PYMUPDF_AVAILABLE = True
    except ImportError:
        PYMUPDF_AVAILABLE = False

    if not PDF2_AVAILABLE and not PDFPLUMBER_AVAILABLE and not PYMUPDF_AVAILABLE:
        typer.secho("ERROR: No PDF processing library available. Install PyPDF2, pdfplumber, or fitz:", fg=typer.colors.RED, err=True)
        typer.secho("  pip install PyPDF2", fg=typer.colors.YELLOW)
        typer.secho("  or", fg=typer.colors.YELLOW)
        typer.secho("  pip install pdfplumber", fg=typer.colors.YELLOW)
        typer.secho("  or", fg=typer.colors.YELLOW)
        typer.secho("  pip install PyMuPDF", fg=typer.colors.YELLOW)
        raise typer.Exit(1)
    
    typer.secho(f"Analyzing {len(files)} PDF file(s)...", fg=typer.colors.BLUE)
    
    # 1. Extract text from PDF files
    docs_pages = []
    for file in files:
        try:
            typer.secho(f"Processing {file.name}...", fg=typer.colors.BLUE)
            from .review import extract_pdf_pages
            pages = extract_pdf_pages(file)
            docs_pages.append((file.name, pages))
            total_chars = sum(len(page) for page in pages)
            typer.secho(f"  ✓ Extracted {len(pages)} pages, {total_chars} characters", fg=typer.colors.GREEN)
        except Exception as e:
            typer.secho(f"  ✗ Failed to process {file.name}: {e}", fg=typer.colors.RED, err=True)
            raise typer.Exit(1)
    
    # 2. Analyze documents for issues
    typer.secho("Analyzing documents for compliance issues...", fg=typer.colors.BLUE)
    from .review import analyze_documents, create_review_response
    issues = analyze_documents(docs_pages)
    
    # Create response with hide_info parameter
    response = create_review_response(issues, [f.name for f in files], hide_info=hide_info)
    issues = response["issues"]  # Use filtered issues
    
    # 3. Output results
    typer.secho("\n" + "="*60, fg=typer.colors.BLUE)
    typer.secho("COMPLIANCE REVIEW RESULTS", fg=typer.colors.BLUE)
    typer.secho("="*60, fg=typer.colors.BLUE)
    
    if not issues:
        typer.secho("✅ No obvious contradictions or compliance issues found.", fg=typer.colors.GREEN)
        typer.secho("\nNote: This automated analysis is not a substitute for legal review.", fg=typer.colors.YELLOW)
        typer.secho("Consult qualified legal professionals for compliance matters.", fg=typer.colors.YELLOW)
    else:
        # Group issues by type (use response data for accurate counts)
        errors = [issue for issue in issues if issue["type"] == "error"]
        warnings = [issue for issue in issues if issue["type"] == "warning"]
        info = [issue for issue in issues if issue["type"] == "info"]
        
        # Display errors first
        if errors:
            typer.secho(f"\n❌ ERRORS ({len(errors)}):", fg=typer.colors.RED)
            for i, issue in enumerate(errors, 1):
                file_info = f" [{issue['file']}]" if issue['file'] else ""
                section_info = f" (Section {issue['section']})" if issue['section'] else ""
                typer.secho(f"  {i}.{file_info}{section_info} {issue['message']}", fg=typer.colors.RED)
        
        # Display warnings
        if warnings:
            typer.secho(f"\n⚠️  WARNINGS ({len(warnings)}):", fg=typer.colors.YELLOW)
            for i, issue in enumerate(warnings, 1):
                file_info = f" [{issue['file']}]" if issue['file'] else ""
                section_info = f" (Section {issue['section']})" if issue['section'] else ""
                typer.secho(f"  {i}.{file_info}{section_info} {issue['message']}", fg=typer.colors.YELLOW)
        
        # Display info messages
        if info:
            typer.secho(f"\nℹ️  INFO ({len(info)}):", fg=typer.colors.CYAN)
            for i, issue in enumerate(info, 1):
                file_info = f" [{issue['file']}]" if issue['file'] else ""
                section_info = f" (Section {issue['section']})" if issue['section'] else ""
                typer.secho(f"  {i}.{file_info}{section_info} {issue['message']}", fg=typer.colors.CYAN)
            
            # Add footnote for info messages
            typer.secho(f"\n     Note: These informational messages indicate terms found only with negation.", fg=typer.colors.CYAN)
            typer.secho(f"     This may be intentional - please verify if the negation is correct.", fg=typer.colors.CYAN)
            typer.secho(f"     Use --hide-info flag to suppress these messages.", fg=typer.colors.CYAN)
        
        # Calculate total issues excluding hidden info
        total_visible_issues = len(errors) + len(warnings) + len(info)
        
        # Display summary with colored counts
        summary_parts = []
        if len(errors) > 0:
            summary_parts.append(f"{len(errors)} errors")
        if len(warnings) > 0:
            summary_parts.append(f"{len(warnings)} warnings")
        if len(info) > 0:
            summary_parts.append(f"{len(info)} info")
        
        summary_text = f"\nFound {total_visible_issues} total issue(s): "
        typer.secho(summary_text, fg=typer.colors.YELLOW, nl=False)
        
        # Print each part with appropriate color
        for i, part in enumerate(summary_parts):
            if "errors" in part:
                typer.secho(part, fg=typer.colors.RED, nl=False)
            elif "warnings" in part:
                typer.secho(part, fg=typer.colors.YELLOW, nl=False)
            elif "info" in part:
                typer.secho(part, fg=typer.colors.CYAN, nl=False)
            
            if i < len(summary_parts) - 1:
                typer.secho(", ", fg=typer.colors.YELLOW, nl=False)
        
        typer.secho()  # New line
        typer.secho("\nNote: This automated analysis is not a substitute for legal review.", fg=typer.colors.YELLOW)
        typer.secho("Consult qualified legal professionals for compliance matters.", fg=typer.colors.YELLOW)

if __name__ == "__main__":
    app() 