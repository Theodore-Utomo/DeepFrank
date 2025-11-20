import argparse
import os
import random
import shutil
from typing import Dict, List, Tuple


IMAGE_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png",
    "webp",
}


def list_images(images_dir: str) -> Dict[str, str]:
    """Return mapping from lowercase stem -> absolute image path.

    Only includes files with IMAGE_EXTENSIONS and skips .mat files.
    """
    mapping: Dict[str, str] = {}
    for entry in os.listdir(images_dir):
        full = os.path.join(images_dir, entry)
        if not os.path.isfile(full):
            continue
        name, ext = os.path.splitext(entry)
        if not ext:
            continue
        ext = ext.lstrip(".").lower()
        if ext == "mat" or ext not in IMAGE_EXTENSIONS:
            continue
        mapping[name.lower()] = full
    return mapping


def list_labels(labels_dir: str) -> Dict[str, str]:
    """Return mapping from lowercase stem -> absolute label path for .txt files."""
    mapping: Dict[str, str] = {}
    for entry in os.listdir(labels_dir):
        if not entry.lower().endswith(".txt"):
            continue
        full = os.path.join(labels_dir, entry)
        if not os.path.isfile(full):
            continue
        name, _ = os.path.splitext(entry)
        mapping[name.lower()] = full
    return mapping


def pair_images_labels(images_dir: str, labels_dir: str) -> List[Tuple[str, str]]:
    images = list_images(images_dir)
    labels = list_labels(labels_dir)
    pairs: List[Tuple[str, str]] = []
    missing_images = 0
    for stem_lower, label_path in labels.items():
        img_path = images.get(stem_lower)
        if img_path:
            pairs.append((img_path, label_path))
        else:
            missing_images += 1
    if missing_images:
        print(
            f"Warning: {missing_images} labels had no matching image and were skipped."
        )
    return pairs


def split_pairs(
    pairs: List[Tuple[str, str]], train: float, val: float, seed: int
) -> Dict[str, List[Tuple[str, str]]]:
    assert 0 < train < 1 and 0 <= val < 1 and train + val < 1
    test = 1.0 - train - val
    random.Random(seed).shuffle(pairs)
    n = len(pairs)
    n_train = int(n * train)
    n_val = int(n * val)
    result = {
        "train": pairs[:n_train],
        "val": pairs[n_train : n_train + n_val],
        "test": pairs[n_train + n_val :],
    }
    print(
        f"Split -> train: {len(result['train'])}, val: {len(result['val'])}, test: {len(result['test'])} (total {n})"
    )
    return result


def safe_copy(src: str, dst: str) -> None:
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.exists(dst):
        # Do not overwrite; keep first occurrence
        return
    shutil.copy2(src, dst)


def build_output_paths(
    root: str, split_name: str, image_src: str, label_src: str
) -> Tuple[str, str]:
    img_name = os.path.basename(image_src)
    lbl_name = os.path.basename(label_src)
    img_dst = os.path.join(root, "images", split_name, img_name)
    lbl_dst = os.path.join(root, "labels", split_name, lbl_name)
    return img_dst, lbl_dst


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Organize labeled cat data into images/{train,val,test} and labels/{train,val,test}.",
    )
    parser.add_argument(
        "--images-dir",
        default=os.path.join("Data", "cat_images"),
        help="Directory containing cat images (default: Data/cat_images)",
    )
    parser.add_argument(
        "--labels-dir",
        default=os.path.join("Data", "cat_labels"),
        help="Directory containing cat labels (default: Data/cat_labels)",
    )
    parser.add_argument(
        "--out-root",
        default=os.path.join("Data", "cat_body_parts_dataset"),
        help="Output dataset root (default: Data/cat_body_parts_dataset)",
    )
    parser.add_argument(
        "--train", type=float, default=0.8, help="Train split ratio (default: 0.8)"
    )
    parser.add_argument(
        "--val", type=float, default=0.1, help="Validation split ratio (default: 0.1)"
    )
    parser.add_argument(
        "--seed", type=int, default=42, help="Random seed for splitting (default: 42)"
    )
    args = parser.parse_args()

    if not os.path.isdir(args.images_dir):
        raise FileNotFoundError(f"Images directory not found: {args.images_dir}")
    if not os.path.isdir(args.labels_dir):
        raise FileNotFoundError(f"Labels directory not found: {args.labels_dir}")

    pairs = pair_images_labels(args.images_dir, args.labels_dir)
    splits = split_pairs(pairs, train=args.train, val=args.val, seed=args.seed)

    for split_name, items in splits.items():
        for img_src, lbl_src in items:
            img_dst, lbl_dst = build_output_paths(
                args.out_root, split_name, img_src, lbl_src
            )
            safe_copy(img_src, img_dst)
            safe_copy(lbl_src, lbl_dst)

    print("Done. Dataset organized at:", os.path.abspath(args.out_root))


if __name__ == "__main__":
    main()
