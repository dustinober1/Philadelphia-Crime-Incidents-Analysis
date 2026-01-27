#!/usr/bin/env python3
"""
Script to remove all .pyc files and __pycache__ directories from the project.

This utility helps clean up Python bytecode files that can accumulate during
development and cause issues with imports or version control.
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple


def find_pyc_files_and_cache_dirs(root_dir: Path) -> Tuple[List[Path], List[Path]]:
    """
    Find all .pyc files and __pycache__ directories in the given directory tree.
    
    Args:
        root_dir: The root directory to search in
        
    Returns:
        Tuple of (pyc_files, cache_dirs)
    """
    pyc_files = []
    cache_dirs = []
    
    for root, dirs, files in os.walk(root_dir):
        # Check for __pycache__ directories
        if '__pycache__' in dirs:
            cache_dirs.append(Path(root) / '__pycache__')
            # Remove __pycache__ from dirs to prevent walking into it
            dirs.remove('__pycache__')
        
        # Check for .pyc files
        for file in files:
            if file.endswith('.pyc'):
                pyc_files.append(Path(root) / file)
    
    return pyc_files, cache_dirs


def remove_files_and_dirs(pyc_files: List[Path], cache_dirs: List[Path]) -> Tuple[int, int]:
    """
    Remove all .pyc files and __pycache__ directories.
    
    Args:
        pyc_files: List of .pyc files to remove
        cache_dirs: List of __pycache__ directories to remove
        
    Returns:
        Tuple of (files_removed, dirs_removed)
    """
    files_removed = 0
    dirs_removed = 0
    
    # Remove .pyc files
    for pyc_file in pyc_files:
        try:
            pyc_file.unlink()
            print(f"Removed: {pyc_file}")
            files_removed += 1
        except Exception as e:
            print(f"Error removing {pyc_file}: {e}")
    
    # Remove __pycache__ directories
    for cache_dir in cache_dirs:
        try:
            # Remove all contents of the cache directory first
            for item in cache_dir.iterdir():
                item.unlink()
            cache_dir.rmdir()
            print(f"Removed: {cache_dir}")
            dirs_removed += 1
        except Exception as e:
            print(f"Error removing {cache_dir}: {e}")
    
    return files_removed, dirs_removed


def main():
    """Main function to clean .pyc files and __pycache__ directories."""
    # Get the project root directory (two levels up from this script)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    
    print(f"Cleaning .pyc files and __pycache__ directories in: {project_root}")
    print("-" * 60)
    
    # Find all .pyc files and __pycache__ directories
    pyc_files, cache_dirs = find_pyc_files_and_cache_dirs(project_root)
    
    if not pyc_files and not cache_dirs:
        print("No .pyc files or __pycache__ directories found.")
        return
    
    print(f"Found {len(pyc_files)} .pyc files and {len(cache_dirs)} __pycache__ directories")
    print("\nFiles and directories to be removed:")
    
    for pyc_file in pyc_files:
        print(f"  {pyc_file}")
    for cache_dir in cache_dirs:
        print(f"  {cache_dir}")
    
    print("\nRemoving files...")
    
    # Remove the files and directories
    files_removed, dirs_removed = remove_files_and_dirs(pyc_files, cache_dirs)
    
    print("-" * 60)
    print(f"Cleanup complete!")
    print(f"Files removed: {files_removed}")
    print(f"Directories removed: {dirs_removed}")


if __name__ == "__main__":
    main()