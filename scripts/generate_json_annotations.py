import os
import json
import random
import time
from pathlib import Path

def generate_unique_id():
    """Generate unique ID with 7 random digits and 3 timestamp digits"""
    random_part = random.randint(1000000, 9999999)
    timestamp_part = int(time.time()) % 1000
    return int(f"{random_part}{timestamp_part:03d}")

def parse_yolo_annotation(txt_file_path, image_width, image_height):
    """Parse YOLO format annotation file"""
    annotations = []
    
    if not os.path.exists(txt_file_path):
        return annotations
    
    try:
        with open(txt_file_path, 'r') as f:
            lines = f.readlines()
        
        for line_num, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            parts = line.split()
            if len(parts) >= 5:
                category_id = int(parts[0]) + 1  # YOLO starts from 0, we change to start from 1
                center_x = float(parts[1])
                center_y = float(parts[2])
                width = float(parts[3])
                height = float(parts[4])
                
                # Convert to absolute coordinates
                x = int((center_x - width/2) * image_width)
                y = int((center_y - height/2) * image_height)
                w = int(width * image_width)
                h = int(height * image_height)
                
                # Ensure coordinates are within image bounds
                x = max(0, min(x, image_width - 1))
                y = max(0, min(y, image_height - 1))
                w = min(w, image_width - x)
                h = min(h, image_height - y)
                
                annotation = {
                    "id": generate_unique_id(),
                    "image_id": 0,  # Will be set later
                    "category_id": category_id,
                    "bbox": [x, y, w, h],
                    "area": w * h,
                    "iscrowd": 0
                }
                annotations.append(annotation)
                
    except Exception as e:
        print(f"Error parsing {txt_file_path}: {e}")
    
    return annotations

def get_image_info(image_path):
    """Get image information"""
    # Here we use fixed dimensions, in real applications you can use PIL or other libraries to get actual dimensions
    # According to README, these images have different sizes
    file_size = os.path.getsize(image_path)
    
    # Determine variety based on filename
    filename = os.path.basename(image_path)
    variety_map = {
        'CDY': 'Chardonnay',
        'CFR': 'Cabernet Franc', 
        'CSV': 'Cabernet Sauvignon',
        'SVB': 'Sauvignon Blanc',
        'SYH': 'Syrah'
    }
    
    variety = None
    for prefix, name in variety_map.items():
        if filename.startswith(prefix):
            variety = name
            break
    
    # Set default dimensions based on variety (these are estimates, actual should be obtained from images)
    default_sizes = {
        'Chardonnay': (1920, 1080),
        'Cabernet Franc': (1920, 1080),
        'Cabernet Sauvignon': (1920, 1080), 
        'Sauvignon Blanc': (1920, 1080),
        'Syrah': (1920, 1080)
    }
    
    width, height = default_sizes.get(variety, (1920, 1080))
    
    return {
        'width': width,
        'height': height,
        'file_size': file_size,
        'variety': variety
    }

def generate_json_annotation(image_path, output_dir):
    """Generate JSON annotation file for a single image"""
    # Get image information
    image_info = get_image_info(image_path)
    
    # Generate image ID
    image_id = generate_unique_id()
    
    # Build image data
    image_data = {
        "id": image_id,
        "width": image_info['width'],
        "height": image_info['height'],
        "file_name": os.path.basename(image_path),
        "size": image_info['file_size'],
        "format": "JPG",
        "url": "",
        "hash": "",
        "status": "success",
        "variety": image_info['variety']
    }
    
    # Parse corresponding annotation file
    txt_path = image_path.replace('.jpg', '.txt')
    annotations = parse_yolo_annotation(txt_path, image_info['width'], image_info['height'])
    
    # Set correct image_id for each annotation
    for ann in annotations:
        ann['image_id'] = image_id
    
    # Build complete JSON structure
    json_data = {
        "info": {
            "description": f"Grape detection annotation for {image_info['variety']} variety",
            "version": "1.0",
            "year": 2025,
            "contributor": "Embrapa WGISD Dataset",
            "source": "Field captured grape images",
            "license": {
                "name": "Creative Commons Attribution 4.0 International",
                "url": "https://creativecommons.org/licenses/by/4.0/"
            }
        },
        "images": [image_data],
        "annotations": annotations,
        "categories": [
            {
                "id": 1,
                "name": "GRAPE_CLUSTER",
                "supercategory": "GRAPE"
            }
        ]
    }
    
    # Generate output filename
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    output_path = os.path.join(output_dir, f"{base_name}.json")
    
    # Write JSON file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    
    return output_path

def main():
    """Main function"""
    # Set paths
    data_dir = "data"
    output_dir = "data"  # Output to same directory
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all jpg images
    image_files = [f for f in os.listdir(data_dir) if f.lower().endswith('.jpg')]
    
    print(f"Found {len(image_files)} images to process...")
    
    # Generate JSON annotations for each image
    for i, image_file in enumerate(image_files):
        image_path = os.path.join(data_dir, image_file)
        
        try:
            output_path = generate_json_annotation(image_path, output_dir)
            print(f"[{i+1}/{len(image_files)}] Generated: {output_path}")
        except Exception as e:
            print(f"Error processing {image_file}: {e}")
    
    print(f"\nCompleted! Generated {len(image_files)} JSON annotation files.")

if __name__ == "__main__":
    main() 