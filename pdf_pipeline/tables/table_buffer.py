"""Table buffer for collecting and merging tables across pages"""

from typing import List, Dict, Any
from dataclasses import dataclass
from .table_merge import merge_tables_if_compatible
from ..pdf.table_extractor import TableBlock


@dataclass
class MergedTable:
    """Represents a table that may span multiple pages"""
    original_tables: List[TableBlock]
    columns: List[str]
    rows: List[List[str]]
    page_range: tuple  # (start_page, end_page)


class TableBuffer:
    """Buffer to collect tables and merge them across pages"""
    
    def __init__(self):
        self.tables: List[TableBlock] = []
        self.merged_tables: List[MergedTable] = []
    
    def add(self, table: TableBlock, page_num: int = None):
        """
        Add a table to the buffer
        
        Args:
            table: TableBlock to add
            page_num: Page number where table was found
        """
        # Update page numbers if provided
        if page_num is not None:
            table.page_start = page_num
            table.page_end = page_num
        
        self.tables.append(table)
    
    def merge(self) -> List[MergedTable]:
        """
        Merge compatible tables that span multiple pages
        
        Returns:
            List of merged tables
        """
        if not self.tables:
            return []
        
        # Sort tables by page number to process in order
        sorted_tables = sorted(self.tables, key=lambda t: t.page_start)
        
        merged = []
        i = 0
        
        while i < len(sorted_tables):
            current_table = sorted_tables[i]
            
            # Look for tables that can be merged with the current one
            j = i + 1
            while j < len(sorted_tables):
                next_table = sorted_tables[j]
                
                # Check if tables can be merged
                if self._can_merge_tables(current_table, next_table):
                    # Merge the tables
                    current_table = merge_tables_if_compatible(current_table, next_table)
                    j += 1  # Continue checking for more merges
                else:
                    # Cannot merge, break and process next
                    break
            
            # Add the (potentially merged) table to results
            original_tables = [current_table] if hasattr(current_table, 'original_tables') else [sorted_tables[i]]
            if j > i + 1:  # If we actually merged tables
                # Collect all original tables that were merged
                original_tables = sorted_tables[i:j]
            
            merged_table = MergedTable(
                original_tables=original_tables,
                columns=current_table.columns,
                rows=current_table.rows,
                page_range=(current_table.page_start, current_table.page_end)
            )
            
            merged.append(merged_table)
            
            # Move to the next unprocessed table
            i = j
        
        self.merged_tables = merged
        return merged
    
    def _can_merge_tables(self, table1: TableBlock, table2: TableBlock) -> bool:
        """
        Check if two tables can be merged
        
        Args:
            table1, table2: TableBlocks to check
            
        Returns:
            True if tables can be merged
        """
        # Check if tables are on consecutive pages
        if abs(table2.page_start - table1.page_end) > 1:
            return False
        
        # Check if they have the same number of columns
        if len(table1.columns) != len(table2.columns):
            # Try to handle cases where one table might be missing header row
            if len(table1.rows) > 0 and len(table1.rows[0]) == len(table2.columns):
                pass  # OK, first row of table1 matches columns of table2
            elif len(table2.rows) > 0 and len(table2.rows[0]) == len(table1.columns):
                pass  # OK, first row of table2 matches columns of table1
            else:
                return False
        
        # Check if column alignments are similar (x-coordinates)
        if table1.x_coordinates and table2.x_coordinates:
            if len(table1.x_coordinates) != len(table2.x_coordinates):
                return False
            
            # Check if x-coordinates are roughly aligned
            for x1, x2 in zip(table1.x_coordinates, table2.x_coordinates):
                if abs(x1 - x2) > 10:  # Allow 10 units tolerance
                    return False
        
        # Check if headers are similar
        if table1.columns and table2.columns:
            # Compare headers with some tolerance for minor differences
            header_similarity = self._compare_headers(table1.columns, table2.columns)
            if header_similarity < 0.7:  # Require 70% similarity
                return False
        
        return True
    
    def _compare_headers(self, headers1: List[str], headers2: List[str]) -> float:
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
            # More sophisticated comparison could go here
        
        return matches / len(headers1) if headers1 else 1.0


def normalize_table(table: MergedTable) -> MergedTable:
    """
    Normalize a table by cleaning up rows and handling special cases
    
    Args:
        table: MergedTable to normalize
        
    Returns:
        Normalized MergedTable
    """
    # Remove empty rows
    cleaned_rows = []
    for row in table.rows:
        # A row is considered empty if all cells are empty or whitespace
        if any(cell.strip() for cell in row):
            cleaned_rows.append([cell.strip() for cell in row])
    
    # Update the table with cleaned rows
    normalized_table = MergedTable(
        original_tables=table.original_tables,
        columns=table.columns,
        rows=cleaned_rows,
        page_range=table.page_range
    )
    
    return normalized_table