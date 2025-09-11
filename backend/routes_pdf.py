import os
from fastapi import APIRouter, HTTPException
from weasyprint import HTML
from fastapi.responses import FileResponse

router = APIRouter()

@router.post("/generate_proposal_pdf")
def generate_proposal_pdf(markdown_content: str):
    """Generate a PDF proposal from Markdown content."""
    # Convert Markdown to HTML (simple placeholder)
    html_content = f"<html><body><pre>{markdown_content}</pre></body></html>"
    pdf_path = "proposal.pdf"
    HTML(string=html_content).write_pdf(pdf_path)
    return FileResponse(pdf_path, media_type='application/pdf', filename="proposal.pdf")
