#!/usr/bin/env python3
"""
Convert NPZ segmentation masks to PNG format.

The NPZ files contain multi-channel segmentation masks (24 channels).
This script converts them to PNG format for use in segmentation tasks.
Each channel represents a different instance mask.
"""

import numpy as np
from PIL import Image
from pathlib import Path


def convert_npz_to_png(npz_path: Path, png_path: Path, method: str = "merge"):
    """
    Convert NPZ segmentation mask to PNG.
    
    Args:
        npz_path: Path to input NPZ file
        png_path: Path to output PNG file
        method: Conversion method
            - "merge": Merge all channels into a single mask (union)
            - "first": Use only the first channel
            - "max": Use channel with maximum area
    """
    try:
        data = np.load(npz_path)
        mask_array = data['arr_0']  # Shape: (height, width, channels)
        
        if method == "merge":
            # Merge all channels: if any channel has value 1, set pixel to 1
            merged_mask = np.max(mask_array, axis=2).astype(np.uint8) * 255
        elif method == "first":
            # Use first channel only
            merged_mask = mask_array[:, :, 0].astype(np.uint8) * 255
        elif method == "max":
            # Use channel with maximum area
            channel_areas = np.sum(mask_array, axis=(0, 1))
            max_channel_idx = np.argmax(channel_areas)
            merged_mask = mask_array[:, :, max_channel_idx].astype(np.uint8) * 255
        else:
            raise ValueError(f"Unknown method: {method}")
        
        # Create PIL Image and save
        img = Image.fromarray(merged_mask, mode='L')
        png_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(png_path)
        return True
    except Exception as e:
        print(f"Error converting {npz_path}: {e}")
        return False


def main():
    """Convert all NPZ files to PNG format."""
    root_dir = Path(__file__).parent.parent
    origin_dir = root_dir / 'data' / 'origin'
    segmentations_dir = root_dir / 'grapes' / 'segmentations'
    
    segmentations_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all NPZ files
    npz_files = list(origin_dir.glob('*.npz'))
    
    print(f"Found {len(npz_files)} NPZ files")
    
    converted = 0
    skipped = 0
    
    for npz_path in npz_files:
        # Get corresponding image stem
        stem = npz_path.stem
        png_path = segmentations_dir / f"{stem}.png"
        
        if convert_npz_to_png(npz_path, png_path, method="merge"):
            converted += 1
        else:
            skipped += 1
    
    print(f"Converted {converted} files, skipped {skipped} files")
    print(f"Segmentation masks saved to: {segmentations_dir}")


if __name__ == '__main__':
    main()

