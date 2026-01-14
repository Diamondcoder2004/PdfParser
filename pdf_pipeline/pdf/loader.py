"""PDF loading utilities"""

import fitz  # PyMuPDF
from pathlib import Path
from typing import Union


def load_pdf(pdf_path: Union[str, Path]):
    """
    Load a PDF document using PyMuPDF
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        fitz.Document object
    """
    pdf_path = str(pdf_path)
    doc = fitz.open(pdf_path)
    return doc


def get_page_info(page):
    """
    Get basic information about a PDF page
    
    Args:
        page: fitz.Page object
        
    Returns:
        Dictionary with page information
    """
    rect = page.rect
    return {
        "width": rect.width,
        "height": rect.height,
        "page_number": page.number,
        "rotation": page.rotation
    }


def close_pdf(doc):
    """
    Close the PDF document
    
    Args:
        doc: fitz.Document object
    """
    doc.close()