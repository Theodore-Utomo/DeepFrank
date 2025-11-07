import argparse
import os
from collections import Counter
from typing import Iterable, Optional


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
    """Extract the breed name from a filename like 'american_cocker_spaniel_12.jpg'.

    Strategy: if the name contains underscores and ends with an underscore + digits,
    treat the part before the LAST underscore as the breed. Otherwise, use the whole
    stem. Normalize to lowercase.

    Examples:
      - 'german-shepherd_123.JPG' -> 'german-shepherd'
      - 'american_cocker_spaniel_12.jpg' -> 'american_cocker_spaniel'
      - 'british_shorthair_003.png' -> 'british_shorthair'
      - 'pug.png' (no underscore) -> 'pug'
    Returns None if no reasonable breed segment is found.
    """
    base = os.path.basename(filename)
    name, _ = os.path.splitext(base)
    if not name:
        return None

    # If ends with _<digits>, drop the trailing numeric chunk
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


def scan_breeds(directory_path: str) -> Counter:
    """Scan a directory (non-recursive) and count breeds inferred from filenames."""
    counts: Counter = Counter()
    if not os.path.isdir(directory_path):
        raise FileNotFoundError(f"Directory not found: {directory_path}")

    for entry in os.listdir(directory_path):
        full_path = os.path.join(directory_path, entry)
        if not os.path.isfile(full_path):
            continue
        if not is_image_file(entry):
            continue
        breed = extract_breed_from_filename(entry)
        if breed:
            counts[breed] += 1

    return counts


def print_report(directory_path: str, counts: Counter) -> None:
    total = sum(counts.values())
    print(f"Directory: {os.path.abspath(directory_path)}")
    print(f"Total images counted: {total}")
    if not counts:
        print("No image files found.")
        return

    print("\nBreeds (inferred from filenames):")
    # Sort by count desc, then name asc
    for breed, count in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
        print(f"- {breed}: {count}")

    kinds = ", ".join(sorted(counts.keys()))
    print(f"\nKinds: {kinds}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Infer unique breeds in a directory by parsing filenames (non-recursive). "
            "Ignores .mat files and only counts common image types."
        )
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default="images_unlabelled",
        help="Directory to scan (default: images_unlabelled)",
    )
    args = parser.parse_args()

    counts = scan_breeds(args.directory)
    print_report(args.directory, counts)


if __name__ == "__main__":
    main()


