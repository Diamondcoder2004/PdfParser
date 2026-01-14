"""Text extraction module using PyMuPDF"""

import fitz
import re
from typing import List, Dict, Any


def extract_text(page: fitz.Page) -> str:
    """
    Extract text from a PDF page using PyMuPDF
    
    Args:
        page: fitz.Page object
        
    Returns:
        Extracted text string
    """
    # Extract text in different formats to capture various text elements
    text = page.get_text("text")
    return text


def extract_text_with_formatting(page: fitz.Page) -> List[Dict[str, Any]]:
    """
    Extract text with formatting information
    
    Args:
        page: fitz.Page object
        
    Returns:
        List of dictionaries containing text and formatting info
    """
    # Get text as dictionary with formatting info
    blocks = page.get_text("dict")["blocks"]
    
    formatted_text = []
    
    for block in blocks:
        if "lines" in block:
            for line in block["lines"]:
                for span in line["spans"]:
                    text_element = {
                        "text": span["text"],
                        "bbox": span["bbox"],  # (x0, y0, x1, y1)
                        "size": span["size"],
                        "font": span.get("font", ""),
                        "flags": span.get("flags", 0)
                    }
                    formatted_text.append(text_element)
    
    return formatted_text


def extract_text_by_blocks(page: fitz.Page) -> List[Dict[str, Any]]:
    """
    Extract text organized by blocks
    
    Args:
        page: fitz.Page object
        
    Returns:
        List of text blocks with position information
    """
    blocks = page.get_text("dict")["blocks"]
    
    text_blocks = []
    
    for block in blocks:
        if "lines" in block:
            # Combine lines in the block into a single text
            block_text_parts = []
            for line in block["lines"]:
                for span in line["spans"]:
                    block_text_parts.append(span["text"])
            
            text_block = {
                "text": " ".join(block_text_parts),
                "bbox": block["bbox"],
                "type": "text"
            }
            text_blocks.append(text_block)
    
    return text_blocks