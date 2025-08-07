from invoke import task
import shutil
import sys
from pathlib import Path


@task
def clean(c):
    """Clean build artifacts"""
    patterns = ["build", "dist", "*.egg-info", "**/__pycache__"]
    for pattern in patterns:
        for path in Path().glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
                print(f"Removed {path}")
            else:
                path.unlink()
                print(f"Removed {path}")


@task
def build(c):
    """Build distribution packages using Flit"""
    clean(c)
    c.run("python -m flit build")
    print("\nBuild complete! Packages are in dist/")


@task
def check_dist(c):
    """Check distribution packages with twine"""
    c.run("python -m twine check dist/*")


@task
def deploy(c, repository="pypi"):
    """Deploy to PyPI or TestPyPI
    
    Args:
        repository: Either 'pypi' or 'testpypi' (default: 'pypi')
    """
    if repository not in ["pypi", "testpypi"]:
        print(f"Error: repository must be 'pypi' or 'testpypi', got '{repository}'")
        sys.exit(1)
    
    # Check if dist directory exists and has files
    dist_path = Path("dist")
    if not dist_path.exists() or not list(dist_path.glob("*")):
        print("No distribution files found. Run 'invoke build' first.")
        sys.exit(1)
    
    # Check the distribution files
    check_dist(c)
    
    # Deploy to PyPI
    cmd = f"python -m twine upload --repository {repository}"
    cmd += " dist/*"
    
    print(f"\nDeploying to {repository}...")
    c.run(cmd)


@task
def release(c):
    """Build and deploy to PyPI"""
    build(c)
    deploy(c, repository="pypi")


@task
def dev(c):
    """Install package in development mode"""
    c.run("python -m flit install --symlink")


@task
def lint(c):
    """Run linting (placeholder for future linting setup)"""
    print("No linters configured yet. Consider adding ruff or flake8.")


@task
def test(c):
    """Run tests (placeholder for future test setup)"""
    print("No tests configured yet. Consider adding pytest.")


@task
def bump(c, part="patch"):
    """Bump version number
    
    Args:
        part: Version part to bump - 'major', 'minor', or 'patch' (default: 'patch')
    """
    if part not in ["major", "minor", "patch"]:
        print(f"Error: part must be 'major', 'minor', or 'patch', got '{part}'")
        sys.exit(1)
    
    # Read current version from __init__.py
    init_file = Path("kintu/__init__.py")
    lines = init_file.read_text().splitlines()
    
    # Find and parse version line
    version_line_idx = None
    old_version = None
    
    for i, line in enumerate(lines):
        if line.startswith('__version__ = "') and line.endswith('"'):
            version_line_idx = i
            # Extract version string between quotes
            version_str = line.split('"')[1]
            old_version = version_str
            break
    
    if version_line_idx is None or old_version is None:
        print("Error: Could not find version in kintu/__init__.py")
        sys.exit(1)
    
    # Parse version parts
    try:
        parts = old_version.split(".")
        major = int(parts[0])
        minor = int(parts[1])
        patch = int(parts[2])
    except (ValueError, IndexError):
        print(f"Error: Invalid version format '{old_version}'. Expected X.Y.Z")
        sys.exit(1)
    
    # Bump the appropriate part
    if part == "major":
        major += 1
        minor = 0
        patch = 0
    elif part == "minor":
        minor += 1
        patch = 0
    else:  # patch
        patch += 1
    
    new_version = f"{major}.{minor}.{patch}"
    
    # Update the version line
    lines[version_line_idx] = f'__version__ = "{new_version}"'
    
    # Write back to file
    init_file.write_text("\n".join(lines) + "\n")
    print(f"Version bumped from {old_version} to {new_version}")