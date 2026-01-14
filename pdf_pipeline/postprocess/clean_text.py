"""Text cleaning utilities"""

import re
from typing import List, Dict, Any


def clean_text(text: str) -> str:
    """
    Clean extracted text from PDF
    
    Args:
        text: Raw extracted text
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace and normalize line breaks
    text = re.sub(r'\s+', ' ', text)  # Replace multiple whitespaces with single space
    text = re.sub(r'\n\s*\n', '\n', text)  # Remove extra blank lines
    
    # Remove special characters that are clearly artifacts
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)  # Remove control characters
    
    # Fix common OCR errors
    text = fix_common_ocr_errors(text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    return text


def fix_common_ocr_errors(text: str) -> str:
    """
    Fix common OCR errors in text
    
    Args:
        text: Text with potential OCR errors
        
    Returns:
        Text with common OCR errors fixed
    """
    # Common replacements
    replacements = {
        r'\bs\b(?=\d)': 'S',  # 's' before numbers often should be 'S'
        r'\bo\b(?=\d)': 'O',  # 'o' before numbers often should be 'O'
        r'(\d)\s*[I,l,|]\s*(?=\d)': r'\11',  # I/l/| between numbers often should be '1'
        r'(\d)\s*[O,0]\s*(?=\d)': r'\10',  # O/0 between numbers often should be '0'
    }
    
    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text)
    
    return text


def is_text_meaningful(text: str, min_length: int = 20) -> bool:
    """
    Check if text is meaningful (not just garbage characters)
    
    Args:
        text: Text to check
        min_length: Minimum length to consider meaningful
        
    Returns:
        True if text is meaningful
    """
    if not text or len(text.strip()) < min_length:
        return False
    
    # Count alphanumeric characters vs special characters
    alnum_count = sum(1 for c in text if c.isalnum())
    total_count = len(text.replace(' ', ''))  # Don't count spaces
    
    if total_count == 0:
        return False
    
    # If less than 50% of non-space characters are alphanumeric, likely garbage
    if alnum_count / total_count < 0.5:
        return False
    
    return True


def segment_text_by_paragraphs(text: str) -> List[str]:
    """
    Segment text into paragraphs
    
    Args:
        text: Input text
        
    Returns:
        List of paragraph strings
    """
    # Split by double newlines first
    paragraphs = text.split('\n\n')
    
    # Further split by single newlines if needed (for PDF-specific line breaks)
    refined_paragraphs = []
    for para in paragraphs:
        if len(para.strip()) > 100:  # If paragraph is long, check for sentence breaks
            # Try to split on sentence endings followed by newlines
            sub_paras = re.split(r'([.!?])\s*\n', para)
            for sub_para in sub_paras:
                sub_para = sub_para.strip()
                if sub_para:
                    refined_paragraphs.append(sub_para)
        else:
            para = para.strip()
            if para:
                refined_paragraphs.append(para)
    
    return [p for p in refined_paragraphs if p]


def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace in text
    
    Args:
        text: Input text
        
    Returns:
        Text with normalized whitespace
    """
    # Replace various whitespace characters with regular spaces
    text = re.sub(r'[\t\r\f\v]+', ' ', text)
    # Replace multiple spaces with single space
    text = re.sub(r' +', ' ', text)
    # Normalize line breaks
    text = re.sub(r'\n+', '\n', text)
    
    return text.strip()