"""Core functionality for Code Apply."""

from code_apply.core.applier import apply_code, apply_from_prompt
from code_apply.core.matchers import find_matching_files, calculate_similarity, find_best_match
from code_apply.core.parsers import get_parser, ContentParser, PromptOutputParser

__all__ = [
    'apply_code',
    'apply_from_prompt',
    'find_matching_files',
    'calculate_similarity',
    'find_best_match',
    'get_parser',
    'ContentParser',
    'PromptOutputParser',
]
