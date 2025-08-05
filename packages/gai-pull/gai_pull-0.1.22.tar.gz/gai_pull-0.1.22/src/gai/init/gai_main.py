#!/bin/env python3
import os
import sys
import json
import re

here = os.path.abspath(os.path.dirname(__file__))

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


def get_pyproject_path():
    # locate pyproject.toml by traversing up the directory tree
    current_dir = os.getcwd()
    while current_dir != os.path.dirname(current_dir):
        pyproject_path = os.path.join(current_dir, "pyproject.toml")
        if os.path.exists(pyproject_path):
            return pyproject_path
        current_dir = os.path.dirname(current_dir)
    sys.exit("❌ pyproject.toml not found in the directory tree")


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

        # locate pyproject.toml three levels up
        file_dir = os.path.dirname(__file__)
        print(f"File directory: {file_dir}")
        pyproject_path = get_pyproject_path()
        with open(pyproject_path, "r") as f:
            content = f.read()
            # Look for version = "x.x.x" pattern
            version_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
            version = version_match.group(1) if version_match else "unknown"
        print(f"gai-init version: {version}")
        sys.exit(0)

    elif args.model_name:
        print(f"Pulling model: {args.model_name}")
        from gai.init.gai_pull import pull

        pull(model_name=args.model_name)
    
    else:
        # No arguments provided, show usage
        print(GENERAL_USAGE_HINT)
        sys.exit(1)


if __name__ == "__main__":
    main()
