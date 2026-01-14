#!/usr/bin/env python3
"""
Example usage of the PDF processing pipeline
"""

import os
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from pdf_pipeline.main import process_multiple_pdfs
from pdf_pipeline.config import config


def setup_example():
    """Set up example configuration and directories"""
    # Create input and output directories
    input_dir = project_root / "input_pdfs"
    output_dir = project_root / "output_docs"
    
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Created input directory: {input_dir}")
    print(f"Created output directory: {output_dir}")
    
    return input_dir, output_dir


def main():
    """Run example processing"""
    print("Setting up example directories...")
    input_dir, output_dir = setup_example()
    
    # Look for PDF files in the input directory
    pdf_files = list(input_dir.glob("*.pdf"))
    
    if not pdf_files:
        print(f"No PDF files found in {input_dir}")
        print("Please place PDF files in the input directory to process them.")
        return
    
    print(f"Found {len(pdf_files)} PDF files to process")
    
    # Update configuration
    config.output_dir = str(output_dir)
    config.export_format = "docx"  # Change to "markdown" or "json" as needed
    
    # Process the PDFs
    process_multiple_pdfs([str(pdf) for pdf in pdf_files], str(output_dir))
    
    print(f"\nProcessing complete! Check {output_dir} for output files.")


if __name__ == "__main__":
    main()