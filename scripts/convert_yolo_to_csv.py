#!/usr/bin/env python3
"""
Convert YOLO format annotations to CSV format for WGISD dataset.
YOLO format: class_id center_x center_y width height (normalized)
CSV format: #item,x,y,width,height,label
"""

import os
import csv
from pathlib import Path
from PIL import Image

def yolo_to_absolute(yolo_bbox, img_width, img_height):
    """Convert YOLO format (normalized center) to absolute coordinates (top-left corner)"""
    class_id, center_x, center_y, width, height = yolo_bbox
    
    # Convert normalized to absolute
    center_x_abs = center_x * img_width
    center_y_abs = center_y * img_height
    width_abs = width * img_width
    height_abs = height * img_height
    
    # Convert center to top-left
    x = center_x_abs - width_abs / 2
    y = center_y_abs - height_abs / 2
    
    # Ensure coordinates are within image bounds
    x = max(0, min(x, img_width - 1))
    y = max(0, min(y, img_height - 1))
    width_abs = min(width_abs, img_width - x)
    height_abs = min(height_abs, img_height - y)
    
    return x, y, width_abs, height_abs, int(class_id) + 1  # YOLO starts from 0, CSV starts from 1

def convert_yolo_to_csv(yolo_file, csv_file, image_path):
    """Convert a single YOLO annotation file to CSV format"""
    # Get image dimensions
    try:
        with Image.open(image_path) as img:
            img_width, img_height = img.size
    except Exception as e:
        print(f"Warning: Could not read image {image_path}: {e}")
        return False
    
    # Read YOLO annotations
    annotations = []
    if os.path.exists(yolo_file):
        try:
            with open(yolo_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split()
                    if len(parts) >= 5:
                        yolo_bbox = [float(parts[0]), float(parts[1]), float(parts[2]), 
                                    float(parts[3]), float(parts[4])]
                        x, y, w, h, label = yolo_to_absolute(yolo_bbox, img_width, img_height)
                        annotations.append((x, y, w, h, label))
        except Exception as e:
            print(f"Error reading {yolo_file}: {e}")
            return False
    
    # Write CSV file
    try:
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['#item', 'x', 'y', 'width', 'height', 'label'])
            for idx, (x, y, w, h, label) in enumerate(annotations):
                writer.writerow([idx, x, y, w, h, label])
        return True
    except Exception as e:
        print(f"Error writing {csv_file}: {e}")
        return False

def main():
    """Convert all YOLO annotations to CSV format"""
    root_dir = Path(__file__).parent.parent
    data_dir = root_dir / 'data'
    csv_dir = root_dir / 'grapes' / 'csv'
    images_dir = root_dir / 'grapes' / 'images'
    
    csv_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all image files
    image_files = list(data_dir.glob('*.jpg')) + list(data_dir.glob('*.png'))
    
    converted = 0
    skipped = 0
    
    for image_file in image_files:
        stem = image_file.stem
        yolo_file = data_dir / f"{stem}.txt"
        csv_file = csv_dir / f"{stem}.csv"
        
        # Check if corresponding image exists in images directory
        image_in_images_dir = images_dir / image_file.name
        if not image_in_images_dir.exists():
            image_in_images_dir = image_file
        
        if convert_yolo_to_csv(yolo_file, csv_file, image_in_images_dir):
            converted += 1
        else:
            skipped += 1
    
    print(f"Converted {converted} files, skipped {skipped} files")

if __name__ == '__main__':
    main()

