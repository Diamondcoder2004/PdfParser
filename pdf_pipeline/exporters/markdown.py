"""Markdown export module"""

from typing import Dict, Any


def export_to_markdown(document: Dict[str, Any], output_path: str):
    """
    Export the processed document to Markdown format
    
    Args:
        document: Processed document dictionary
        output_path: Path to save the Markdown file
    """
    md_content = []
    
    # Add title
    title = document.get("metadata", {}).get("title", "Processed PDF Document")
    md_content.append(f"# {title}\n")
    
    # Process each element in the document structure
    for element in document["structure"]:
        elem_type = element["type"]
        
        if elem_type == "text":
            content = element.get("content", "")
            if content.strip():
                md_content.append(f"{content}\n")
        
        elif elem_type == "table":
            # Add table to markdown
            table_data = element
            table_md = convert_table_to_markdown(table_data)
            md_content.append(table_md + "\n")
        
        elif elem_type == "image_caption":
            caption = element.get("content", "")
            if caption.strip():
                md_content.append(f"> {caption}\n")
    
    # Join all content
    final_content = "\n".join(md_content)
    
    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_content)


def convert_table_to_markdown(table_data: Dict[str, Any]) -> str:
    """
    Convert table data to Markdown format
    
    Args:
        table_data: Table data dictionary
        
    Returns:
        Markdown formatted table string
    """
    rows_data = table_data.get("rows", [])
    cols_data = table_data.get("columns", [])
    
    if not rows_data and not cols_data:
        return ""
    
    # Prepare header
    headers = cols_data if cols_data else (rows_data[0] if rows_data else [])
    if not headers and rows_data:
        # If no explicit headers, make placeholders
        headers = [f"Column {i+1}" for i in range(len(rows_data[0]) if rows_data else 0)]
    
    # Prepare data rows
    data_rows = rows_data
    if cols_data and rows_data and len(cols_data) == len(rows_data[0]):
        # If headers are separate from data, skip first row in data
        pass
    elif cols_data and rows_data and len(cols_data) != len(rows_data[0]):
        # Headers are separate, keep all data rows
        pass
    elif not cols_data and rows_data:
        # Headers are first row of data, so remove from data
        if rows_data:
            headers = rows_data[0]
            data_rows = rows_data[1:]
    
    # Create markdown table
    md_table = []
    
    # Add header row
    header_row = "| " + " | ".join(str(h) for h in headers) + " |"
    md_table.append(header_row)
    
    # Add separator row
    separator = "| " + " | ".join("---" for _ in headers) + " |"
    md_table.append(separator)
    
    # Add data rows
    for row in data_rows:
        row_str = "| " + " | ".join(str(cell) for cell in row) + " |"
        md_table.append(row_str)
    
    return "\n".join(md_table)