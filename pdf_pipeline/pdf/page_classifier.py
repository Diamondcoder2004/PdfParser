"""Page classification module - determines content type of each page"""

import fitz
import pdfplumber
from pathlib import Path
from typing import Tuple
from dataclasses import dataclass
import math


@dataclass
class PageProfile:
    """Profile of a PDF page containing information about its content"""
    page_num: int
    has_text: bool
    has_table: bool
    has_images: bool
    is_scan: bool
    text_density: float = 0.0
    image_count: int = 0
    char_count: int = 0
    
    def __repr__(self):
        return (f"PageProfile(page={self.page_num}, has_text={self.has_text}, "
                f"has_table={self.has_table}, has_images={self.has_images}, "
                f"is_scan={self.is_scan}, text_density={self.text_density:.2f})")


def classify_page(page: fitz.Page, page_num: int = 0) -> PageProfile:
    """
    Classify the content type of a PDF page
    
    Args:
        page: fitz.Page object
        page_num: Page number (0-indexed)
        
    Returns:
        PageProfile object with classification results
    """
    # Get basic page info
    page_width = page.rect.width
    page_height = page.rect.height
    page_area = page_width * page_height
    
    # Extract text content
    text = page.get_text("text")
    char_count = len(text.strip())
    
    # Calculate text density
    text_lines = text.split('\n')
    text_density = calculate_text_density(text_lines, page_area)
    
    # Check for images
    image_list = page.get_images()
    image_count = len(image_list)
    
    # Check for vector graphics (lines, rectangles, etc.)
    drawing_paths = page.get_cdrawings()
    
    # Check for table-like structures using pdfplumber approach
    has_table = detect_table_structure(page)
    
    # Determine if page has readable text
    has_text = char_count > 20  # At least 20 characters to consider as having text
    
    # Determine if page is likely a scan
    is_scan = determine_if_scan(char_count, text_density, image_count, drawing_paths, text)
    
    # Determine if page has images
    has_images = image_count > 0
    
    return PageProfile(
        page_num=page_num,
        has_text=has_text,
        has_table=has_table,
        has_images=has_images,
        is_scan=is_scan,
        text_density=text_density,
        image_count=image_count,
        char_count=char_count
    )


def calculate_text_density(text_lines: list, page_area: float) -> float:
    """
    Calculate text density on the page
    
    Args:
        text_lines: List of text lines
        page_area: Total area of the page
        
    Returns:
        Text density as a ratio
    """
    if page_area <= 0:
        return 0.0
    
    # Count non-empty lines
    non_empty_lines = sum(1 for line in text_lines if line.strip())
    
    # Estimate character area (rough approximation)
    avg_line_length = sum(len(line) for line in text_lines) / max(len(text_lines), 1)
    estimated_char_area = non_empty_lines * avg_line_length * 6 * 12  # approx char width * height
    
    return min(estimated_char_area / page_area, 1.0)


def detect_table_structure(page: fitz.Page) -> bool:
    """
    Detect if the page contains table-like structures
    
    Args:
        page: fitz.Page object
        
    Returns:
        True if table structure detected
    """
    # Extract words with their positions
    words = page.get_text("dict")["blocks"]
    
    # Look for repeated patterns that suggest table headers/columns
    lines = []
    for block in words:
        if "lines" in block:
            for line in block["lines"]:
                spans = line["spans"]
                if len(spans) > 1:  # Multiple text elements in line
                    line_info = {
                        "bbox": line["bbox"],
                        "spans": [(span["bbox"][0], span["text"]) for span in spans]  # x-coordinate and text
                    }
                    lines.append(line_info)
    
    # Analyze line alignment for potential columns
    if len(lines) < 3:  # Need at least a few lines to form a table
        return False
    
    # Look for consistent vertical alignment (similar x-coordinates across lines)
    # which would indicate columnar structure
    column_candidates = {}
    for line in lines:
        for x_pos, text in line["spans"]:
            rounded_x = round(x_pos, -1)  # Round to nearest 10 for grouping
            if rounded_x not in column_candidates:
                column_candidates[rounded_x] = 0
            column_candidates[rounded_x] += 1
    
    # If we have multiple aligned columns appearing frequently, likely a table
    frequent_columns = sum(1 for count in column_candidates.values() if count >= 3)
    
    return frequent_columns >= 2  # At least 2 columns appearing in multiple lines


def determine_if_scan(char_count: int, text_density: float, image_count: int, 
                     drawing_paths: list, raw_text: str) -> bool:
    """
    Determine if a page is likely a scanned image rather than text
    
    Args:
        char_count: Number of characters in extracted text
        text_density: Density of text on page
        image_count: Number of images on page
        drawing_paths: Vector drawing paths
        raw_text: Raw extracted text
        
    Returns:
        True if page appears to be a scan
    """
    # Criteria for determining if it's a scan:
    # 1. Very low character count despite page size
    # 2. Low text density
    # 3. High image count relative to text
    # 4. Contains mostly unstructured text (OCR artifacts)
    
    if char_count < 10:
        return True
    
    if text_density < 0.05 and image_count > 0:  # Less than 5% text density but has images
        return True
    
    # Check for OCR-like artifacts in text (lots of special characters, no spaces)
    special_chars_ratio = sum(1 for c in raw_text if not c.isalnum() and c != ' ') / max(len(raw_text), 1)
    
    if text_density < 0.1 and special_chars_ratio > 0.3:  # Low density + lots of special chars = likely OCR
        return True
    
    return False