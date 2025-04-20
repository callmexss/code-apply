"""Main module for code_apply."""

import os
import shutil
from pathlib import Path
import click

def apply_code(source, target, dry_run=False, verbose=False):
    """
    Apply code from source to target based on name patterns.

    Args:
        source (str): Source directory or file path
        target (str): Target directory or file path
        dry_run (bool): If True, only show what would be done without making changes
        verbose (bool): If True, print verbose output

    Returns:
        bool: True if successful, False otherwise
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
            if dry_run:
                click.echo(f"Would copy {source_path} to {target_path}")
                return True
            else:
                # Create parent directories if they don't exist
                target_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_path, target_path)
                if verbose:
                    click.echo(f"Copied {source_path} to {target_path}")
        else:  # source is a directory
            if not target_path.exists() and not dry_run:
                target_path.mkdir(parents=True, exist_ok=True)

            for item in source_path.glob('**/*'):
                # Calculate relative path from source
                rel_path = item.relative_to(source_path)
                dest_path = target_path / rel_path

                if item.is_file():
                    if dry_run:
                        click.echo(f"Would copy {item} to {dest_path}")
                    else:
                        dest_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(item, dest_path)
                        if verbose:
                            click.echo(f"Copied {item} to {dest_path}")

        return True
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        return False


def apply_from_prompt(content: str, target_dir: str, similarity_threshold: float = 0.7, 
                     force: bool = False, dry_run: bool = False, verbose: bool = False):
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
        bool: True if successful, False otherwise
    """
    from code_apply.parsers import get_parser
    from code_apply.matchers import find_matching_files, calculate_similarity
    
    parser = get_parser("prompt")
    target_path = Path(target_dir)
    
    if not target_path.exists():
        if verbose:
            click.echo(f"Target directory {target_path} does not exist, creating it")
        if not dry_run:
            target_path.mkdir(parents=True, exist_ok=True)
    
    try:
        parsed_files = parser.parse(content)
        
        if verbose:
            click.echo(f"Parsed {len(parsed_files)} files from prompt output")
        
        for file_path, file_content in parsed_files:
            if verbose:
                click.echo(f"Processing file: {file_path}")
            
            # Find matching files based on filename
            filename = Path(file_path).name
            matching_files = find_matching_files(filename, target_path)
            
            # Decide what to do based on matching files
            if not matching_files:
                # No matching files found - always create a new file
                target_file = target_path / file_path
                
                if verbose:
                    click.echo(f"No matching files found, creating new file: {target_file}")
                
                if dry_run:
                    click.echo(f"Would create {target_file}")
                else:
                    target_file.parent.mkdir(parents=True, exist_ok=True)
                    with open(target_file, 'w', encoding='utf-8') as f:
                        f.write(file_content)
                    if verbose:
                        click.echo(f"Created {target_file}")
            else:
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
                if best_score >= similarity_threshold:
                    if verbose:
                        click.echo(f"Found matching file: {best_match} (similarity: {best_score:.2f})")
                    
                    if dry_run:
                        click.echo(f"Would update {best_match}")
                    else:
                        with open(best_match, 'w', encoding='utf-8') as f:
                            f.write(file_content)
                        if verbose:
                            click.echo(f"Updated {best_match}")
                elif force:
                    # No good match was found, but force is enabled
                    target_file = target_path / file_path
                    
                    if verbose:
                        click.echo(f"Force mode enabled, creating new file: {target_file}")
                    
                    if dry_run:
                        click.echo(f"Would create {target_file}")
                    else:
                        target_file.parent.mkdir(parents=True, exist_ok=True)
                        with open(target_file, 'w', encoding='utf-8') as f:
                            f.write(file_content)
                        if verbose:
                            click.echo(f"Created {target_file}")
                else:
                    # No good match was found and force is not enabled
                    click.echo(f"No suitable match found for {file_path} (best similarity: {best_score:.2f})")
        
        return True
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        return False
