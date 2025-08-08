# Captioned Image Dataset Formatter

Flexible dataset tool for creating a 🤗 Datasets dataset from image-caption pairs.

The tool expects duplicate directory structures and filenames (excluding file extentions) for the images and captions. Subdirectories will be used as additional tabular attributes.

This file structure is chosen to allow for efficient changes between caption sets, and to easily integrate with my [VLM-Captioner](https://github.com/alexsenden/vlm-captioning).

**Ex.**

_Input File Structure:_

```
dataset/
├── image_folder/
|   ├── subdir1/
|   │   ├── image_1.png
|   │   ├── image_2.png
|   │   └── ...
|   └── subdir2/
|       ├── image_1001.png
|       └── ...
└── caption_folder/
    ├── subdir1/
    │   ├── image_1.txt
    │   ├── image_2.txt
    │   └── ...
    └── subdir2/
        ├── image_1001.txt
        └── ...
```

_Output Dataset:_

| image          | caption        | attribute_1 |
| -------------- | -------------- | ----------- |
| image_1.png    | image_1.txt    | subdir1     |
| image_2.png    | image_2.txt    | subdir1     |
| ...            | ...            | ...         |
| image_1001.png | image_1001.txt | subdir2     |

### Installation and Usage

First, install the package from PyPI:

```
pip install captioned-image-dataset-loader
```

Datasets can then be loaded using the following:

```
from captioned_image_dataset_generator import load_captioned_image_dataset

dataset = load_captioned_image_dataset("data/images", "data/captions")
```
