# Embrapa WGISD Grape Detection Dataset

[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/) 
[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](#changelog)

High-quality grape vineyard imagery for grape detection and instance recognition. Suitable for object detection, instance segmentation, and yield estimation experiments in viticulture applications.

- Project page: `https://github.com/thsant/wgisd`

## TL;DR
- Task: detection
- Modality: RGB 
- Platform: ground/handheld
- Real/Synthetic: real
- Images: 300 images across multiple grape varieties (Chardonnay, Cabernet Franc, Cabernet Sauvignon, Sauvignon Blanc, Syrah)
- Resolution: Variable (typically 1920×1080 or 2048×1365)
- Annotations: per-image CSV (x,y,width,height) and JSON; originally YOLO format
- License: CC BY-NC 4.0 (see License)
- Citation: see below

## Table of contents
- [Download](#download)
- [Dataset structure](#dataset-structure)
- [Sample images](#sample-images)
- [Annotation schema](#annotation-schema)
- [Stats and splits](#stats-and-splits)
- [Quick start](#quick-start)
- [Evaluation and baselines](#evaluation-and-baselines)
- [Datasheet (data card)](#datasheet-data-card)
- [Known issues and caveats](#known-issues-and-caveats)
- [Additional Documentation](#additional-documentation)
- [License](#license)
- [Citation](#citation)
- [Changelog](#changelog)
- [Contact](#contact)

## Download
- Original dataset: `https://github.com/thsant/wgisd`
- This repo hosts structure and conversion scripts only; place the downloaded folders under this directory.
- Local license file: see `LICENSE` (Creative Commons Attribution-NonCommercial 4.0).

## Dataset structure
```
embrapa_wgisd_grape_detection/
├── grapes/                    # Downsampled images dataset (2048×1365)
│   ├── berries/              # Berry center point annotations (tab-separated x y)
│   ├── csv/                   # CSV per image (x, y, width, height)
│   ├── json/                  # JSON per image
│   ├── images/                # JPG images
│   ├── segmentations/         # PNG segmentation masks (optional)
│   ├── labelmap.json
│   └── sets/                  # train.txt / val.txt / test.txt (plus all.txt, train_val.txt)
├── high_resolution/           # High-resolution images dataset (5184×3456)
│   ├── berries/              # Berry center point annotations
│   ├── csv/                   # CSV annotations (needs coordinate scaling)
│   ├── json/                  # JSON annotations
│   ├── images/                # High-resolution JPG images
│   ├── labelmap.json
│   └── sets/                  # Dataset split files
├── video_frames/              # Video demo frames dataset
│   ├── berries/              # Berry annotations (empty, ready for annotation)
│   ├── csv/                   # CSV annotations (empty, ready for annotation)
│   ├── json/                  # JSON annotations
│   ├── images/                # Video frame images
│   ├── labelmap.json
│   └── sets/                  # Dataset split files
├── annotations/               # COCO JSON output (generated)
│   ├── grapes_instances_train.json
│   ├── grapes_instances_val.json
│   └── grapes_instances_test.json
├── scripts/
│   ├── convert_to_coco.py     # CSV to COCO conversion utility
│   ├── convert_yolo_to_csv.py # YOLO to CSV conversion utility
│   ├── organize_dataset.py    # Dataset organization script
│   ├── add_berry_counts_to_json.py  # Add berry counts to JSON
│   ├── organize_video_frames.py      # Organize video frames
│   ├── copy_berry_annotations.py     # Copy berry annotations
│   └── reorganize_datasets.py        # Reorganize datasets
├── data/
│   └── origin/                # Original data directory (preserved)
│       ├── *.jpg              # Original image files (high-resolution)
│       ├── *.txt              # Original YOLO format annotations
│       ├── *.npz              # Original segmentation masks
│       ├── *_berries.txt      # Berry center point coordinates (for counting/keypoint detection)
│       ├── *_masked.txt       # List of images with segmentation masks
│       ├── contrib/           # Contrib data directory
│       │   └── berries/       # Berry annotation files (tab-separated x y coordinates)
│       └── video_demo_frames/ # Video demo frames (500 images)
├── LICENSE
├── README.md
└── requirements.txt
```
- Splits: `grapes/sets/train.txt`, `grapes/sets/val.txt`, `grapes/sets/test.txt` (and also `all.txt`, `train_val.txt`) list image basenames (no extension). If missing, all images are used.

## Sample images

Below are example images from the dataset. Paths are relative to this README location.

<table>
  <tr>
    <th>Category</th>
    <th>Sample</th>
  </tr>
  <tr>
    <td><strong>Grape</strong></td>
    <td>
      <img src="grapes/images/CDY_2015.jpg" alt="Grape example" width="260"/>
      <div align="center"><code>grapes/images/CDY_2015.jpg</code></div>
    </td>
  </tr>
</table>

## Annotation schema
- CSV per-image schema (stored under `grapes/csv/` folder):
  - Columns: `#item, x, y, width, height, label`
  - Coordinates are in absolute pixels (top-left corner format)
  - Label: 1 for grape (background is 0)
- COCO-style (generated):
```json
{
  "info": {"year": 2025, "version": "1.0.0", "description": "WGISD grapes <split>", "url": "https://github.com/thsant/wgisd"},
  "images": [{"id": 1, "file_name": "grapes/images/CDY_2015.jpg", "width": 1920, "height": 1080}],
  "categories": [{"id": 1, "name": "grape", "supercategory": "fruit"}],
  "annotations": [{"id": 10, "image_id": 1, "category_id": 1, "bbox": [x, y, w, h], "area": 1234, "iscrowd": 0}]
}
```

- Label maps: `grapes/labelmap.json` defines the category mapping:
  - `object_id: 0` = background
  - `object_id: 1` = grape

## Stats and splits
- Total images: 300
- Train: 194 images (2,947 annotations)
- Val: 48 images (633 annotations)
- Test: 58 images (850 annotations)
- Splits provided via `grapes/sets/*.txt`. You may define your own splits by editing those files.

## Quick start
Python (COCO):
```python
from pycocotools.coco import COCO
coco = COCO("annotations/grapes_instances_train.json")
img_ids = coco.getImgIds()
img = coco.loadImgs(img_ids[0])[0]
ann_ids = coco.getAnnIds(imgIds=img['id'])
anns = coco.loadAnns(ann_ids)
```

Convert CSV to COCO JSON:
```bash
python scripts/convert_to_coco.py --root . --out annotations --category grapes --splits train val test
```

Dependencies:
```bash
python -m pip install -r requirements.txt
```

Optional for the COCO API example:
```bash
python -m pip install pycocotools
```

## Evaluation and baselines
- Metric: mAP@[.50:.95] for detection
- This dataset is commonly used for grape detection and yield estimation tasks in viticulture.

## Datasheet (data card)

### Motivation
The WGISD (Wine Grape Instance Segmentation Dataset) was created to support research in automated grape detection and yield estimation in vineyards. The dataset contains high-resolution images of grape clusters from multiple varieties captured in field conditions.

### Composition
- **Image types**: RGB images of grape clusters in vineyards
- **Grape varieties**: Chardonnay (CDY), Cabernet Franc (CFR), Cabernet Sauvignon (CSV), Sauvignon Blanc (SVB), Syrah (SYH)
- **Image resolution**: Variable, typically 1920×1080 or 2048×1365 pixels
- **Annotation format**: Bounding boxes for grape instances

### Collection process
Images were captured in vineyard field conditions using handheld or ground-based cameras. The dataset includes images from different grape varieties and growing conditions to ensure diversity.

### Preprocessing
- Original data files (images, YOLO annotations, segmentation masks) are preserved in `data/origin/` directory
- Original YOLO format annotations have been converted to CSV format and stored in `grapes/csv/`, `high_resolution/csv/`, `video_frames/csv/`
- Images have been organized into standardized directory structure:
  - `grapes/images/` - Downsampled images (2048×1365)
  - `high_resolution/images/` - High-resolution images (5184×3456 or 4032×3024)
  - `video_frames/images/` - Video demo frames (500 images)
- JSON annotations have been created in each dataset directory (`grapes/json/`, `high_resolution/json/`, `video_frames/json/`)
- Berry annotations from `data/origin/contrib/berries/` have been copied to each dataset directory (`grapes/berries/`, `high_resolution/berries/`, `video_frames/berries/`)
- COCO format annotations have been generated for compatibility with standard detection frameworks
- Additional annotation files in `data/origin/`:
  - `*_berries.txt`: Space-separated berry center point coordinates (format: `image_name class_id x y`) for counting/keypoint detection tasks
  - `*_masked.txt`: List of image names (without extension) that have segmentation masks (.npz files)
  - `contrib/berries/*-berries.txt`: Tab-separated berry center point coordinates (format: `x y`) for counting/keypoint detection tasks
  - `video_demo_frames/`: Original video demo frames (500 images)

### Distribution
The dataset is distributed under CC BY-NC 4.0 license. Original data can be obtained from the GitHub repository: `https://github.com/thsant/wgisd`

### Maintenance
This standardized structure is maintained to ensure compatibility with standard detection frameworks and tools.

## Known issues and caveats
- **Image resolution**: Images have variable resolutions. The actual resolution should be read from the image files or COCO annotations.
- **Coordinate system**: All annotations use top-left corner coordinate system (x, y, width, height) in absolute pixels.
- **Original format**: The original dataset used YOLO format (normalized center coordinates). These have been converted to absolute pixel coordinates in CSV format.
- **File naming**: Image filenames include variety prefixes (CDY, CFR, CSV, SVB, SYH) indicating the grape variety.
- **Additional annotations**: The dataset includes additional annotation files in `data/origin/`:
  - Berry center point coordinates (`*_berries.txt`) for counting tasks: format is space-separated `image_name class_id x y`
  - Segmentation mask lists (`*_masked.txt`): list of images that have corresponding .npz segmentation mask files
- **Multiple resolutions**: The dataset includes both downsampled images (2048×1365) in `data/origin/` and original high-resolution images (5184×3456) in `original_resolution/`. All annotations are based on the downsampled images.
- **Segmentation coverage**: Only 137 images (45.7%) have segmentation masks (.npz files). See `docs/数据集结构详细说明.md` for details.

## Additional Documentation

For detailed information about the dataset structure and file formats, please refer to:

- **[数据集结构详细说明.md](docs/数据集结构详细说明.md)**: Comprehensive documentation of dataset structure, file formats, and differences from standard datasets
- **[关键问题解答.md](docs/关键问题解答.md)**: Answers to key questions about specific files and directories

These documents explain:
- The purpose of `data/origin/contrib/berries/`, `*.npz` files, `data/origin/video_demo_frames/`, and `WGISD.ipynb`
- Differences between this dataset and standard fruit detection datasets
- Recommendations for dataset standardization and potential re-annotation needs

## License
This dataset is licensed under the Creative Commons Attribution-NonCommercial 4.0 International License (CC BY-NC 4.0). See the `LICENSE` file for details.

**Important**: This license allows non-commercial use only. For commercial use, please contact the original dataset authors.

Check the original dataset terms and cite appropriately.

## Citation
If you use this dataset in your research, please cite the original WGISD dataset:

```bibtex
@misc{wgisd,
  title={WGISD: Wine Grape Instance Segmentation Dataset},
  author={Santos, Thiago Teixeira and others},
  howpublished={GitHub repository},
  url={https://github.com/thsant/wgisd},
  year={2020}
}
```

For the Embrapa version or this standardized structure, please also cite:

```bibtex
@misc{embrapa_wgisd,
  title={Embrapa WGISD Grape Detection Dataset - Standardized Structure},
  author={Embrapa},
  howpublished={Dataset repository},
  year={2025}
}
```

## Changelog
- **V1.0.0** (2025): Initial standardized structure and COCO conversion utility
  - Converted YOLO format annotations to CSV format
  - Organized images and annotations into standard directory structure
  - Generated COCO format annotations for train/val/test splits
  - Created conversion and organization scripts

## Contact
- **Maintainers**: Dataset structure maintainers
- **Original authors**: Thiago Teixeira Santos and collaborators
- **Source**: `https://github.com/thsant/wgisd`
