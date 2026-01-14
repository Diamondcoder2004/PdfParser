"""Table extraction module using pdfplumber"""

import fitz
import pdfplumber
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class TableBlock:
    """Represents a table extracted from PDF"""
    page_start: int
    page_end: int
    columns: List[str]
    rows: List[List[str]]
    bbox: tuple  # (x0, y0, x1, y1)
    x_coordinates: List[float]  # Column boundaries


def extract_tables(page: fitz.Page) -> List[TableBlock]:
    """
    Extract tables from a PDF page using pdfplumber
    
    Args:
        page: fitz.Page object
        
    Returns:
        List of TableBlock objects
    """
    # Since we can't directly use pdfplumber with fitz.Page, 
    # we'll implement a method to detect and extract table-like structures
    # using PyMuPDF and some heuristics
    
    tables = []
    
    # Get the page as a rectangle
    page_bbox = page.rect
    
    # First, let's try to find table-like structures by analyzing text positioning
    # We'll look for aligned text that suggests columnar data
    
    # Extract words with their positions
    words_data = page.get_text("dict")
    
    # Find potential table areas by looking for aligned text
    potential_tables = find_table_areas(words_data, page_bbox)
    
    for table_data in potential_tables:
        # Create a TableBlock from the detected table area
        table_block = TableBlock(
            page_start=page.number,
            page_end=page.number,
            columns=table_data.get('headers', []),
            rows=table_data['rows'],
            bbox=table_data['bbox'],
            x_coordinates=table_data.get('x_coords', [])
        )
        tables.append(table_block)
    
    return tables


def find_table_areas(words_data: Dict, page_bbox) -> List[Dict[str, Any]]:
    """
    Find potential table areas in the page by analyzing text alignment
    
    Args:
        words_data: Words data from PyMuPDF
        page_bbox: Page bounding box
        
    Returns:
        List of dictionaries representing potential table areas
    """
    potential_tables = []
    
    # Extract text lines with their positions
    lines = []
    for block in words_data.get("blocks", []):
        if "lines" in block:
            for line in block["lines"]:
                # Get text spans in this line
                spans = []
                for span in line.get("spans", []):
                    text = span.get("text", "").strip()
                    if text:
                        spans.append({
                            "text": text,
                            "bbox": span["bbox"],  # (x0, y0, x1, y1)
                            "size": span["size"]
                        })
                
                if spans:  # Only add lines that have text
                    # Sort spans by x-coordinate to get left-to-right order
                    spans.sort(key=lambda s: s["bbox"][0])
                    
                    lines.append({
                        "spans": spans,
                        "bbox": line["bbox"]
                    })
    
    # Group lines that might form tables based on similar column structure
    table_groups = group_lines_into_tables(lines)
    
    for table_group in table_groups:
        if len(table_group) >= 2:  # Need at least 2 rows to form a table
            # Extract headers and rows
            headers = extract_headers_from_group(table_group)
            rows = extract_rows_from_group(table_group, headers)
            
            # Calculate bounding box for the entire table
            min_x = min(min(span["bbox"][0] for span in line["spans"]) for line in table_group)
            max_x = max(max(span["bbox"][2] for span in line["spans"]) for line in table_group)
            min_y = min(line["bbox"][1] for line in table_group)
            max_y = max(line["bbox"][3] for line in table_group)
            
            # Extract x-coordinates of columns
            x_coords = extract_column_coordinates(table_group)
            
            table_data = {
                "headers": headers,
                "rows": rows,
                "bbox": (min_x, min_y, max_x, max_y),
                "x_coords": x_coords
            }
            
            potential_tables.append(table_data)
    
    return potential_tables


def group_lines_into_tables(lines: List[Dict]) -> List[List[Dict]]:
    """
    Group lines that potentially form tables based on alignment
    
    Args:
        lines: List of line data with spans
        
    Returns:
        List of groups of lines that may form tables
    """
    if not lines:
        return []
    
    # Group consecutive lines that have similar span counts and x-alignments
    table_groups = []
    current_group = [lines[0]]
    
    for i in range(1, len(lines)):
        prev_line = current_group[-1]
        curr_line = lines[i]
        
        # Check if current line aligns with previous in terms of column structure
        if lines_align_as_table(prev_line, curr_line):
            current_group.append(curr_line)
        else:
            # If the current group has multiple lines, save it as a potential table
            if len(current_group) > 1:
                table_groups.append(current_group)
            # Start a new group
            current_group = [curr_line]
    
    # Add the last group if it has multiple lines
    if len(current_group) > 1:
        table_groups.append(current_group)
    
    return table_groups


def lines_align_as_table(line1: Dict, line2: Dict, tolerance: float = 5.0) -> bool:
    """
    Check if two lines align in a way that suggests they're part of the same table
    
    Args:
        line1, line2: Line data with spans
        tolerance: Tolerance for alignment checking
        
    Returns:
        True if lines align as table rows
    """
    spans1 = line1["spans"]
    spans2 = line2["spans"]
    
    # Check if both lines have similar number of spans (columns)
    if abs(len(spans1) - len(spans2)) > 1:  # Allow difference of 1
        return False
    
    # Check if corresponding spans have similar x-coordinates
    min_matches = min(len(spans1), len(spans2))
    matches = 0
    
    for i in range(min(len(spans1), len(spans2))):
        x_diff = abs(spans1[i]["bbox"][0] - spans2[i]["bbox"][0])
        if x_diff <= tolerance:
            matches += 1
    
    # At least half of the columns should align
    return matches >= min_matches // 2


def extract_headers_from_group(group: List[Dict]) -> List[str]:
    """
    Extract potential header values from a group of table lines
    
    Args:
        group: Group of lines that form a potential table
        
    Returns:
        List of header strings
    """
    if not group:
        return []
    
    # For now, we'll take the first line as headers
    # In a more sophisticated implementation, we could analyze
    # which line has more distinctive characteristics of headers
    first_line_spans = group[0]["spans"]
    headers = [span["text"] for span in first_line_spans]
    
    return headers


def extract_rows_from_group(group: List[Dict], headers: List[str]) -> List[List[str]]:
    """
    Extract rows from a group of table lines
    
    Args:
        group: Group of lines that form a potential table
        headers: Header values for reference
        
    Returns:
        List of rows (each row is a list of cell values)
    """
    rows = []
    
    # Skip the first line if it was used as headers
    start_idx = 1 if headers else 0
    
    for i in range(start_idx, len(group)):
        line_spans = group[i]["spans"]
        row = [span["text"] for span in line_spans]
        rows.append(row)
    
    return rows


def extract_column_coordinates(group: List[Dict]) -> List[float]:
    """
    Extract x-coordinates that represent column boundaries
    
    Args:
        group: Group of lines that form a potential table
        
    Returns:
        List of x-coordinate values
    """
    if not group:
        return []
    
    # Use the first line to determine column positions
    x_coords = []
    for span in group[0]["spans"]:
        x_coords.append(span["bbox"][0])  # Left x-coordinate of each span
    
    return x_coords