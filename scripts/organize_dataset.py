#!/usr/bin/env python3
"""
Organize WGISD dataset into standardized structure.
- Move images to grapes/images/
- Move JSON annotations to grapes/json/
- Create sets/ directory with train/val/test splits
"""

import os
import shutil
from pathlib import Path

def main():
    root_dir = Path(__file__).parent.parent
    data_dir = root_dir / 'data'
    images_dir = root_dir / 'grapes' / 'images'
    json_dir = root_dir / 'grapes' / 'json'
    sets_dir = root_dir / 'grapes' / 'sets'
    
    # Create directories
    images_dir.mkdir(parents=True, exist_ok=True)
    json_dir.mkdir(parents=True, exist_ok=True)
    sets_dir.mkdir(parents=True, exist_ok=True)
    
    # Move images
    print("Moving images...")
    image_files = list(data_dir.glob('*.jpg')) + list(data_dir.glob('*.png'))
    for img_file in image_files:
        dest = images_dir / img_file.name
        if not dest.exists():
            shutil.copy2(img_file, dest)
    
    # Move JSON annotations
    print("Moving JSON annotations...")
    json_files = list(data_dir.glob('*.json'))
    for json_file in json_files:
        dest = json_dir / json_file.name
        if not dest.exists():
            shutil.copy2(json_file, dest)
    
    # Read split files and create standardized sets
    print("Creating sets files...")
    
    # Read train.txt
    train_images = set()
    if (root_dir / 'train.txt').exists():
        with open(root_dir / 'train.txt', 'r') as f:
            train_images = {line.strip() for line in f if line.strip()}
    
    # Read test.txt
    test_images = set()
    if (root_dir / 'test.txt').exists():
        with open(root_dir / 'test.txt', 'r') as f:
            test_images = {line.strip() for line in f if line.strip()}
    
    # Create validation set from train set (20% split)
    # First, get all images
    all_image_stems = {f.stem for f in image_files}
    
    # Remove test images from train set for validation split
    train_only = train_images - test_images
    
    # Split train into train and val (80/20)
    train_list = sorted(list(train_only))
    val_size = max(1, int(len(train_list) * 0.2))
    val_list = train_list[:val_size]
    train_final = train_list[val_size:]
    
    # Write sets files
    with open(sets_dir / 'train.txt', 'w') as f:
        for img in sorted(train_final):
            f.write(f"{img}\n")
    
    with open(sets_dir / 'val.txt', 'w') as f:
        for img in sorted(val_list):
            f.write(f"{img}\n")
    
    with open(sets_dir / 'test.txt', 'w') as f:
        for img in sorted(test_images):
            f.write(f"{img}\n")
    
    # Create all.txt
    all_images = sorted(list(all_image_stems))
    with open(sets_dir / 'all.txt', 'w') as f:
        for img in all_images:
            f.write(f"{img}\n")
    
    # Create train_val.txt
    train_val = sorted(train_final + val_list)
    with open(sets_dir / 'train_val.txt', 'w') as f:
        for img in train_val:
            f.write(f"{img}\n")
    
    print(f"Created sets:")
    print(f"  Train: {len(train_final)} images")
    print(f"  Val: {len(val_list)} images")
    print(f"  Test: {len(test_images)} images")
    print(f"  All: {len(all_images)} images")

if __name__ == '__main__':
    main()

