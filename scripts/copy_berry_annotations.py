#!/usr/bin/env python3
"""
Copy berry annotation files from contrib/berries/ to grapes/, high_resolution/, and video_frames/.
Creates berries/ subdirectory in each dataset directory with the same structure.
"""

import shutil
from pathlib import Path


def copy_berry_annotations(source_dir, target_dirs, image_dirs):
    """
    Copy berry annotation files to target directories.
    
    Args:
        source_dir: Path to contrib/berries/ directory
        target_dirs: List of target dataset directories (grapes, high_resolution, video_frames)
        image_dirs: List of corresponding image directories
    """
    source_berries = Path(source_dir)
    
    for target_dir, image_dir in zip(target_dirs, image_dirs):
        target_path = Path(target_dir)
        image_path = Path(image_dir)
        
        # Create berries subdirectory
        berries_dir = target_path / 'berries'
        berries_dir.mkdir(parents=True, exist_ok=True)
        
        # Get list of images in this dataset
        image_stems = set()
        for img_file in image_path.glob('*.jpg'):
            stem = img_file.stem
            image_stems.add(stem)
        
        # Copy matching berry annotation files
        copied = 0
        for berry_file in source_berries.glob('*-berries.txt'):
            # Extract image stem from filename (e.g., CDY_2015-berries.txt -> CDY_2015)
            berry_stem = berry_file.stem.replace('-berries', '')
            
            if berry_stem in image_stems:
                dest_file = berries_dir / berry_file.name
                shutil.copy2(berry_file, dest_file)
                copied += 1
        
        print(f"{target_dir}: Copied {copied} berry annotation files")


def main():
    """Copy berry annotations to all three dataset directories."""
    root_dir = Path(__file__).parent.parent
    
    source_berries = root_dir / 'contrib' / 'berries'
    
    target_dirs = [
        root_dir / 'grapes',
        root_dir / 'high_resolution',
        root_dir / 'video_frames'
    ]
    
    image_dirs = [
        root_dir / 'grapes' / 'images',
        root_dir / 'high_resolution' / 'images',
        root_dir / 'video_frames' / 'images'
    ]
    
    print("Copying berry annotations from contrib/berries/ to dataset directories...")
    copy_berry_annotations(source_berries, target_dirs, image_dirs)
    
    print("\nSummary:")
    for target_dir in target_dirs:
        berries_dir = target_dir / 'berries'
        if berries_dir.exists():
            count = len(list(berries_dir.glob('*.txt')))
            print(f"  {target_dir}/berries/: {count} files")


if __name__ == '__main__':
    main()




