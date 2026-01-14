"""Table merging logic for combining tables across pages"""

from typing import List, Tuple
from ..pdf.table_extractor import TableBlock


def merge_tables_if_compatible(table1: TableBlock, table2: TableBlock) -> TableBlock:
    """
    Merge two tables if they appear to be continuations of each other
    
    Args:
        table1, table2: TableBlocks to merge
        
    Returns:
        Merged TableBlock
    """
    # Determine which table comes first based on page number
    if table1.page_start <= table2.page_start:
        first_table, second_table = table1, table2
    else:
        first_table, second_table = table2, table1
    
    # Merge the rows
    merged_rows = first_table.rows + second_table.rows
    
    # Determine the page range
    merged_page_start = min(first_table.page_start, second_table.page_start)
    merged_page_end = max(first_table.page_end, second_table.page_end)
    
    # Use the columns from the first table (assuming they're the same)
    merged_columns = first_table.columns if first_table.columns else second_table.columns
    
    # Determine bounding box
    merged_bbox = (
        min(first_table.bbox[0], second_table.bbox[0]),  # x0
        min(first_table.bbox[1], second_table.bbox[1]),  # y0
        max(first_table.bbox[2], second_table.bbox[2]),  # x1
        max(first_table.bbox[3], second_table.bbox[3])   # y1
    )
    
    # Use x_coordinates from the first table if available, otherwise second
    merged_x_coords = first_table.x_coordinates if first_table.x_coordinates else second_table.x_coordinates
    
    # Create merged table
    merged_table = TableBlock(
        page_start=merged_page_start,
        page_end=merged_page_end,
        columns=merged_columns,
        rows=merged_rows,
        bbox=merged_bbox,
        x_coordinates=merged_x_coords
    )
    
    return merged_table


def is_table_continuation(table1: TableBlock, table2: TableBlock, 
                         max_page_gap: int = 1, column_tolerance: float = 10.0) -> bool:
    """
    Check if table2 is a continuation of table1
    
    Args:
        table1, table2: TableBlocks to compare
        max_page_gap: Maximum allowed gap in pages between tables
        column_tolerance: Tolerance for column alignment matching
        
    Returns:
        True if table2 is a continuation of table1
    """
    # Check page sequence
    page_gap = abs(table2.page_start - table1.page_end)
    if page_gap > max_page_gap:
        return False
    
    # Check column count compatibility
    if len(table1.columns) != len(table2.columns):
        # Handle case where one table might not have headers
        if len(table1.rows) > 0 and len(table1.rows[0]) == len(table2.columns):
            # First row of table1 matches column count of table2
            pass
        elif len(table2.rows) > 0 and len(table2.rows[0]) == len(table1.columns):
            # First row of table2 matches column count of table1
            pass
        else:
            return False
    
    # Check column alignment (x-coordinates)
    if table1.x_coordinates and table2.x_coordinates:
        if len(table1.x_coordinates) != len(table2.x_coordinates):
            return False
        
        # Check if x-coordinates align within tolerance
        for x1, x2 in zip(table1.x_coordinates, table2.x_coordinates):
            if abs(x1 - x2) > column_tolerance:
                return False
    
    # Check if headers are similar (if both have headers)
    if table1.columns and table2.columns:
        header_similarity = compare_headers(table1.columns, table2.columns)
        if header_similarity < 0.7:  # Require 70% similarity
            return False
    
    return True


def compare_headers(headers1: List[str], headers2: List[str]) -> float:
    """
    Compare two sets of headers and return similarity ratio
    
    Args:
        headers1, headers2: Lists of header strings
        
    Returns:
        Similarity ratio (0.0 to 1.0)
    """
    if len(headers1) != len(headers2):
        return 0.0
    
    matches = 0
    for h1, h2 in zip(headers1, headers2):
        # Simple comparison, ignoring case and extra whitespace
        if h1.strip().lower() == h2.strip().lower():
            matches += 1
        # Could add more sophisticated comparison here (substring matching, etc.)
    
    return matches / len(headers1) if headers1 else 1.0


def normalize_merged_table(table: TableBlock) -> TableBlock:
    """
    Clean up a merged table by removing empty rows/cells and standardizing format
    
    Args:
        table: TableBlock to normalize
        
    Returns:
        Normalized TableBlock
    """
    # Clean up rows by stripping whitespace
    cleaned_rows = []
    for row in table.rows:
        cleaned_row = [cell.strip() if isinstance(cell, str) else str(cell) for cell in row]
        cleaned_rows.append(cleaned_row)
    
    # Remove completely empty rows
    filtered_rows = []
    for row in cleaned_rows:
        if any(cell for cell in row if cell):  # Keep rows with at least one non-empty cell
            filtered_rows.append(row)
    
    # Create normalized table
    normalized_table = TableBlock(
        page_start=table.page_start,
        page_end=table.page_end,
        columns=[col.strip() if isinstance(col, str) else str(col) for col in table.columns],
        rows=filtered_rows,
        bbox=table.bbox,
        x_coordinates=table.x_coordinates
    )
    
    return normalized_table