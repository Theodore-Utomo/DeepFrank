import argparse
import json
import os
import shutil
from typing import Optional, Set, Tuple


IMAGE_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png",
    "gif",
    "bmp",
    "tif",
    "tiff",
    "webp",
    "heic",
    "heif",
}


def is_image_file(filename: str) -> bool:
    _, ext = os.path.splitext(filename)
    if not ext:
        return False
    ext = ext.lower().lstrip(".")
    if ext == "mat":
        return False
    return ext in IMAGE_EXTENSIONS


def extract_breed_from_filename(filename: str) -> Optional[str]:
    base = os.path.basename(filename)
    name, _ = os.path.splitext(base)
    if not name:
        return None

    if "_" in name:
        head, tail = name.rsplit("_", 1)
        if tail.isdigit():
            candidate = head
        else:
            candidate = name
    else:
        candidate = name

    candidate = candidate.strip()
    if not candidate:
        return None
    return candidate.lower()


def load_species_sets(breeds_json_path: str) -> Tuple[Set[str], Set[str]]:
    with open(breeds_json_path, "r") as f:
        data = json.load(f)
    cats = set(x.lower() for x in data.get("cats", []))
    dogs = set(x.lower() for x in data.get("dogs", []))
    return cats, dogs


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def move_file(src_path: str, dst_dir: str) -> bool:
    """Move file to dst_dir. If a file with same name exists, skip and return False."""
    ensure_dir(dst_dir)
    filename = os.path.basename(src_path)
    dst_path = os.path.join(dst_dir, filename)
    if os.path.exists(dst_path):
        # Skip on collision to avoid overwriting
        return False
    shutil.move(src_path, dst_path)
    return True


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Separate images into cat_images and dog_images based on breed names in filenames."
        )
    )
    parser.add_argument(
        "--source",
        default=os.path.join("Data", "images_unlabelled"),
        help="Source directory of unlabeled images (default: Data/images_unlabelled)",
    )
    parser.add_argument(
        "--breeds-json",
        default=os.path.join("Data", "breeds.json"),
        help="Path to breeds.json mapping (default: Data/breeds.json)",
    )
    parser.add_argument(
        "--cat-dest",
        default=os.path.join("Data", "cat_images"),
        help="Destination directory for cat images (default: Data/cat_images)",
    )
    parser.add_argument(
        "--dog-dest",
        default=os.path.join("Data", "dog_images"),
        help="Destination directory for dog images (default: Data/dog_images)",
    )
    args = parser.parse_args()

    source_dir = args.source
    if not os.path.isdir(source_dir):
        raise FileNotFoundError(f"Source directory not found: {source_dir}")

    cats, dogs = load_species_sets(args.breeds_json)

    counts = {
        "cats_moved": 0,
        "dogs_moved": 0,
        "unknown_skipped": 0,
        "non_image_skipped": 0,
        "collisions_skipped": 0,
    }

    for entry in os.listdir(source_dir):
        src_path = os.path.join(source_dir, entry)
        if not os.path.isfile(src_path):
            continue
        if not is_image_file(entry):
            counts["non_image_skipped"] += 1
            continue
        breed = extract_breed_from_filename(entry)
        if not breed:
            counts["unknown_skipped"] += 1
            continue

        if breed in cats:
            moved = move_file(src_path, args.cat_dest)
            if moved:
                counts["cats_moved"] += 1
            else:
                counts["collisions_skipped"] += 1
        elif breed in dogs:
            moved = move_file(src_path, args.dog_dest)
            if moved:
                counts["dogs_moved"] += 1
            else:
                counts["collisions_skipped"] += 1
        else:
            counts["unknown_skipped"] += 1

    print("Separation complete.")
    print(f"Source: {os.path.abspath(source_dir)}")
    print(f"Cats moved: {counts['cats_moved']}")
    print(f"Dogs moved: {counts['dogs_moved']}")
    print(f"Unknown/Unmapped skipped: {counts['unknown_skipped']}")
    print(f"Non-image skipped: {counts['non_image_skipped']}")
    print(f"Name collisions skipped: {counts['collisions_skipped']}")


if __name__ == "__main__":
    main()


