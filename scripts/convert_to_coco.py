#!/usr/bin/env python3
"""Convert WGISD annotations to COCO JSON format.

This script converts per-image CSV annotations in the WGISD dataset
into COCO-style JSON files for train/val/test splits.

Usage examples:
    python scripts/convert_to_coco.py --root . --out annotations --splits train val test
"""

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence

from PIL import Image


def _read_split_list(split_file: Path) -> List[str]:
    """Read image base names (without extension) from a split file."""
    if not split_file.exists():
        return []
    lines = [line.strip() for line in split_file.read_text(encoding="utf-8").splitlines()]
    return [line for line in lines if line]


def _image_size(image_path: Path) -> tuple[int, int]:
    """Return (width, height) for an image path using PIL."""
    with Image.open(image_path) as img:
        return img.width, img.height


def _parse_csv_boxes(csv_path: Path) -> List[Dict[str, float]]:
    """Parse a single per-image CSV file and return COCO-style bboxes."""
    if not csv_path.exists():
        return []
    
    boxes: List[Dict[str, float]] = []
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            return boxes
        
        # Normalize header keys to lowercase
        header_lower = {k.lower(): k for k in reader.fieldnames}
        
        for row in reader:
            # Normalize row keys
            row_lower = {k.lower(): v for k, v in row.items()}
            
            # Get coordinates (support various column name variants)
            def get(key_variants: List[str]) -> Optional[float]:
                for key in key_variants:
                    if key in row_lower and row_lower[key] not in (None, ""):
                        try:
                            return float(row_lower[key])
                        except ValueError:
                            continue
                return None
            
            x = get(["x", "xc", "x_center"])
            y = get(["y", "yc", "y_center"])
            w = get(["w", "width", "dx"])
            h = get(["h", "height", "dy"])
            
            if x is not None and y is not None and w is not None and h is not None:
                boxes.append({
                    "x": x,
                    "y": y,
                    "width": w,
                    "height": h
                })
    
    return boxes


def _collect_annotations_for_split(
    category_root: Path,
    split: str,
) -> tuple[List[Dict[str, object]], List[Dict[str, object]], List[Dict[str, object]]]:
    """Collect COCO dictionaries for images, annotations, and categories."""
    images_dir = category_root / "images"
    annotations_dir = category_root / "csv"
    sets_dir = category_root / "sets"
    
    split_file = sets_dir / f"{split}.txt"
    image_stems = set(_read_split_list(split_file))
    if not image_stems:
        # If no split list is provided, fall back to all images
        image_stems = {p.stem for p in images_dir.glob("*.jpg")}
        image_stems.update({p.stem for p in images_dir.glob("*.png")})
    
    images: List[Dict[str, object]] = []
    anns: List[Dict[str, object]] = []
    categories: List[Dict[str, object]] = [
        {"id": 1, "name": "grape", "supercategory": "fruit"}
    ]
    
    image_id_counter = 1
    ann_id_counter = 1
    
    for stem in sorted(image_stems):
        # Try to find image file (jpg or png)
        img_path = images_dir / f"{stem}.jpg"
        if not img_path.exists():
            img_path = images_dir / f"{stem}.png"
            if not img_path.exists():
                continue
        
        width, height = _image_size(img_path)
        images.append({
            "id": image_id_counter,
            "file_name": str(img_path.relative_to(category_root.parent)),
            "width": width,
            "height": height,
        })
        
        csv_path = annotations_dir / f"{stem}.csv"
        for box in _parse_csv_boxes(csv_path):
            anns.append({
                "id": ann_id_counter,
                "image_id": image_id_counter,
                "category_id": 1,
                "bbox": [box["x"], box["y"], box["width"], box["height"]],
                "area": box["width"] * box["height"],
                "iscrowd": 0,
            })
            ann_id_counter += 1
        
        image_id_counter += 1
    
    return images, anns, categories


def _build_coco_dict(
    images: List[Dict[str, object]],
    anns: List[Dict[str, object]],
    categories: List[Dict[str, object]],
    description: str,
) -> Dict[str, object]:
    """Build a complete COCO dict from components."""
    return {
        "info": {
            "year": 2025,
            "version": "1.0.0",
            "description": description,
            "url": "https://github.com/thsant/wgisd",
        },
        "images": images,
        "annotations": anns,
        "categories": categories,
        "licenses": [],
    }


def convert(
    root: Path,
    out_dir: Path,
    category: str,
    splits: Sequence[str],
) -> None:
    """Convert selected splits to COCO JSON files."""
    out_dir.mkdir(parents=True, exist_ok=True)
    
    category_root = root / category
    
    for split in splits:
        images, anns, categories = _collect_annotations_for_split(category_root, split)
        desc = f"WGISD {category} {split} split"
        coco = _build_coco_dict(images, anns, categories, desc)
        out_path = out_dir / f"{category}_instances_{split}.json"
        out_path.write_text(json.dumps(coco, indent=2), encoding="utf-8")
        print(f"Generated {out_path} with {len(images)} images and {len(anns)} annotations")


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Entry point for the converter CLI."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="Dataset root containing category subfolder (default: dataset root)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "annotations",
        help="Output directory for COCO JSON files (default: <root>/annotations)",
    )
    parser.add_argument(
        "--category",
        type=str,
        default="grapes",
        help="Category name (default: grapes)",
    )
    parser.add_argument(
        "--splits",
        nargs="+",
        type=str,
        default=["train", "val", "test"],
        choices=["train", "val", "test"],
        help="Dataset splits to generate (default: train val test)",
    )
    
    args = parser.parse_args(argv)
    
    convert(
        root=Path(args.root),
        out_dir=Path(args.out),
        category=args.category,
        splits=args.splits,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

