"""Image extraction module"""

import fitz
from pathlib import Path
from typing import List, Dict, Any


def extract_images(page: fitz.Page) -> List[Dict[str, Any]]:
    """
    Extract images from a PDF page
    
    Args:
        page: fitz.Page object
        
    Returns:
        List of dictionaries containing image information
    """
    image_list = page.get_images()
    images = []
    
    for img_index, img in enumerate(image_list):
        # Get image details
        xref = img[0]  # Image XREF
        
        # Get image information
        pix = fitz.Pixmap(page.parent, xref)
        
        # Convert to bytes if needed
        if pix.n < 5:  # Grayscale or RGB
            img_data = pix.tobytes()
        else:  # CMYK: convert to RGB first
            img_data = fitz.Pixmap(fitz.csRGB, pix).tobytes()
        
        image_info = {
            "index": img_index,
            "xref": xref,
            "width": pix.width,
            "height": pix.height,
            "bbox": get_image_bbox(page, xref),  # Position on page
            "colorspace": pix.colorspace.name if pix.colorspace else None,
            "image_data": img_data,
            "extension": get_image_extension(pix)
        }
        
        pix = None  # Free memory
        images.append(image_info)
    
    return images


def get_image_bbox(page: fitz.Page, xref: int) -> tuple:
    """
    Get the bounding box of an image on the page
    
    Args:
        page: fitz.Page object
        xref: Image XREF
        
    Returns:
        Bounding box as (x0, y0, x1, y1)
    """
    # Find the image location on the page
    # This is a simplified approach - in practice, getting exact image bbox
    # requires analyzing page resources and content streams
    img_rects = page.get_image_rects(xref)
    
    if img_rects:
        # Return the first rectangle found
        return img_rects[0].round()
    else:
        # If no specific bbox found, return a default
        return (0, 0, 0, 0)


def get_image_extension(pixmap: fitz.Pixmap) -> str:
    """
    Determine the appropriate extension for an image based on its properties
    
    Args:
        pixmap: fitz.Pixmap object
        
    Returns:
        File extension string
    """
    if pixmap.n == 1:  # Grayscale
        return "png"
    elif pixmap.n == 4:  # CMYK would have been converted to RGB
        return "jpg"
    else:  # RGB or other
        return "png"


def save_image_data(image_data: bytes, output_path: str):
    """
    Save image data to a file
    
    Args:
        image_data: Raw image bytes
        output_path: Path to save the image
    """
    with open(output_path, "wb") as f:
        f.write(image_data)