"""
Text processing and manipulation utilities.

BRANCH-8: Utilities
Author: Boris (Claude Code)
"""

import re
from typing import List, Set, Dict, Optional

from ..core.logger import get_logger

logger = get_logger(__name__)


def normalize_text(text: str) -> str:
    """
    Normalize text for processing.

    Args:
        text: Input text

    Returns:
        Normalized text
    """
    # Convert to lowercase
    text = text.lower()
    # Remove leading/trailing whitespace
    text = text.strip()
    # Replace multiple spaces with single space
    text = ' '.join(text.split())
    return text


def clean_html(html: str) -> str:
    """
    Remove HTML tags from text.

    Args:
        html: HTML text

    Returns:
        Cleaned text
    """
    # Remove script and style elements
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
    # Remove HTML tags
    html = re.sub(r'<[^>]+>', '', html)
    # Decode HTML entities
    html = html.replace('&nbsp;', ' ')
    html = html.replace('&lt;', '<')
    html = html.replace('&gt;', '>')
    html = html.replace('&amp;', '&')
    return html


def extract_keywords(
    text: str,
    min_length: int = 3,
    max_keywords: Optional[int] = None
) -> List[str]:
    """
    Extract keywords from text.

    Args:
        text: Input text
        min_length: Minimum keyword length
        max_keywords: Maximum keywords to return

    Returns:
        List of keywords
    """
    # Simple keyword extraction
    words = text.lower().split()
    keywords = list(set([w for w in words if len(w) >= min_length]))

    if max_keywords:
        keywords = keywords[:max_keywords]

    return keywords


def remove_special_chars(
    text: str,
    keep_spaces: bool = True,
    keep_punctuation: bool = False
) -> str:
    """
    Remove special characters from text.

    Args:
        text: Input text
        keep_spaces: Keep spaces
        keep_punctuation: Keep punctuation marks

    Returns:
        Cleaned text
    """
    if keep_punctuation:
        if keep_spaces:
            pattern = r'[^a-zA-Z0-9\s.,!?;:-]'
        else:
            pattern = r'[^a-zA-Z0-9.,!?;:-]'
    else:
        if keep_spaces:
            pattern = r'[^a-zA-Z0-9\s]'
        else:
            pattern = r'[^a-zA-Z0-9]'

    return re.sub(pattern, '', text)


def truncate_text(
    text: str,
    max_length: int = 100,
    suffix: str = "..."
) -> str:
    """
    Truncate text to maximum length.

    Args:
        text: Input text
        max_length: Maximum length
        suffix: Suffix to append

    Returns:
        Truncated text
    """
    if len(text) > max_length:
        return text[:max_length - len(suffix)] + suffix
    return text


def count_sentences(text: str) -> int:
    """
    Count sentences in text.

    Args:
        text: Input text

    Returns:
        Number of sentences
    """
    # Split by sentence-ending punctuation
    sentences = re.split(r'[.!?]+', text)
    return len([s for s in sentences if s.strip()])


def count_words(text: str) -> int:
    """
    Count words in text.

    Args:
        text: Input text

    Returns:
        Number of words
    """
    return len(text.split())


def extract_urls(text: str) -> List[str]:
    """
    Extract URLs from text.

    Args:
        text: Input text

    Returns:
        List of URLs
    """
    pattern = r'https?://[^\s]+'
    return re.findall(pattern, text)


def extract_emails(text: str) -> List[str]:
    """
    Extract email addresses from text.

    Args:
        text: Input text

    Returns:
        List of email addresses
    """
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return re.findall(pattern, text)


def extract_mentions(text: str) -> List[str]:
    """
    Extract @mentions from text.

    Args:
        text: Input text

    Returns:
        List of mentions
    """
    pattern = r'@\w+'
    return re.findall(pattern, text)


def extract_hashtags(text: str) -> List[str]:
    """
    Extract #hashtags from text.

    Args:
        text: Input text

    Returns:
        List of hashtags
    """
    pattern = r'#\w+'
    return re.findall(pattern, text)


def extract_numbers(text: str) -> List[float]:
    """
    Extract numbers from text.

    Args:
        text: Input text

    Returns:
        List of numbers
    """
    pattern = r'\d+\.?\d*'
    matches = re.findall(pattern, text)
    return [float(m) for m in matches]


def camel_to_snake(text: str) -> str:
    """
    Convert camelCase to snake_case.

    Args:
        text: Input text

    Returns:
        Converted text
    """
    text = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', text).lower()


def snake_to_camel(text: str) -> str:
    """
    Convert snake_case to camelCase.

    Args:
        text: Input text

    Returns:
        Converted text
    """
    components = text.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


def highlight_keywords(
    text: str,
    keywords: List[str],
    highlight_char: str = "*"
) -> str:
    """
    Highlight keywords in text.

    Args:
        text: Input text
        keywords: Keywords to highlight
        highlight_char: Character to surround keywords

    Returns:
        Text with highlighted keywords
    """
    result = text
    for keyword in keywords:
        # Case-insensitive replacement
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        result = pattern.sub(f"{highlight_char}{keyword}{highlight_char}", result)
    return result


def similarity_score(text1: str, text2: str) -> float:
    """
    Calculate text similarity score (simple Levenshtein-based).

    Args:
        text1: First text
        text2: Second text

    Returns:
        Similarity score (0-1)
    """
    text1 = normalize_text(text1)
    text2 = normalize_text(text2)

    # Dice coefficient
    set1 = set(text1.split())
    set2 = set(text2.split())

    if not set1 and not set2:
        return 1.0

    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))

    return intersection / union if union > 0 else 0.0