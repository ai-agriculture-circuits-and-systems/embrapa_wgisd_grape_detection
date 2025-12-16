#!/usr/bin/env python3
"""
Reorganize datasets to have three equal-level directories:
- grapes/ (downsampled images, 2048x1365)
- video_frames/ (video demo frames)
- high_resolution/ (original high-resolution images, 5184x3456)

All three should have the same structure: csv/, json/, images/, sets/, labelmap.json
"""

import os
import shutil
import json
from pathlib import Path
from PIL import Image


def create_labelmap(dest_dir):
    """Create labelmap.json file."""
    labelmap_data = [
        {
            "object_id": 0,
            "label_id": 0,
            "keyboard_shortcut": "0",
            "object_name": "background"
        },
        {
            "object_id": 1,
            "label_id": 1,
            "keyboard_shortcut": "1",
            "object_name": "grape"
        }
    ]
    labelmap_file = dest_dir / 'labelmap.json'
    with open(labelmap_file, 'w', encoding='utf-8') as f:
        json.dump(labelmap_data, f, indent=2, ensure_ascii=False)


def copy_annotation_structure(source_dir, dest_dir, image_source_dir):
    """Copy annotation structure from source to destination."""
    # Create directories
    csv_dir = dest_dir / 'csv'
    json_dir = dest_dir / 'json'
    images_dir = dest_dir / 'images'
    sets_dir = dest_dir / 'sets'
    
    csv_dir.mkdir(parents=True, exist_ok=True)
    json_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)
    sets_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy CSV files
    source_csv = source_dir / 'csv'
    if source_csv.exists():
        for csv_file in source_csv.glob('*.csv'):
            shutil.copy2(csv_file, csv_dir / csv_file.name)
    
    # Copy JSON files
    source_json = source_dir / 'json'
    if source_json.exists():
        for json_file in source_json.glob('*.json'):
            shutil.copy2(json_file, json_dir / json_file.name)
    
    # Copy images
    if image_source_dir.exists():
        for img_file in image_source_dir.glob('*.jpg'):
            shutil.copy2(img_file, images_dir / img_file.name)
    
    # Copy sets files
    source_sets = source_dir / 'sets'
    if source_sets.exists():
        for sets_file in source_sets.glob('*.txt'):
            shutil.copy2(sets_file, sets_dir / sets_file.name)
    
    # Create labelmap
    create_labelmap(dest_dir)


def main():
    """Reorganize datasets."""
    root_dir = Path(__file__).parent.parent
    
    # 1. Move video_frames from grapes/video_frames/ to root level
    print("Moving video_frames to root level...")
    video_frames_source = root_dir / 'grapes' / 'video_frames'
    video_frames_dest = root_dir / 'video_frames'
    
    if video_frames_source.exists():
        if video_frames_dest.exists():
            shutil.rmtree(video_frames_dest)
        shutil.move(str(video_frames_source), str(video_frames_dest))
        print(f"  Moved {video_frames_source} -> {video_frames_dest}")
    
    # 2. Create high_resolution directory structure
    print("\nCreating high_resolution directory structure...")
    high_resolution_dir = root_dir / 'high_resolution'
    high_resolution_dir.mkdir(exist_ok=True)
    
    # Copy structure from grapes (as template)
    grapes_dir = root_dir / 'grapes'
    
    # Create directories
    csv_dir = high_resolution_dir / 'csv'
    json_dir = high_resolution_dir / 'json'
    images_dir = high_resolution_dir / 'images'
    sets_dir = high_resolution_dir / 'sets'
    
    csv_dir.mkdir(parents=True, exist_ok=True)
    json_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)
    sets_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy high-resolution images from data/origin
    print("  Copying high-resolution images...")
    origin_dir = root_dir / 'data' / 'origin'
    high_res_images = []
    
    for img_file in origin_dir.glob('*.jpg'):
        try:
            with Image.open(img_file) as img:
                width, height = img.size
                # Check if it's high resolution (larger than 3000x2000)
                if width > 3000 or height > 2000:
                    high_res_images.append(img_file)
                    shutil.copy2(img_file, images_dir / img_file.name)
        except Exception as e:
            print(f"    Error processing {img_file}: {e}")
    
    print(f"  Copied {len(high_res_images)} high-resolution images")
    
    # Copy CSV and JSON annotations (will need coordinate conversion later)
    print("  Copying annotation files...")
    grapes_csv = grapes_dir / 'csv'
    grapes_json = grapes_dir / 'json'
    grapes_sets = grapes_dir / 'sets'
    
    if grapes_csv.exists():
        for csv_file in grapes_csv.glob('*.csv'):
            shutil.copy2(csv_file, csv_dir / csv_file.name)
    
    if grapes_json.exists():
        for json_file in grapes_json.glob('*.json'):
            shutil.copy2(json_file, json_dir / json_file.name)
    
    if grapes_sets.exists():
        for sets_file in grapes_sets.glob('*.txt'):
            shutil.copy2(sets_file, sets_dir / sets_file.name)
    
    # Create labelmap
    create_labelmap(high_resolution_dir)
    
    print("\nSummary:")
    print(f"  grapes/ - Downsampled images (2048x1365)")
    print(f"  video_frames/ - Video demo frames (500 images)")
    print(f"  high_resolution/ - High-resolution images ({len(high_res_images)} images)")
    print("\nAll three directories now have the same structure:")
    print("  - csv/")
    print("  - json/")
    print("  - images/")
    print("  - sets/")
    print("  - labelmap.json")
    print("\nNote: High-resolution annotations need coordinate conversion (×2.53 scale)")


if __name__ == '__main__':
    main()

