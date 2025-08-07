import json
import os
import re
import subprocess

import requests
from rich.console import Console

console = Console()

PATCHES_BASE_URL = "https://raw.githubusercontent.com/yoursteacup/skeletone/main/patches/"

def get_all_patch_names():
    """
    Fetching patches names with GitHub API
    """
    api_url = "https://api.github.com/repos/yoursteacup/skeletone/contents/patches"
    r = requests.get(api_url)
    if r.status_code != 200:
        raise Exception(f"Could not fetch patches list: {r.text}")
    files = r.json()
    patch_names = [f["name"] for f in files if f["name"].endswith(".patch")]
    return sorted(patch_names)

def build_patch_chain(cur_ver, patch_names):
    chain = []
    while True:
        found = False
        for fname in patch_names:
            m = re.match(rf"{re.escape(cur_ver)}_to_(v[\d\.]+)\.patch$", fname)
            if m:
                next_ver = m.group(1)
                chain.append((fname, next_ver))
                cur_ver = next_ver
                found = True
                break
        if not found:
            break
    return chain

def check_git_status():
    """Check if working directory is clean and suitable for patching"""
    # Check if we're in a git repository
    result = subprocess.run(["git", "rev-parse", "--git-dir"], 
                          capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception("Not in a git repository. Patches require git.")
    
    # Check for uncommitted changes
    result = subprocess.run(["git", "status", "--porcelain"], 
                          capture_output=True, text=True)
    if result.stdout.strip():
        console.print("[bold yellow]⚠️  Warning: You have uncommitted changes.[/bold yellow]")
        console.print("Applying patches may fail or produce unexpected results.")
        console.print("Consider committing or stashing your changes first.")
        return False
    return True

def filter_patch_content(patch_content):
    """Remove make_diff.sh and other unnecessary files from patch"""
    lines = patch_content.split('\n')
    filtered_lines = []
    skip_section = False
    
    for i, line in enumerate(lines):
        # Check if this is a new file section
        if line.startswith('diff --git'):
            # Check if this section is for make_diff.sh
            if 'make_diff.sh' in line:
                skip_section = True
                # Find the next diff section or end of file
                for j in range(i + 1, len(lines)):
                    if lines[j].startswith('diff --git') or j == len(lines) - 1:
                        break
                continue
            else:
                skip_section = False
        
        if not skip_section:
            filtered_lines.append(line)
    
    return '\n'.join(filtered_lines)

def download_and_apply_patch(patch_name):
    url = PATCHES_BASE_URL + patch_name
    console.print(f"[bold green]⬇ Downloading patch: {url}[/bold green]")
    r = requests.get(url)
    if r.status_code != 200:
        raise Exception(f"Can't download patch {patch_name}: HTTP {r.status_code}")
    
    # Filter out make_diff.sh from patch
    patch_content = r.text
    filtered_content = filter_patch_content(patch_content)
    
    patch_file = "tmp_skeletone_upgrade.patch"
    with open(patch_file, "w") as f:
        f.write(filtered_content)
    
    # First, try a dry run to check if patch can be applied
    dry_run = subprocess.run(["git", "apply", "--check", "--whitespace=nowarn", patch_file],
                             capture_output=True, text=True)
    
    if dry_run.returncode != 0:
        # Try to get more detailed error information
        verbose_check = subprocess.run(["git", "apply", "--check", "-v", patch_file],
                                       capture_output=True, text=True)
        os.remove(patch_file)
        error_msg = f"❌ Patch {patch_name} cannot be applied cleanly.\n"
        error_msg += f"Error: {dry_run.stderr.strip()}\n"
        if verbose_check.stderr:
            error_msg += f"Details: {verbose_check.stderr.strip()}"
        raise Exception(error_msg)
    
    # Apply the patch
    result = subprocess.run(["git", "apply", "--whitespace=nowarn", patch_file],
                            capture_output=True, text=True)
    os.remove(patch_file)
    
    if result.returncode != 0:
        error_msg = f"❌ Failed to apply patch {patch_name}.\n"
        error_msg += f"stdout: {result.stdout.strip()}\n" if result.stdout else ""
        error_msg += f"stderr: {result.stderr.strip()}" if result.stderr else ""
        raise Exception(error_msg)

def upgrade_skeletone():
    console.print("[bold green]Running upgrade...[/bold green]")
    
    # Check git status before proceeding
    check_git_status()
    
    with open("skeletone.lock") as f:
        lock = json.load(f)
    cur_ver = lock["template_version"]

    patch_names = get_all_patch_names()
    chain = build_patch_chain(cur_ver, patch_names)

    if not chain:
        console.print("[bold green]No patches required[/bold green]")
        return

    console.print(f"[bold blue]Found {len(chain)} patch(es) to apply:[/bold blue]")
    for patch_name, next_ver in chain:
        console.print(f"  • {patch_name} → {next_ver}")
    
    for patch_name, next_ver in chain:
        console.print(f"[bold green]⏩ Applying patch: {patch_name}[/bold green]")
        try:
            download_and_apply_patch(patch_name)
            lock["template_version"] = next_ver
            with open("skeletone.lock", "w") as f:
                json.dump(lock, f, indent=2)
            console.print(f"[bold green]✅ Patched to version {next_ver}[/bold green]")
        except Exception as e:
            console.print(f"[bold red]❌ Failed to apply patch {patch_name}[/bold red]")
            console.print(f"[red]{str(e)}[/red]")
            console.print("\n[yellow]Troubleshooting tips:[/yellow]")
            console.print("1. Check if you have uncommitted changes: git status")
            console.print("2. Try stashing changes: git stash")
            console.print("3. Check if files were modified: git diff")
            console.print("4. Try resetting to clean state: git reset --hard (⚠️  destructive)")
            raise

    console.print("[bold green]Patch complete[/bold green]")
