#!/usr/bin/env python3
"""
Organize video demo frames into standardized structure under grapes/video_frames/.
Creates the same directory structure as grapes/ but for video frames.
"""

import os
import shutil
from pathlib import Path
from PIL import Image


def create_empty_csv(csv_path, image_name):
    """Create an empty CSV annotation file."""
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with open(csv_path, 'w') as f:
        f.write('#item,x,y,width,height,label\n')


def create_empty_json(json_path, image_path, image_name):
    """Create an empty JSON annotation file."""
    json_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Get image dimensions
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            file_size = os.path.getsize(image_path)
    except Exception as e:
        print(f"Error reading image {image_path}: {e}")
        width, height = 1920, 1080  # Default
        file_size = 0
    
    json_data = {
        "info": {
            "description": "Video demo frame annotation",
            "version": "1.0",
            "year": 2025,
            "contributor": "Embrapa WGISD Dataset",
            "source": "Video demo frames",
            "license": {
                "name": "Creative Commons Attribution 4.0 International",
                "url": "https://creativecommons.org/licenses/by/4.0/"
            },
            "berry_count": 0
        },
        "images": [
            {
                "id": hash(image_name) % 10000000000,  # Generate unique ID
                "width": width,
                "height": height,
                "file_name": image_name,
                "size": file_size,
                "format": "JPG",
                "url": "",
                "hash": "",
                "status": "success",
                "source": "video_demo",
                "berry_count": 0
            }
        ],
        "annotations": [],
        "categories": [
            {
                "id": 0,
                "name": "background",
                "supercategory": "background"
            },
            {
                "id": 1,
                "name": "grape",
                "supercategory": "fruit"
            }
        ]
    }
    
    import json
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)


def main():
    """Organize video frames into standardized structure."""
    root_dir = Path(__file__).parent.parent
    video_frames_source = root_dir / 'extra' / 'video_demo_frames'
    video_frames_dest = root_dir / 'grapes' / 'video_frames'
    
    # Create directory structure
    images_dir = video_frames_dest / 'images'
    csv_dir = video_frames_dest / 'csv'
    json_dir = video_frames_dest / 'json'
    sets_dir = video_frames_dest / 'sets'
    
    images_dir.mkdir(parents=True, exist_ok=True)
    csv_dir.mkdir(parents=True, exist_ok=True)
    json_dir.mkdir(parents=True, exist_ok=True)
    sets_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy images and create empty annotations
    video_frame_files = sorted(video_frames_source.glob('*.jpg'))
    
    print(f"Found {len(video_frame_files)} video frame images")
    
    copied = 0
    for img_file in video_frame_files:
        stem = img_file.stem  # e.g., "frame-00001"
        dest_img = images_dir / img_file.name
        
        # Copy image
        if not dest_img.exists():
            shutil.copy2(img_file, dest_img)
        
        # Create empty CSV
        csv_file = csv_dir / f"{stem}.csv"
        if not csv_file.exists():
            create_empty_csv(csv_file, img_file.name)
        
        # Create empty JSON
        json_file = json_dir / f"{stem}.json"
        if not json_file.exists():
            create_empty_json(json_file, dest_img, img_file.name)
        
        copied += 1
        if copied % 50 == 0:
            print(f"Processed {copied} frames...")
    
    # Create labelmap.json
    labelmap_file = video_frames_dest / 'labelmap.json'
    if not labelmap_file.exists():
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
        import json
        with open(labelmap_file, 'w', encoding='utf-8') as f:
            json.dump(labelmap_data, f, indent=2, ensure_ascii=False)
    
    # Create sets files (all frames in all.txt, can be split later)
    all_frames = sorted([f.stem for f in video_frame_files])
    with open(sets_dir / 'all.txt', 'w') as f:
        for frame in all_frames:
            f.write(f"{frame}\n")
    
    print(f"\nSummary:")
    print(f"  Processed: {copied} video frames")
    print(f"  Images: {images_dir}")
    print(f"  CSV annotations: {csv_dir} (empty, ready for annotation)")
    print(f"  JSON annotations: {json_dir} (empty, ready for annotation)")
    print(f"  Sets: {sets_dir}")
    print(f"\nVideo frames structure created at: {video_frames_dest}")
    print("Note: Annotation files are empty and ready for manual annotation.")


if __name__ == '__main__':
    main()

