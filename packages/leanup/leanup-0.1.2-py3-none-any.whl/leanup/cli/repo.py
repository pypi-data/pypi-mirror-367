import click
import shutil
import sys
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from leanup.const import LEANUP_CACHE_DIR
from leanup.repo.manager import RepoManager, LeanRepo
from leanup.utils.custom_logger import setup_logger

logger = setup_logger("repo_cli")

@click.group()
def repo():
    """Repository management commands"""
    pass


@repo.command()
@click.argument('repository', required=False)
@click.option('--source', '-s', help='Repository source', default='https://github.com')
@click.option('--branch', '-b', help='Branch or tag to clone')
@click.option('--force', '-f', is_flag=True, help='Replace existing directory')
@click.option('--dest-dir', '-d', help='Destination directory', type=click.Path(path_type=Path))
@click.option('--interactive', '-i', is_flag=True, help='Interactive mode')
def install(repository: str, source: str, branch: Optional[str], force: bool,
            dest_dir: Optional[Path], interactive: bool):
    """Install a repository"""
    if interactive:
        if repository:
            click.echo(f"Repository name: {repository}")
        else:
            repository = click.prompt("Repository name(required)", type=str)
        source = click.prompt("Repository source", type=str, default=source)
        branch = click.prompt("Branch or tag", type=str, default=branch or "")
    
    if not repository:
        click.echo("Error: Repository name is required", err=True)
        sys.exit(1)

    # Determine URL
    repo_url = f"{source.rstrip('/')}/{repository}"
    # Determine destination directory
    if dest_dir:
        dest_path = dest_dir
    else:
        repository = repository.replace('/', '_').lower()
        # Default to current directory + repo name
        dir_name = f"{repository}_{branch}" if branch else repository
        dest_path = LEANUP_CACHE_DIR / "repos" / dir_name
    if interactive:
        dest_path = click.prompt("Destination directory", type=click.Path(path_type=Path), default=dest_path)
    
    # Check if directory exists
    if dest_path.exists():
        if interactive:
            force = click.confirm("Repository already exists. Replace it?", default=force)
        if not force:
            click.echo(f"Directory {dest_path} already exists. Use --force to replace.", err=True)
            sys.exit(1)
        else:
            shutil.rmtree(dest_path)
            click.echo(f"Removed existing directory: {dest_path}")
    
    # Create parent directories
    dest_path.mkdir(parents=True, exist_ok=True)
    
    # Clone repository
    click.echo(f"Cloning {repo_url} to {dest_path}...")
    repo_manager = RepoManager(dest_path)
    
    success = repo_manager.clone_from(
        url=repo_url,
        branch=branch,
        depth=1  # Shallow clone for faster download
    )
    
    if success:
        click.echo(f"✓ Repository cloned successfully to {dest_path}")
        
        # Check if it's a Lean project and run post-install commands
        if (dest_path / "lakefile.lean").exists() or (dest_path / "lakefile.toml").exists():
            click.echo("📦 Detected Lean project")
            
            # Show lean-toolchain if exists
            toolchain_file = dest_path / "lean-toolchain"
            if toolchain_file.exists():
                toolchain = toolchain_file.read_text().strip()
                click.echo(f"🔧 Lean toolchain: {toolchain}")
            
            # Execute post-install commands
            lean_repo = LeanRepo(dest_path)
            
            # Lake update
            click.echo("Executing lake update...")
            try:
                stdout, stderr, returncode = lean_repo.lake_update()
                if returncode == 0:
                    click.echo("✓ lake update completed")
                else:
                    click.echo(f"⚠ lake update failed: {stderr}", err=True)
            except Exception as e:
                click.echo(f"⚠ lake update error: {e}", err=True)
            
            # Lake build
            click.echo("Building project...")
            try:
                stdout, stderr, returncode = lean_repo.lake_build()
                if returncode == 0:
                    click.echo("✓ Build completed")
                else:
                    click.echo(f"⚠ Build failed: {stderr}", err=True)
            except Exception as e:
                click.echo(f"⚠ Build error: {e}", err=True)
    else:
        click.echo("✗ Failed to clone repository", err=True)
        sys.exit(1)


@repo.command()
@click.option('--name', '-n', help='Filter by repository name')
@click.option('--search-dir', '-d', help='Directory to search for repositories', 
              type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
              default=LEANUP_CACHE_DIR / "repos")
def list(name: Optional[str], search_dir: Path):
    """List repositories in the specified directory"""
    
    if not search_dir.exists():
        click.echo(f"Directory {search_dir} doesn't exist.")
        return
    names = [dir.name for dir in search_dir.iterdir() if dir.is_dir()]

    if name:
        names = [n for n in names if name in n]
    
    for name in names:
        click.echo(name)
