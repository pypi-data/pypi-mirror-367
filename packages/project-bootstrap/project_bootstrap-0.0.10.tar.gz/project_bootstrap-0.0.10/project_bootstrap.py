#!/usr/bin/env python3
# project_bootstrap.py

import argparse
import os
import re
import subprocess
import sys
from typing import Dict, Optional, cast

import requests
from bs4 import BeautifulSoup, Tag

def get_latest_node_version() -> Optional[str]:
    """
    Fetches the latest stable Node.js version using nvm.
    Checks if nvm is installed, offers to install it if not.
    If installed, ensures it's up-to-date and fetches the latest version.
    """
    if not is_nvm_installed():
        if prompt_to_install_nvm():
            # After installation, we need to source nvm, which is tricky in a script.
            # For now, we'll ask the user to re-run.
            print("nvm installed. Please re-run the script in a new terminal.", file=sys.stderr)
            sys.exit(1)
        else:
            print("nvm is required to determine the latest Node.js version.", file=sys.stderr)
            return None
    
    return fetch_latest_node_version_with_nvm()


def find_nvm_sh() -> Optional[str]:
    """Finds the nvm.sh script in common locations."""
    # Homebrew on Apple Silicon
    brew_prefix_arm = "/opt/homebrew/opt/nvm/nvm.sh"
    if os.path.exists(brew_prefix_arm):
        return brew_prefix_arm
    
    # Homebrew on Intel
    brew_prefix_intel = "/usr/local/opt/nvm/nvm.sh"
    if os.path.exists(brew_prefix_intel):
        return brew_prefix_intel

    # Default nvm install script location
    default_path = os.path.expanduser("~/.nvm/nvm.sh")
    if os.path.exists(default_path):
        return default_path
        
    return None


def is_nvm_installed() -> bool:
    """Checks if nvm is installed by looking for nvm.sh."""
    return find_nvm_sh() is not None


def prompt_to_install_nvm() -> bool:
    """Prompts the user to install nvm using Homebrew."""
    answer = input("nvm is not installed. Would you like to install it now using Homebrew? (y/n) ")
    if answer.lower() == 'y':
        try:
            subprocess.run(['brew', 'install', 'nvm'], check=True)
            # The user will need to configure their shell to use nvm
            print("\nTo finish installation, add the following to your shell's startup file (e.g., ~/.zshrc):")
            print('  export NVM_DIR="$HOME/.nvm"')
            print('  [ -s "/opt/homebrew/opt/nvm/nvm.sh" ] && . "/opt/homebrew/opt/nvm/nvm.sh"')
            print('  [ -s "/opt/homebrew/opt/nvm/etc/bash_completion.d/nvm" ] && . "/opt/homebrew/opt/nvm/etc/bash_completion.d/nvm"')
            return True
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"Error installing nvm: {e}", file=sys.stderr)
            return False
    return False


def fetch_latest_node_version_with_nvm() -> Optional[str]:
    """Fetches the latest node version using nvm ls-remote."""
    nvm_sh_path = find_nvm_sh()
    if not nvm_sh_path:
        print("Could not find nvm.sh. This should not happen if is_nvm_installed() is checked first.", file=sys.stderr)
        return None
    try:
        # nvm is a shell function, so we need to source it before running.
        command = f'. "{nvm_sh_path}" && nvm ls-remote --lts | tail -n 1 | grep -o "v[0-9]*\\.[0-9]*\\.[0-9]*"'
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True, executable='/bin/zsh')
        version = result.stdout.strip()
        if version.startswith('v'):
            return version[1:]
        return version
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Error fetching Node.js version with nvm: {e}", file=sys.stderr)
        if isinstance(e, subprocess.CalledProcessError):
            print(f"nvm output:\n{e.stderr}", file=sys.stderr)
        return None


def get_latest_python_version() -> Optional[str]:
    """Fetches the latest stable Python version."""
    try:
        response = requests.get("https://www.python.org/downloads/")
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        version_element = soup.find('a', href=re.compile(r"/downloads/release/python-"))
        if version_element:
            return version_element.text.split()[-1]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Python version: {e}", file=sys.stderr)
    return None


def get_latest_swift_version() -> Optional[str]:
    """Fetches the latest stable Swift version."""
    try:
        response = requests.get("https://www.swift.org/download/")
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        version_element = soup.find('h3', id=re.compile(r'swift-.*-release'))
        if version_element:
            return version_element.text.split()[-1]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Swift version: {e}", file=sys.stderr)
    return None


