# PDF Processing Pipeline

This is a comprehensive PDF processing pipeline designed to extract high-quality text and tables from complex PDF documents for use in knowledge bases. The pipeline intelligently handles different content types including text, tables, and images/scans.

## Architecture Overview

The pipeline follows a modular architecture:

```
pdf_pipeline/
├── main.py                     # Entry point
├── config.py                   # Configuration settings
├── pdf/                        # PDF processing modules
│   ├── loader.py               # PDF loading
│   ├── page_classifier.py      # Content type detection
│   ├── text_extractor.py       # Text extraction
│   ├── table_extractor.py      # Table detection/extraction
│   └── image_extractor.py      # Image extraction
├── tables/                     # Table processing
│   ├── table_buffer.py         # Table collection
│   └── table_merge.py          # Cross-page table merging
├── vision/                     # Vision processing
│   ├── ocr_client.py           # OCR processing
│   └── vl_caption.py           # Image captioning
├── postprocess/                # Post-processing
│   ├── clean_text.py           # Text cleaning
│   └── assemble_doc.py         # Document assembly
├── exporters/                  # Export formats
│   ├── docx.py                 # DOCX export
│   └── markdown.py             # Markdown export
└── utils/                      # Utility functions
    ├── geometry.py             # Geometric calculations
    └── heuristics.py           # Heuristic functions
```

## Features

- **Intelligent Content Classification**: Each page is analyzed to determine if it contains text, tables, or images/scans
- **Multi-method Extraction**: Uses the best extraction method for each content type
- **Cross-page Table Merging**: Tables spanning multiple pages are automatically merged
- **OCR for Scanned Documents**: Applies OCR only where needed
- **Flexible Export**: Supports DOCX, Markdown, and JSON formats

## How It Works

1. **Page Classification**: Each page is classified as containing text, tables, or images/scans
2. **Content Extraction**: Appropriate extraction method is applied based on classification:
   - Tables: Direct extraction using pdfplumber techniques
   - Text: PyMuPDF text extraction
   - Scans: OCR processing
   - Images: Captioning with VL models
3. **Table Merging**: Tables spanning multiple pages are identified and merged
4. **Assembly**: All content is assembled in document order
5. **Export**: Final document is exported in chosen format

## Installation

```bash
pip install -r requirements.txt
```

For OCR functionality:
```bash
# Install Tesseract OCR (for pytesseract)
# On Ubuntu/Debian: sudo apt-get install tesseract-ocr
# On macOS: brew install tesseract
# On Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
```

## Usage

```bash
python -m pdf_pipeline.main --input /path/to/input.pdf --output /path/to/output --format docx
```

Or process a directory of PDFs:

```bash
python -m pdf_pipeline.main --input /path/to/input_directory --output /path/to/output --format markdown
```

## Configuration

Modify `config.py` to adjust processing parameters:

- `enable_ocr`: Enable/disable OCR processing
- `export_format`: Default export format ('docx', 'markdown', 'json')
- `min_table_rows`: Minimum rows to consider content as a table
- And many more...

## Output Format

The pipeline produces structured output containing:
- Clean, readable text
- Properly formatted tables (merged across pages)
- Image descriptions where appropriate
- Document structure preserved

## Testing

The pipeline was designed specifically to handle complex documents like:
- Technical documentation
- Legal documents
- Financial reports
- Scientific papers
- Government forms

Test with challenging documents to see the full capabilities of the intelligent content classification and multi-method extraction approach.

## Performance Notes

- Tables are prioritized over OCR to preserve structure
- OCR is applied only to pages identified as scans
- Memory usage is optimized for large documents
- Processing speed scales with document complexity