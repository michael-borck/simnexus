#!/usr/bin/env python3
"""
Release script for SimLab.

This script automates the process of building and publishing SimLab to PyPI.
It performs several checks before publishing to ensure the release is ready.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

# Get the project root directory
ROOT_DIR = Path(__file__).parent.parent.resolve()


def run_command(command, check=True):
    """Run a shell command and print its output."""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result


def check_working_directory():
    """Ensure the working directory is clean."""
    result = run_command("git status --porcelain", check=False)
    if result.stdout.strip():
        print("Error: Working directory is not clean. Commit or stash changes before releasing.")
        sys.exit(1)
    print("✅ Working directory is clean")


def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import build
        import twine
        print("✅ Dependencies are installed")
    except ImportError as e:
        print(f"Error: Required dependency not found - {e}")
        print("Install with: pip install build twine")
        sys.exit(1)


def parse_version():
    """Parse the current version from pyproject.toml."""
    pyproject_path = ROOT_DIR / "pyproject.toml"
    with open(pyproject_path, "r") as f:
        for line in f:
            if line.strip().startswith('version = "'):
                version = line.strip().split('"')[1]
                return version
    print("Error: Could not parse version from pyproject.toml")
    sys.exit(1)


def tag_version(version, push=False):
    """Create a git tag for the version."""
    tag = f"v{version}"
    run_command(f'git tag -a {tag} -m "Release {tag}"')
    print(f"✅ Created tag {tag}")

    if push:
        run_command(f"git push origin {tag}")
        print(f"✅ Pushed tag {tag} to origin")


def build_package():
    """Build the package."""
    os.chdir(ROOT_DIR)
    run_command("python -m build")
    print("✅ Built package")


def upload_to_pypi(test=False):
    """Upload the package to PyPI or TestPyPI."""
    import glob
    from twine.commands.upload import upload
    
    print("Uploading distributions to", "TestPyPI" if test else "PyPI")
    dist_files = glob.glob(str(ROOT_DIR / "dist" / "*"))
    if not dist_files:
        print("Error: No distribution files found in ./dist/")
        sys.exit(1)
    
    args = ["--verbose"]
    if test:
        args.extend(["--repository-url", "https://test.pypi.org/legacy/"])
    args.extend(dist_files)
    
    try:
        # Use twine directly
        os.system(f"python -m twine upload {'--repository-url https://test.pypi.org/legacy/' if test else ''} dist/*")
        print(f"✅ Uploaded to {'TestPyPI' if test else 'PyPI'}")
    except Exception as e:
        print(f"Error during upload: {e}")
        sys.exit(1)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Release SimLab to PyPI")
    parser.add_argument(
        "--test", action="store_true", help="Upload to TestPyPI instead of PyPI"
    )
    parser.add_argument(
        "--no-tag", action="store_true", help="Skip creating a git tag"
    )
    parser.add_argument(
        "--no-push", action="store_true", help="Skip pushing the git tag"
    )
    args = parser.parse_args()

    # Check dependencies
    check_dependencies()

    # Check working directory
    check_working_directory()

    # Parse version
    version = parse_version()
    print(f"Releasing version {version}")

    # Build package
    build_package()

    # Create tag
    if not args.no_tag:
        tag_version(version, push=not args.no_push)

    # Upload to PyPI
    upload_to_pypi(test=args.test)

    print("\n🎉 Release completed successfully!")
    if args.test:
        print("\nTest package available at: https://test.pypi.org/project/sim-lab/")
    else:
        print("\nPackage available at: https://pypi.org/project/sim-lab/")


if __name__ == "__main__":
    main()