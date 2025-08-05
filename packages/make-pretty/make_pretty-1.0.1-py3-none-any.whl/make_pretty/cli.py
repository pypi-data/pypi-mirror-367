#!/usr/bin/env python3
import os
import subprocess
import sys
from pathlib import Path

def run_command(command, cwd=None):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd, 
            capture_output=True, 
            text=True,
            check=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, f"Error: {e.stderr}"

def process_python_file(file_path):
    """Process a single Python file with the specified commands"""
    print(f"Processing: {file_path}")
    
    # Command 1: isort
    print(f"  Running isort on {file_path}...")
    success, output = run_command(f"isort '{file_path}'")
    if not success:
        print(f"    ⚠️  isort failed: {output}")
    else:
        print(f"    ✅ isort completed")
    
    # Command 2: black
    print(f"  Running black on {file_path}...")
    success, output = run_command(f"black '{file_path}'")
    if not success:
        print(f"    ⚠️  black failed: {output}")
    else:
        print(f"    ✅ black completed")
    
    print()

def main():
    """Main CLI function"""
    # Get current working directory (where command is run)
    current_dir = Path.cwd()
    print(f"Current directory: {current_dir}")
    print(f"Processing all .py files in: {current_dir}")
    print("=" * 50)
    
    # Find all Python files recursively
    python_files = list(current_dir.rglob("*.py"))
    python_files.sort()
    
    if not python_files:
        print("No Python files found to process.")
        return
    
    print(f"Found {len(python_files)} Python files to process:")
    for file_path in python_files:
        print(f"  - {file_path.relative_to(current_dir)}")
    print()
    
    # Ask for confirmation
    response = input("Do you want to proceed? (y/N): ").strip().lower()
    if response != 'y':
        print("Operation cancelled.")
        return
    
    print("\nStarting processing...")
    print("=" * 50)
    
    # Process each file
    for file_path in python_files:
        process_python_file(file_path)
    
    print("=" * 50)
    print("✅ All files processed!")

if __name__ == "__main__":
    main()
