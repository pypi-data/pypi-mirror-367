#!/bin/env python3
import os
import sys
import json
import httpx
from rich.console import Console

here = os.path.abspath(os.path.dirname(__file__))
console = Console()

GENERAL_USAGE_HINT = """
[yellow]Usage: gai-init --version | gai-init [--force]
options:
  --version      Get the version of gai-init
  --force        Force initialization, deleting existing directories if they exist (default: False)
[/]
"""


def app_dir():
    with open(os.path.expanduser("~/.gairc"), "r") as file:
        rc = file.read()
        jsoned = json.loads(rc)
        return os.path.expanduser(jsoned["app_dir"])


def get_pyproject_path():
    # locate pyproject.toml by traversing up the directory tree
    current_dir = os.getcwd()
    while current_dir != os.path.dirname(current_dir):
        pyproject_path = os.path.join(current_dir, "pyproject.toml")
        if os.path.exists(pyproject_path):
            return pyproject_path
        current_dir = os.path.dirname(current_dir)
    sys.exit("❌ pyproject.toml not found in the directory tree")


def get_current_version():
    """Get the current version from version.txt"""
    version_file_path = os.path.join(here, "..", "..", "data", "version.txt")
    try:
        with open(version_file_path, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "unknown"


def get_latest_pypi_version(package_name="gai-init", timeout=5):
    """Get the latest version from PyPI"""
    try:
        with httpx.Client(timeout=timeout) as client:
            response = client.get(f"https://pypi.org/pypi/{package_name}/json")
            if response.status_code == 200:
                data = response.json()
                return data["info"]["version"]
            return None
    except Exception:
        return None


def check_version_update():
    """Check if a newer version is available on PyPI and show warning if needed"""
    try:
        current_version = get_current_version()
        latest_version = get_latest_pypi_version()
        
        if latest_version and current_version != latest_version:
            console.print(f"⚠️  [yellow]Version mismatch detected![/yellow]")
            console.print(f"   Current version: [red]{current_version}[/red]")
            console.print(f"   Latest version:  [green]{latest_version}[/green]")
            console.print(f"   To update: [cyan]uvx gai-init@latest[/cyan]")
            console.print()
    except Exception:
        # Silently ignore errors in version checking to not break the main functionality
        pass


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Gai Init Tool")

    # Global arguments
    # --version
    parser.add_argument(
        "-v", "--version", help="Get the version of gai-init", action="store_true"
    )

    # --force flag (optional)
    parser.add_argument(
        "-f",
        "--force",
        help="Force initialization, deleting existing directories if they exist (default: False)",
        action="store_true",
    )

    try:
        args = parser.parse_args()
    except SystemExit:
        print("Syntax Error: Invalid command.")
        print(GENERAL_USAGE_HINT)
        raise
    except Exception as e:
        print(f"An error occurred: {e}")
        print(GENERAL_USAGE_HINT)
        raise

    # Handle commands

    if args.version:
        """
        --version or -v
        """
        file_dir = os.path.dirname(__file__)
        print(f"File directory: {file_dir}")
        version = get_current_version()
        print(f"gai-init version: {version}")
        sys.exit(0)

    else:
        """
        Default initialization (with optional --force flag)
        """
        if args.force:
            print("Force initialization enabled.")
        else:
            print("Normal initialization.")

        # import init function lazily to allow smoke testing without importing the entire package
        from gai.init.gai_init import init

        force = hasattr(args, "force") and args.force
        init(force=force)


if __name__ == "__main__":
    # Check for version updates before running main
    check_version_update()
    main()
