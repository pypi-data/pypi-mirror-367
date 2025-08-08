import os

from datasets import Dataset, Features, Image, Value

IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tif")


def _generate_examples_recursive(image_dir, caption_dir, relative_path_array):
    directory_listing = os.listdir(image_dir)

    for fname in sorted(directory_listing):
        fpath = os.path.join(image_dir, fname)
        if os.path.isdir(fpath):
            yield from _generate_examples_recursive(
                fpath, caption_dir, relative_path_array + [fname]
            )
        elif fname.lower().endswith(IMAGE_EXTENSIONS):
            caption = None
            caption_path = os.path.join(
                caption_dir,
                *relative_path_array,
                fname.replace(os.path.splitext(fname)[1], ".txt"),
            )
            with open(caption_path, "r") as f:
                caption = f.read().strip()

            datum = {
                "image": fpath,
                "caption": caption,
                "filepath": os.path.join(caption_dir, *relative_path_array, fname),
            }

            for i, subdir in enumerate(relative_path_array):
                datum[f"attribute_{i + 1}"] = subdir

            yield datum


def captioned_image_generator(image_dir, caption_dir):
    yield from _generate_examples_recursive(image_dir, caption_dir, [])


def max_recursive_depth(image_dir, current_depth=0):
    directory_listing = os.listdir(image_dir)
    depths = [current_depth]

    for fname in sorted(directory_listing):
        fpath = os.path.join(image_dir, fname)
        if os.path.isdir(fpath):
            depths.append(max_recursive_depth(fpath, current_depth + 1))

    return max(depths)


def load_captioned_image_dataset(image_dir, caption_dir):
    features_dict = {
        "image": Image(),
        "caption": Value("string"),
        "filepath": Value("string"),
    }
    for i in range(max_recursive_depth(image_dir)):
        features_dict[f"attribute_{i + 1}"] = Value("string")

    return Dataset.from_generator(
        captioned_image_generator,
        gen_kwargs={
            "image_dir": image_dir,
            "caption_dir": caption_dir,
        },
        features=Features(features_dict),
    )
