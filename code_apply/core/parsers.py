"""Parsers for different file content formats."""

import re
from typing import Dict, List, Tuple, Protocol


class ContentParser(Protocol):
    """Protocol for content parsers."""
    
    def parse(self, content: str) -> List[Tuple[str, str]]:
        """Parse content and return a list of (file_path, file_content) tuples."""
        ...


class PromptOutputParser:
    """Parser for the prompt output format."""
    
    def __init__(self):
        # 改进的正则表达式以更健壮地处理语言说明符
        self.file_path_pattern = r"---FILE_PATH:\s*(.*?)\s*\n```(?:(\w+)?\n)?(.*?)```\s*\n---END_FILE"
        self.file_regex = re.compile(self.file_path_pattern, re.DOTALL)
    
    def parse(self, content: str) -> List[Tuple[str, str]]:
        """
        Parse content in the prompt output format.
        
        The prompt output format is expected to be in the form:
        
        ---FILE_PATH: path/to/file.ext
        ```language
        file content
        ```
        ---END_FILE
        
        Args:
            content: The prompt output content to parse
            
        Returns:
            A list of tuples containing (file_path, file_content)
        """
        matches = self.file_regex.finditer(content)
        results = []
        
        for match in matches:
            file_path = match.group(1).strip()
            # group(2) is the language specifier (optional)
            file_content = match.group(3)
            results.append((file_path, file_content))
        
        return results


def get_parser(parser_type: str = "prompt") -> ContentParser:
    """
    Factory function to get the appropriate parser based on type.
    
    Args:
        parser_type: The type of parser to return
        
    Returns:
        A ContentParser instance
    """
    parsers = {
        "prompt": PromptOutputParser(),
    }
    
    return parsers.get(parser_type, PromptOutputParser())
