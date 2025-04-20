"""Tests for the prompt parser and matcher functionality."""

import os
import tempfile
from pathlib import Path

import pytest

from code_apply.parsers import PromptOutputParser, get_parser
from code_apply.matchers import find_matching_files, calculate_similarity, find_best_match
from code_apply.code_apply import apply_from_prompt


def test_prompt_parser():
    """Test that the prompt parser correctly parses the expected format."""
    test_content = """
---FILE_PATH: src/main.js
```javascript
console.log('Hello World');
```
---END_FILE

---FILE_PATH: src/styles.css
```css
body {
    font-family: sans-serif;
}
```
---END_FILE
"""
    
    parser = PromptOutputParser()
    results = parser.parse(test_content)
    
    assert len(results) == 2
    assert results[0][0] == "src/main.js"
    assert results[0][1] == "console.log('Hello World');\n"
    assert results[1][0] == "src/styles.css"
    assert results[1][1] == "body {\n    font-family: sans-serif;\n}\n"


def test_calculate_similarity():
    """Test the similarity calculation function."""
    text1 = "Hello World"
    text2 = "Hello World!"
    text3 = "Something completely different"
    
    assert calculate_similarity(text1, text1) == 1.0
    assert calculate_similarity(text1, text2) > 0.9  # Very similar
    assert calculate_similarity(text1, text3) < 0.5  # Not very similar


def test_find_matching_files():
    """Test finding matching files in a directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create some test files
        test_files = [
            "file1.txt",
            "subdir/file1.txt",
            "file2.txt"
        ]
        
        for file_path in test_files:
            full_path = Path(temp_dir) / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.touch()
        
        # Test finding matches
        matches = find_matching_files("file1.txt", Path(temp_dir))
        assert len(matches) == 2
        
        matches = find_matching_files("file2.txt", Path(temp_dir))
        assert len(matches) == 1
        
        matches = find_matching_files("nonexistent.txt", Path(temp_dir))
        assert len(matches) == 0


def test_apply_from_prompt():
    """Test applying code from a prompt to a directory."""
    test_content = """
---FILE_PATH: file1.txt
```
Hello World
```
---END_FILE

---FILE_PATH: subdir/file2.txt
```
This is file 2
```
---END_FILE
"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a test file with similar content
        test_file = Path(temp_dir) / "existing" / "file1.txt"
        test_file.parent.mkdir(parents=True)
        test_file.write_text("Hello Universe")
        
        # Apply the prompt content
        result = apply_from_prompt(
            content=test_content,
            target_dir=temp_dir,
            similarity_threshold=0.5,
            force=False,
            dry_run=False,
            verbose=False
        )
        
        assert result is True
        
        # Check that the existing file was updated
        assert test_file.read_text() == "Hello World\n"
        
        # Check that the new file was created
        new_file = Path(temp_dir) / "subdir" / "file2.txt"
        assert new_file.exists()
        assert new_file.read_text() == "This is file 2\n"