def create_mise_toml(path: str, toolchain: str, versions: Dict[str, str]) -> None:
    """Creates a .mise.toml file."""
    config = ""
    if toolchain == 'python':
        config += '[env]\n'
        config += '_.python.venv = { path = ".venv", create = true }\n\n'

    config += '[tools]\n'
    for tool, version in versions.items():
        config += f'{tool} = "{version}"\n'

    with open(os.path.join(path, '.mise.toml'), 'w') as f:
        f.write(config)
    print("Created .mise.toml")


def create_version_instructions(path: str, toolchain: str) -> None:
    """Creates a .roo/rules/<toolchain>.md instruction file from a template."""
    rules_dir = os.path.join(path, '.roo', 'rules')
    os.makedirs(rules_dir, exist_ok=True)

    try:
        from importlib.resources import files as importlib_files
    except ImportError:
        from importlib_resources import files as importlib_files

    try:
        template_path = importlib_files('project_bootstrap').joinpath('templates', f'{toolchain}.md')
        content = template_path.read_text()
    except FileNotFoundError:
        print(f"Error: Template file not found for toolchain '{toolchain}' at {template_path}", file=sys.stderr)
        sys.exit(1)

    rules_path = os.path.join(rules_dir, f'{toolchain}.md')
    with open(rules_path, 'w') as f:
        f.write(content)
    print(f"Created {os.path.relpath(rules_path)}")


def create_gitignore(path: str, toolchain: str) -> None:
    """Fetches a .gitignore from gitignore.io and writes it to the specified path."""
    url = f"https://www.toptal.com/developers/gitignore/api/{toolchain}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        content = response.text
        # Remove the header comments from the gitignore.io response
        lines = content.splitlines()
        cleaned_lines = [
            line for line in lines
            if not line.startswith("# Created by") and not line.startswith("# Edit at") and not line.startswith("# End of")
        ]
        content = "\n".join(cleaned_lines).lstrip('\n')

        if toolchain == 'python':
            content = "# Ignore virtual environment\n.venv/\n\n" + content
        
        content = "# Ignore refs\nrefs/\n\n" + content

        with open(os.path.join(path, '.gitignore'), 'w') as f:
            f.write(content)
        print("Created .gitignore")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching .gitignore: {e}", file=sys.stderr)


def trust_mise_config(path: str) -> None:
    """Executes 'mise trust' in the specified directory."""
    print(f"Running 'mise trust' in {path}...")
    try:
        subprocess.run(['mise', 'trust'], cwd=path, check=True, capture_output=True, text=True)
        print("Successfully trusted .mise.toml.")
    except FileNotFoundError:
        print("Error: 'mise' command not found. Please ensure it's installed and in your PATH.", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error running 'mise trust':\n{e.stderr}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main function to configure the repository."""
    parser = argparse.ArgumentParser(description="Configure a repository with the latest toolchain versions.")
    parser.add_argument("toolchain", choices=['node', 'python', 'swift'], help="The toolchain to configure.")
    parser.add_argument("path", nargs='?', default='.', help="Path to the repository to configure.")
    args = parser.parse_args()

    repo_path = os.path.abspath(args.path)
    # Create the target directory if it doesn't exist
    os.makedirs(repo_path, exist_ok=True)

    toolchain = args.toolchain
    print(f"Configuring for {toolchain} toolchain.")

    versions: Dict[str, str] = {}
    if toolchain == 'node':
        node_version = get_latest_node_version()
        if node_version:
            versions['node'] = node_version
            versions['npm'] = 'latest'
    elif toolchain == 'python':
        python_version = get_latest_python_version()
        if python_version:
            versions['python'] = python_version
    elif toolchain == 'swift':
        swift_version = get_latest_swift_version()
        if swift_version:
            versions['swift'] = swift_version

    if not versions:
        print("Could not determine latest versions. Exiting.", file=sys.stderr)
        sys.exit(1)

    create_gitignore(repo_path, toolchain)
    create_mise_toml(repo_path, toolchain, versions)
    create_version_instructions(repo_path, toolchain)
    trust_mise_config(repo_path)

    print("Repository configuration complete.")


if __name__ == "__main__":
    main()
