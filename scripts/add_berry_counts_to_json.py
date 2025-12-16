#!/usr/bin/env python3
"""
Add berry count information from contrib/berries/ to JSON annotations.
Reads berry center point coordinates and adds berry_count field to JSON files.
"""

import json
import os
from pathlib import Path


def count_berries_from_file(berry_file_path):
    """Count berries from a berry annotation file."""
    if not berry_file_path.exists():
        return 0
    
    try:
        with open(berry_file_path, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
        return len(lines)
    except Exception as e:
        print(f"Error reading {berry_file_path}: {e}")
        return 0


def add_berry_count_to_json(json_path, berry_count):
    """Add berry_count field to JSON annotation file."""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Add berry_count to image info
        if 'images' in data and len(data['images']) > 0:
            if 'berry_count' not in data['images'][0]:
                data['images'][0]['berry_count'] = berry_count
            else:
                # Update if exists
                data['images'][0]['berry_count'] = berry_count
        
        # Also add to info section for reference
        if 'info' in data:
            if 'berry_count' not in data['info']:
                data['info']['berry_count'] = berry_count
        
        # Write back
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        print(f"Error updating {json_path}: {e}")
        return False


def main():
    """Add berry counts to all JSON annotation files."""
    root_dir = Path(__file__).parent.parent
    contrib_berries_dir = root_dir / 'contrib' / 'berries'
    json_dir = root_dir / 'grapes' / 'json'
    
    updated = 0
    skipped = 0
    not_found = 0
    
    # Process all JSON files
    for json_file in json_dir.glob('*.json'):
        stem = json_file.stem
        
        # Find corresponding berry file
        berry_file = contrib_berries_dir / f"{stem}-berries.txt"
        
        if berry_file.exists():
            berry_count = count_berries_from_file(berry_file)
            if add_berry_count_to_json(json_file, berry_count):
                updated += 1
                if updated % 50 == 0:
                    print(f"Updated {updated} files...")
            else:
                skipped += 1
        else:
            not_found += 1
    
    print(f"\nSummary:")
    print(f"  Updated: {updated} files")
    print(f"  Skipped: {skipped} files")
    print(f"  Berry file not found: {not_found} files")
    print(f"\nBerry count information has been added to JSON annotations.")


if __name__ == '__main__':
    main()

