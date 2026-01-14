"""OCR client for processing scanned documents"""

import fitz
import cv2
import numpy as np
from PIL import Image
import io
from typing import List, Dict, Any


def ocr_page(page: fitz.Page) -> str:
    """
    Apply OCR to a PDF page using PaddleOCR or Tesseract
    
    Args:
        page: fitz.Page object
        
    Returns:
        Extracted text from OCR
    """
    try:
        # Import OCR library (preferably PaddleOCR, fallback to pytesseract)
        try:
            from paddleocr import PaddleOCR
            ocr = PaddleOCR(use_angle_cls=True, lang='en')  # Can be configured for different languages
            text = ocr_page_with_paddle(page, ocr)
        except ImportError:
            try:
                import pytesseract
                text = ocr_page_with_tesseract(page, pytesseract)
            except ImportError:
                # If neither OCR engine is available, return empty string
                print("Warning: No OCR engine available (install paddleocr or pytesseract)")
                return ""
        
        return text
    
    except Exception as e:
        print(f"Error during OCR: {str(e)}")
        return ""


def ocr_page_with_paddle(page: fitz.Page, ocr) -> str:
    """
    Apply OCR using PaddleOCR
    
    Args:
        page: fitz.Page object
        ocr: PaddleOCR instance
        
    Returns:
        Extracted text
    """
    # Render page to image
    mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better OCR quality
    pix = page.get_pixmap(matrix=mat)
    
    # Convert to OpenCV format
    img_data = pix.tobytes("png")
    img_array = np.frombuffer(img_data, dtype=np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    
    # Apply OCR
    result = ocr.ocr(img, cls=True)
    
    # Extract text from results
    texts = []
    for res in result:
        for line in res:
            if line:
                text = line[1][0]  # Extract the text part
                texts.append(text)
    
    return "\n".join(texts)


def ocr_page_with_tesseract(page: fitz.Page, pytesseract) -> str:
    """
    Apply OCR using Tesseract
    
    Args:
        page: fitz.Page object
        pytesseract: pytesseract module
        
    Returns:
        Extracted text
    """
    # Render page to image
    mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better OCR quality
    pix = page.get_pixmap(matrix=mat)
    
    # Convert to PIL Image
    img_data = pix.tobytes("png")
    pil_img = Image.open(io.BytesIO(img_data))
    
    # Apply OCR
    text = pytesseract.image_to_string(pil_img)
    
    return text


def preprocess_image_for_ocr(image_array: np.ndarray) -> np.ndarray:
    """
    Preprocess image to improve OCR accuracy
    
    Args:
        image_array: Input image array
        
    Returns:
        Preprocessed image array
    """
    # Convert to grayscale if needed
    if len(image_array.shape) == 3:
        gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)
    else:
        gray = image_array
    
    # Apply threshold to get white text on black background
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Apply morphological operations to clean up
    kernel = np.ones((1, 1), np.uint8)
    processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    
    return processed