#!/bin/env python3
import os
import sys
import json
import httpx
from rich.console import Console

here = os.path.abspath(os.path.dirname(__file__))
console = Console()

GENERAL_USAGE_HINT = """
[yellow]Usage: gai-pull --version | gai-pull <model_name>
options:
  --version      Get the version of gai-pull
  <model_name>   Pull a model (refer to gai.yml) from its respective remote repository. Example: gai-pull llama-3.1-exl2
[/]
"""


def app_dir():
    with open(os.path.expanduser("~/.gairc"), "r") as file:
        rc = file.read()
        jsoned = json.loads(rc)
        return os.path.expanduser(jsoned["app_dir"])



def get_current_version():
    """Get the current version from version.txt"""
    version_file_path = os.path.join(here, "..", "..", "data", "version.txt")
    try:
        with open(version_file_path, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "unknown"


def get_latest_pypi_version(package_name="gai-pull", timeout=5):
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
            console.print(f"   To update: [cyan]uvx gai-pull@latest[/cyan]")
            console.print()
    except Exception:
        # Silently ignore errors in version checking to not break the main functionality
        pass

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Gai Pull Tool")

    # Global arguments
    # --version
    parser.add_argument(
        "-v", "--version", help="Get the version of gai-pull", action="store_true"
    )

    # model_name as positional argument (optional)
    parser.add_argument(
        "model_name", 
        nargs="?", 
        help="Name of the model to pull"
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
        print(f"gai-pull version: {version}")
        sys.exit(0)

    elif args.model_name:
        print(f"Pulling model: {args.model_name}")
        from gai.pull.gai_pull import pull

        pull(model_name=args.model_name)
    
    else:
        # No arguments provided, show usage
        print(GENERAL_USAGE_HINT)
        sys.exit(1)


if __name__ == "__main__":
    # Check for version updates before running main
    check_version_update()    
    main()
