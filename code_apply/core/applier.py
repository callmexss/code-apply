"""Core module for code application logic."""

import shutil
from pathlib import Path
from typing import List, Union
import click

from code_apply.core.matchers import find_matching_files, calculate_similarity
from code_apply.core.parsers import get_parser
from code_apply.utils.file_utils import ensure_directory


def apply_code(source: Union[str, Path], target: Union[str, Path], 
              dry_run: bool = False, verbose: bool = False) -> bool:
    """
    Apply code from source to target based on name patterns.

    Args:
        source: Source directory or file path
        target: Target directory or file path
        dry_run: If True, only show what would be done without making changes
        verbose: If True, print verbose output

    Returns:
        True if successful, False otherwise
    """
    source_path = Path(source)
    target_path = Path(target)

    if verbose:
        click.echo(f"Source: {source_path}")
        click.echo(f"Target: {target_path}")

    if not source_path.exists():
        click.echo(f"Error: Source path {source_path} does not exist", err=True)
        return False

    try:
        if source_path.is_file():
            return _apply_single_file(source_path, target_path, dry_run, verbose)
        else:
            return _apply_directory(source_path, target_path, dry_run, verbose)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        return False


def _apply_single_file(source_path: Path, target_path: Path, 
                      dry_run: bool, verbose: bool) -> bool:
    """Apply a single file from source to target."""
    if dry_run:
        click.echo(f"Would copy {source_path} to {target_path}")
        return True
    else:
        # Create parent directories if they don't exist
        ensure_directory(target_path.parent)
        shutil.copy2(source_path, target_path)
        if verbose:
            click.echo(f"Copied {source_path} to {target_path}")
        return True


def _apply_directory(source_path: Path, target_path: Path, 
                    dry_run: bool, verbose: bool) -> bool:
    """Apply a directory of files from source to target."""
    if not dry_run:
        ensure_directory(target_path)

    for item in source_path.glob('/*'):
        # Calculate relative path from source
        rel_path = item.relative_to(source_path)
        dest_path = target_path / rel_path

        if item.is_file():
            if dry_run:
                click.echo(f"Would copy {item} to {dest_path}")
            else:
                ensure_directory(dest_path.parent)
                shutil.copy2(item, dest_path)
                if verbose:
                    click.echo(f"Copied {item} to {dest_path}")

    return True


def apply_from_prompt(content: str, target_dir: Union[str, Path], 
                     similarity_threshold: float = 0.7, 
                     force: bool = False, dry_run: bool = False, 
                     verbose: bool = False) -> bool:
    """
    Apply code from a prompt output to a target directory.
    
    Args:
        content: The prompt output content
        target_dir: The target directory path
        similarity_threshold: The similarity threshold for matching files (0.0 to 1.0)
        force: If True, force replacement regardless of similarity
        dry_run: If True, only show what would be done without making changes
        verbose: If True, print verbose output
        
    Returns:
        True if successful, False otherwise
    """
    target_path = Path(target_dir)
    
    if not target_path.exists():
        if verbose:
            click.echo(f"Target directory {target_path} does not exist, creating it")
        if not dry_run:
            ensure_directory(target_path)
    
    try:
        # Parse files from the prompt output
        parser = get_parser("prompt")
        parsed_files = parser.parse(content)
        
        if verbose:
            click.echo(f"Parsed {len(parsed_files)} files from prompt output")
        
        # Process each parsed file
        for file_path, file_content in parsed_files:
            process_parsed_file(
                file_path=file_path,
                file_content=file_content,
                target_path=target_path,
                similarity_threshold=similarity_threshold,
                force=force,
                dry_run=dry_run,
                verbose=verbose
            )
        
        return True
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        return False


def process_parsed_file(file_path: str, file_content: str, target_path: Path,
                       similarity_threshold: float, force: bool,
                       dry_run: bool, verbose: bool) -> None:
    """
    Process a single parsed file and apply it to the target directory.
    
    Args:
        file_path: The file path from the parsed content
        file_content: The file content from the parsed content
        target_path: The target directory path
        similarity_threshold: The similarity threshold for matching files
        force: If True, force replacement regardless of similarity
        dry_run: If True, only show what would be done without making changes
        verbose: If True, print verbose output
    """
    if verbose:
        click.echo(f"Processing file: {file_path}")
    
    # Find matching files based on filename
    filename = Path(file_path).name
    matching_files = find_matching_files(filename, target_path)
    
    if not matching_files:
        # No matching files found - create a new file
        create_new_file(file_path, file_content, target_path, dry_run, verbose)
    else:
        # Process matching files
        process_matching_files(
            file_path=file_path,
            file_content=file_content,
            matching_files=matching_files,
            target_path=target_path,
            similarity_threshold=similarity_threshold,
            force=force,
            dry_run=dry_run,
            verbose=verbose
        )


def create_new_file(file_path: str, file_content: str, target_path: Path,
                   dry_run: bool, verbose: bool) -> None:
    """Create a new file in the target directory."""
    target_file = target_path / file_path
    
    if verbose:
        click.echo(f"No matching files found, creating new file: {target_file}")
    
    if dry_run:
        click.echo(f"Would create {target_file}")
    else:
        ensure_directory(target_file.parent)
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(file_content)
        if verbose:
            click.echo(f"Created {target_file}")


def process_matching_files(file_path: str, file_content: str, matching_files: List[Path],
                          target_path: Path, similarity_threshold: float,
                          force: bool, dry_run: bool, verbose: bool) -> None:
    """Process matching files and decide whether to update or create a new file."""
    # Find the best match based on content similarity
    best_match = None
    best_score = 0.0
    
    for match_path in matching_files:
        try:
            with open(match_path, 'r', encoding='utf-8') as f:
                target_content = f.read()
            
            similarity = calculate_similarity(file_content, target_content)
            
            if similarity > best_score:
                best_score = similarity
                best_match = match_path
        except Exception:
            # Skip files that can't be read as text
            continue
    
    # If we have a good match or force is enabled
    if best_match and best_score >= similarity_threshold:
        update_existing_file(best_match, file_content, best_score, dry_run, verbose)
    elif force:
        # No good match was found, but force is enabled
        create_new_file(file_path, file_content, target_path, dry_run, verbose)
    else:
        # No good match was found and force is not enabled
        click.echo(f"No suitable match found for {file_path} (best similarity: {best_score:.2f})")


def update_existing_file(file_path: Path, file_content: str, 
                        similarity_score: float, dry_run: bool, 
                        verbose: bool) -> None:
    """Update an existing file with new content."""
    if verbose:
        click.echo(f"Found matching file: {file_path} (similarity: {similarity_score:.2f})")
    
    if dry_run:
        click.echo(f"Would update {file_path}")
    else:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(file_content)
        if verbose:
            click.echo(f"Updated {file_path}")
