"""File matching and similarity comparison utilities."""

import os
from pathlib import Path
from difflib import SequenceMatcher
from typing import List, Optional, Tuple


def find_matching_files(filename: str, target_dir: Path) -> List[Path]:
    """
    Find files with matching names in the target directory.
    
    Args:
        filename: The filename to search for
        target_dir: The target directory to search in
        
    Returns:
        A list of matching file paths
    """
    matches = []
    
    for root, _, files in os.walk(target_dir):
        for file in files:
            if file == filename:
                matches.append(Path(root) / file)
    
    return matches


def calculate_similarity(text1: str, text2: str) -> float:
    """
    Calculate the similarity ratio between two text strings.
    
    Args:
        text1: First text string
        text2: Second text string
        
    Returns:
        Similarity ratio between 0.0 and 1.0
    """
    return SequenceMatcher(None, text1, text2).ratio()


def find_best_match(source_path: str, source_content: str, target_dir: Path, 
                   threshold: float = 0.7) -> Tuple[Optional[Path], float]:
    """
    Find the best matching file based on filename and content similarity.
    
    Args:
        source_path: The source file path
        source_content: The source file content
        target_dir: The target directory to search in
        threshold: The similarity threshold (default 0.7)
        
    Returns:
        A tuple containing the best match path (or None) and the similarity score
    """
    filename = Path(source_path).name
    matching_files = find_matching_files(filename, target_dir)
    
    best_match = None
    best_score = 0.0
    
    for match_path in matching_files:
        try:
            with open(match_path, 'r', encoding='utf-8') as f:
                target_content = f.read()
            
            similarity = calculate_similarity(source_content, target_content)
            
            if similarity > best_score:
                best_score = similarity
                best_match = match_path
        except Exception:
            # Skip files that can't be read as text
            continue
    
    if best_score >= threshold:
        return best_match, best_score
    
    return None, best_score
