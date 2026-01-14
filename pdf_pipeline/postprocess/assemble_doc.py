"""Document assembly module - combines text, tables, and other elements into final document"""

from typing import List, Dict, Any
from ..tables.table_buffer import MergedTable


def assemble_document(blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Assemble all extracted content into a final document structure
    
    Args:
        blocks: List of content blocks (text, tables, images, etc.)
        
    Returns:
        Assembled document as dictionary
    """
    # Sort blocks by their original page order if available
    sorted_blocks = sorted(blocks, key=lambda x: x.get('page_num', 0))
    
    # Separate different types of content
    text_blocks = []
    table_blocks = []
    image_blocks = []
    
    for block in sorted_blocks:
        block_type = block.get('type', 'unknown')
        
        if block_type == 'text':
            text_blocks.append(block)
        elif block_type == 'table':
            table_blocks.append(block)
        elif block_type == 'image_caption':
            image_blocks.append(block)
    
    # Create the final document structure
    document = {
        "metadata": {
            "created_at": __import__('datetime').datetime.now().isoformat(),
            "processing_method": "pdf_pipeline"
        },
        "content": {
            "text_elements": text_blocks,
            "tables": table_blocks,
            "images": image_blocks
        },
        "structure": build_document_structure(text_blocks, table_blocks, image_blocks)
    }
    
    return document


def build_document_structure(text_blocks: List[Dict], 
                           table_blocks: List[Dict], 
                           image_blocks: List[Dict]) -> List[Dict[str, Any]]:
    """
    Build a linear structure of the document combining all elements
    
    Args:
        text_blocks: List of text blocks
        table_blocks: List of table blocks
        image_blocks: List of image blocks
        
    Returns:
        Linear structure of document elements
    """
    # Combine all blocks maintaining order
    all_blocks = []
    
    # Add text blocks
    for text_block in text_blocks:
        all_blocks.append({
            "type": "text",
            "content": text_block.get("content", ""),
            "page_num": text_block.get("page_num", -1)
        })
    
    # Add table blocks
    for table_block in table_blocks:
        all_blocks.append({
            "type": "table",
            "columns": table_block.get("columns", []),
            "rows": table_block.get("rows", []),
            "pages": table_block.get("pages", []),
            "page_num": min(table_block.get("pages", [float('inf')]))
        })
    
    # Add image blocks
    for image_block in image_blocks:
        all_blocks.append({
            "type": "image_caption",
            "content": image_block.get("content", ""),
            "page_num": image_block.get("page_num", -1)
        })
    
    # Sort by page number to maintain document flow
    all_blocks.sort(key=lambda x: x["page_num"])
    
    return all_blocks


def extract_knowledge_elements(document: Dict[str, Any]) -> Dict[str, List]:
    """
    Extract knowledge elements from the assembled document
    
    Args:
        document: Assembled document
        
    Returns:
        Dictionary with categorized knowledge elements
    """
    knowledge_elements = {
        "facts": [],
        "procedures": [],
        "requirements": [],
        "definitions": [],
        "tables": [],
        "figures": []
    }
    
    # Extract from text elements
    for text_elem in document["content"]["text_elements"]:
        text = text_elem.get("content", "")
        # Basic categorization based on keywords (could be enhanced with NLP)
        if any(keyword in text.lower() for keyword in ["require", "must", "should", "need"]):
            knowledge_elements["requirements"].append(text)
        elif any(keyword in text.lower() for keyword in ["define", "definition", "means", "term"]):
            knowledge_elements["definitions"].append(text)
        elif any(keyword in text.lower() for keyword in ["procedure", "step", "process", "how to"]):
            knowledge_elements["procedures"].append(text)
        else:
            knowledge_elements["facts"].append(text)
    
    # Add tables
    knowledge_elements["tables"] = document["content"]["tables"]
    
    # Add figures/captions
    knowledge_elements["figures"] = document["content"]["images"]
    
    return knowledge_elements


def validate_document_structure(document: Dict[str, Any]) -> bool:
    """
    Validate that the document structure is complete and consistent
    
    Args:
        document: Document to validate
        
    Returns:
        True if document structure is valid
    """
    required_keys = ["metadata", "content", "structure"]
    content_required_keys = ["text_elements", "tables", "images"]
    
    # Check top-level keys
    for key in required_keys:
        if key not in document:
            print(f"Missing required key: {key}")
            return False
    
    # Check content keys
    content = document["content"]
    for key in content_required_keys:
        if key not in content:
            print(f"Missing required content key: {key}")
            return False
    
    # Additional validation could go here
    return True