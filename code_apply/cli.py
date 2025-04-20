"""Command line interface for code_apply."""

import click
from code_apply import __version__
from code_apply.code_apply import apply_code, apply_from_prompt

@click.group()
@click.version_option(version=__version__)
def main():
    """Code Apply - Apply code content based on name."""
    pass

@main.command()
@click.argument('source', type=click.Path(exists=True))
@click.argument('target', type=click.Path())
@click.option('--dry-run', is_flag=True, help='Show what would be done without making changes.')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output.')
def apply(source, target, dry_run, verbose):
    """Apply code from SOURCE to TARGET based on name patterns."""
    click.echo(f"Applying code from {source} to {target}")
    if dry_run:
        click.echo("Dry run mode - no changes will be made")
    
    result = apply_code(source, target, dry_run=dry_run, verbose=verbose)
    
    if result:
        click.echo("Code application completed successfully!")
    else:
        click.echo("Code application failed!", err=True)

@main.command()
@click.argument('input_file', type=click.File('r'), required=False)
@click.option('--target', '-t', type=click.Path(), required=True, 
              help='Target directory to apply the code to.')
@click.option('--threshold', '-th', type=float, default=0.7, 
              help='Similarity threshold for file matching (0.0 to 1.0).')
@click.option('--force', '-f', is_flag=True, 
              help='Force replacement regardless of similarity.')
@click.option('--dry-run', is_flag=True, 
              help='Show what would be done without making changes.')
@click.option('--verbose', '-v', is_flag=True, 
              help='Enable verbose output.')
def apply_prompt(input_file, target, threshold, force, dry_run, verbose):
    """
    Apply code from a prompt output to a target directory.
    
    If INPUT_FILE is not specified, reads from standard input.
    """
    import sys
    
    # Read from stdin if no input file is provided
    if input_file is None:
        content = sys.stdin.read()
    else:
        content = input_file.read()
    
    if verbose:
        click.echo(f"Applying code from prompt to {target}")
        click.echo(f"Similarity threshold: {threshold}")
        if force:
            click.echo("Force mode enabled - will replace regardless of similarity")
        if dry_run:
            click.echo("Dry run mode - no changes will be made")
    
    result = apply_from_prompt(
        content=content,
        target_dir=target,
        similarity_threshold=threshold,
        force=force,
        dry_run=dry_run,
        verbose=verbose
    )
    
    if result:
        click.echo("Code application completed successfully!")
    else:
        click.echo("Code application failed!", err=True)

if __name__ == '__main__':
    main()  # pragma: no cover
