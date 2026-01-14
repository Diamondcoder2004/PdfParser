"""Geometry utilities for PDF processing"""

from typing import Tuple, List


def bbox_overlap(bbox1: Tuple[float, float, float, float], 
                bbox2: Tuple[float, float, float, float]) -> float:
    """
    Calculate overlap ratio between two bounding boxes
    
    Args:
        bbox1, bbox2: Bounding boxes as (x0, y0, x1, y1)
        
    Returns:
        Overlap ratio (0.0 to 1.0)
    """
    x0_1, y0_1, x1_1, y1_1 = bbox1
    x0_2, y0_2, x1_2, y1_2 = bbox2
    
    # Calculate intersection
    inter_x0 = max(x0_1, x0_2)
    inter_y0 = max(y0_1, y0_2)
    inter_x1 = min(x1_1, x1_2)
    inter_y1 = min(y1_1, y1_2)
    
    if inter_x0 >= inter_x1 or inter_y0 >= inter_y1:
        return 0.0  # No overlap
    
    inter_area = (inter_x1 - inter_x0) * (inter_y1 - inter_y0)
    area1 = (x1_1 - x0_1) * (y1_1 - y0_1)
    area2 = (x1_2 - x0_2) * (y1_2 - y0_2)
    
    union_area = area1 + area2 - inter_area
    return inter_area / union_area if union_area > 0 else 0.0


def bbox_distance(bbox1: Tuple[float, float, float, float], 
                 bbox2: Tuple[float, float, float, float]) -> float:
    """
    Calculate distance between two bounding boxes
    
    Args:
        bbox1, bbox2: Bounding boxes as (x0, y0, x1, y1)
        
    Returns:
        Distance between boxes (0 if overlapping)
    """
    x0_1, y0_1, x1_1, y1_1 = bbox1
    x0_2, y0_2, x1_2, y1_2 = bbox2
    
    # Calculate horizontal and vertical distances
    x_dist = max(0, max(x0_1, x0_2) - min(x1_1, x1_2))
    y_dist = max(0, max(y0_1, y0_2) - min(y1_1, y1_2))
    
    # Euclidean distance
    return (x_dist**2 + y_dist**2)**0.5


def is_aligned_horizontally(bbox1: Tuple[float, float, float, float], 
                          bbox2: Tuple[float, float, float, float], 
                          tolerance: float = 5.0) -> bool:
    """
    Check if two bounding boxes are horizontally aligned
    
    Args:
        bbox1, bbox2: Bounding boxes as (x0, y0, x1, y1)
        tolerance: Vertical alignment tolerance
        
    Returns:
        True if boxes are horizontally aligned
    """
    _, y0_1, _, y1_1 = bbox1
    _, y0_2, _, y1_2 = bbox2
    
    center1 = (y0_1 + y1_1) / 2
    center2 = (y0_2 + y1_2) / 2
    
    return abs(center1 - center2) <= tolerance


def is_aligned_vertically(bbox1: Tuple[float, float, float, float], 
                        bbox2: Tuple[float, float, float, float], 
                        tolerance: float = 5.0) -> bool:
    """
    Check if two bounding boxes are vertically aligned
    
    Args:
        bbox1, bbox2: Bounding boxes as (x0, y0, x1, y1)
        tolerance: Horizontal alignment tolerance
        
    Returns:
        True if boxes are vertically aligned
    """
    x0_1, _, x1_1, _ = bbox1
    x0_2, _, x1_2, _ = bbox2
    
    center1 = (x0_1 + x1_1) / 2
    center2 = (x0_2 + x1_2) / 2
    
    return abs(center1 - center2) <= tolerance


def get_column_positions(bboxes: List[Tuple[float, float, float, float]], 
                       tolerance: float = 10.0) -> List[float]:
    """
    Identify column positions based on x-coordinates of bounding boxes
    
    Args:
        bboxes: List of bounding boxes as (x0, y0, x1, y1)
        tolerance: Tolerance for grouping similar x-coordinates
        
    Returns:
        List of x-coordinates representing column positions
    """
    if not bboxes:
        return []
    
    # Get left x-coordinates
    x_coords = [bbox[0] for bbox in bboxes]
    x_coords.sort()
    
    # Group similar coordinates
    columns = []
    for coord in x_coords:
        # Check if coordinate is close to existing column
        found = False
        for col in columns:
            if abs(coord - col) <= tolerance:
                found = True
                break
        
        if not found:
            columns.append(coord)
    
    return sorted(columns)