"""Heuristic utilities for PDF analysis"""

from typing import List, Dict, Any


def is_table_header(text: str) -> bool:
    """
    Heuristic to determine if text is likely a table header
    
    Args:
        text: Text to evaluate
        
    Returns:
        True if text appears to be a header
    """
    text = text.strip()
    if not text:
        return False
    
    # Check for common header indicators
    header_indicators = [
        "table", "fig", "figure", "chart", "list", "summary",
        "overview", "outline", "classification", "categorization"
    ]
    
    text_lower = text.lower()
    
    # Check if text contains header indicators
    if any(indicator in text_lower for indicator in header_indicators):
        return True
    
    # Check if text is short and contains separators (suggesting multiple columns)
    if len(text) < 50 and ("|" in text or "," in text or "\t" in text):
        return True
    
    # Check if text is all caps (common for headers)
    if text.isupper() and len(text) > 3:
        return True
    
    # Check if text looks like column names (no punctuation, multiple words)
    words = text.split()
    if len(words) > 1 and len(words) < 8:
        word_chars = sum(1 for w in words if w.isalpha())
        if word_chars == len(words):  # All words are alphabetic
            return True
    
    return False


def is_sentence_like(text: str) -> bool:
    """
    Heuristic to determine if text looks like a sentence
    
    Args:
        text: Text to evaluate
        
    Returns:
        True if text appears to be sentence-like
    """
    text = text.strip()
    if not text:
        return False
    
    # Check length
    if len(text) < 5:
        return False
    
    # Check if it starts with capital letter
    starts_with_cap = text[0].isupper() if text else False
    
    # Check if it ends with sentence punctuation
    ends_with_punct = text.endswith(('.', '!', '?'))
    
    # Count words (more than 2 suggests sentence)
    word_count = len(text.split())
    
    # Check for balanced quotes and parentheses
    quote_count = text.count('"') + text.count("'")
    paren_count = text.count('(') + text.count(')')
    
    return (starts_with_cap and 
            (ends_with_punct or word_count > 3) and 
            quote_count % 2 == 0 and 
            paren_count % 2 == 0)


def is_list_item(text: str) -> bool:
    """
    Heuristic to determine if text is a list item
    
    Args:
        text: Text to evaluate
        
    Returns:
        True if text appears to be a list item
    """
    text = text.strip()
    if not text:
        return False
    
    # Check for common list prefixes
    list_prefixes = [
        r'^\d+[.)]',  # Numbers with period or parenthesis
        r'^[a-zA-Z][.)]',  # Letters with period or parenthesis
        r'^•', r'^-', r'^*',  # Bullet points
        r'^○', r'^■', r'^●',  # Other bullet styles
    ]
    
    import re
    for prefix in list_prefixes:
        if re.match(prefix, text):
            return True
    
    return False


def estimate_reading_time(text: str) -> float:
    """
    Estimate reading time for text in minutes
    
    Args:
        text: Text to analyze
        
    Returns:
        Estimated reading time in minutes
    """
    if not text:
        return 0.0
    
    word_count = len(text.split())
    # Average reading speed is ~200 words per minute
    reading_time = word_count / 200.0
    
    return reading_time


def is_significant_content(text: str, min_word_count: int = 5) -> bool:
    """
    Determine if text contains significant content worth preserving
    
    Args:
        text: Text to evaluate
        min_word_count: Minimum number of words to consider significant
        
    Returns:
        True if text has significant content
    """
    if not text or len(text.strip()) == 0:
        return False
    
    # Remove extra whitespace and count words
    words = [w for w in text.split() if w.strip()]
    
    # Filter out purely numeric or special character words
    content_words = []
    for word in words:
        # Consider word as content if it has at least one alphabetic character
        if any(c.isalpha() for c in word):
            content_words.append(word)
    
    return len(content_words) >= min_word_count


def calculate_text_complexity(text: str) -> Dict[str, float]:
    """
    Calculate various metrics for text complexity
    
    Args:
        text: Text to analyze
        
    Returns:
        Dictionary with complexity metrics
    """
    if not text:
        return {
            "word_count": 0,
            "sentence_count": 0,
            "avg_word_length": 0,
            "complexity_score": 0
        }
    
    words = text.split()
    word_count = len(words)
    
    # Calculate average word length
    avg_word_length = sum(len(word) for word in words) / word_count if word_count > 0 else 0
    
    # Count sentences (very basic estimation)
    sentence_endings = text.count('.') + text.count('!') + text.count('?')
    sentence_count = max(1, sentence_endings)
    
    # Calculate complexity score (simple heuristic)
    # Longer words and more sentences generally indicate higher complexity
    complexity_score = (avg_word_length * 0.1) + (sentence_count * 0.01)
    
    return {
        "word_count": word_count,
        "sentence_count": sentence_count,
        "avg_word_length": avg_word_length,
        "complexity_score": complexity_score
    }