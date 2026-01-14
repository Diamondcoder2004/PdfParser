"""Configuration for PDF processing pipeline"""

import os
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ProcessingConfig:
    """Configuration for PDF processing"""
    # Input/output paths
    input_dir: str = "./input"
    output_dir: str = "./output"
    
    # Processing settings
    max_pages_per_doc: Optional[int] = None
    enable_ocr: bool = True
    enable_vl_caption: bool = False
    
    # Table detection settings
    min_table_rows: int = 3
    min_column_alignment_threshold: float = 0.8
    
    # Text cleaning settings
    min_text_length: int = 10
    remove_extra_whitespace: bool = True
    
    # Export settings
    export_format: str = "docx"  # "docx", "markdown", "json"
    include_tables: bool = True
    include_images: bool = True

# Global config instance
config = ProcessingConfig()