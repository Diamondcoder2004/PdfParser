"""Main entry point for PDF processing pipeline"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config import config
from pdf.loader import load_pdf
from pdf.page_classifier import classify_page
from pdf.table_extractor import extract_tables
from pdf.text_extractor import extract_text
from pdf.image_extractor import extract_images
from vision.ocr_client import ocr_page
from vision.vl_caption import caption_images
from tables.table_buffer import TableBuffer
from postprocess.assemble_doc import assemble_document
from postprocess.clean_text import clean_text
from exporters.docx import export_to_docx
from exporters.markdown import export_to_markdown


@dataclass
class PageProfile:
    """Profile of a PDF page containing information about its content"""
    page_num: int
    has_text: bool
    has_table: bool
    has_images: bool
    is_scan: bool
    text_density: float
    image_count: int


def process_single_pdf(pdf_path: str) -> Dict[str, Any]:
    """
    Process a single PDF file according to the pipeline
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Dictionary containing processed content
    """
    print(f"Processing PDF: {pdf_path}")
    
    # Load PDF document
    doc = load_pdf(pdf_path)
    
    # Initialize components
    table_buffer = TableBuffer()
    doc_blocks = []
    
    # Process each page
    for page_idx in range(len(doc)):
        page = doc[page_idx]
        
        # Get page profile
        profile = classify_page(page, page_idx)
        print(f"Page {page_idx + 1} profile: {profile}")
        
        # Extract content based on profile
        if profile.has_table:
            print(f"  - Found table on page {page_idx + 1}, extracting...")
            tables = extract_tables(page)
            for table in tables:
                table_buffer.add(table, page_idx)
        
        if profile.has_text and not profile.has_table:
            print(f"  - Found text on page {page_idx + 1}, extracting...")
            text = extract_text(page)
            if text.strip():
                doc_blocks.append({"type": "text", "content": clean_text(text)})
        
        elif profile.is_scan:
            print(f"  - Page {page_idx + 1} appears to be a scan, applying OCR...")
            text = ocr_page(page)
            if text.strip():
                doc_blocks.append({"type": "text", "content": clean_text(text)})
        
        elif profile.has_images and not profile.has_text and not profile.has_table:
            print(f"  - Found images on page {page_idx + 1}, generating captions...")
            captions = caption_images(page)
            for caption in captions:
                doc_blocks.append({"type": "image_caption", "content": caption})
    
    # Merge tables that span multiple pages
    print("Merging tables across pages...")
    merged_tables = table_buffer.merge()
    
    # Add merged tables to document blocks
    for table in merged_tables:
        doc_blocks.append({
            "type": "table", 
            "columns": table.columns, 
            "rows": table.rows,
            "pages": table.page_range
        })
    
    # Sort blocks by original page order
    doc_blocks.sort(key=lambda x: x.get('page_num', 0))
    
    # Assemble final document
    print("Assembling final document...")
    final_doc = assemble_document(doc_blocks)
    
    return final_doc


def process_multiple_pdfs(pdf_paths: List[str], output_dir: str = None):
    """
    Process multiple PDF files
    
    Args:
        pdf_paths: List of paths to PDF files
        output_dir: Output directory for results
    """
    if output_dir is None:
        output_dir = config.output_dir
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    for pdf_path in pdf_paths:
        try:
            # Process the PDF
            result = process_single_pdf(pdf_path)
            
            # Generate output filename
            base_name = Path(pdf_path).stem
            
            # Export based on configured format
            if config.export_format == "docx":
                output_path = os.path.join(output_dir, f"{base_name}.docx")
                export_to_docx(result, output_path)
            elif config.export_format == "markdown":
                output_path = os.path.join(output_dir, f"{base_name}.md")
                export_to_markdown(result, output_path)
            else:  # json
                import json
                output_path = os.path.join(output_dir, f"{base_name}.json")
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
            
            print(f"Saved result to: {output_path}")
            
        except Exception as e:
            print(f"Error processing {pdf_path}: {str(e)}")
            continue


def main():
    """Main function to run the pipeline"""
    import argparse
    
    parser = argparse.ArgumentParser(description="PDF Processing Pipeline")
    parser.add_argument("--input", "-i", type=str, required=True, 
                       help="Input PDF file or directory")
    parser.add_argument("--output", "-o", type=str, default=config.output_dir,
                       help="Output directory")
    parser.add_argument("--format", choices=["docx", "markdown", "json"], 
                       default=config.export_format,
                       help="Output format")
    
    args = parser.parse_args()
    
    # Update config with arguments
    config.output_dir = args.output
    config.export_format = args.format
    
    # Determine input files
    input_path = Path(args.input)
    if input_path.is_file():
        pdf_files = [str(input_path)]
    elif input_path.is_dir():
        pdf_files = [str(f) for f in input_path.glob("*.pdf")]
    else:
        raise ValueError(f"Input path does not exist: {input_path}")
    
    if not pdf_files:
        print("No PDF files found!")
        return
    
    print(f"Found {len(pdf_files)} PDF files to process")
    
    # Process all PDFs
    process_multiple_pdfs(pdf_files, args.output)


if __name__ == "__main__":
    main()