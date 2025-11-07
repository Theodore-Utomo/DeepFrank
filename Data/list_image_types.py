import argparse
import os
from collections import Counter


def list_image_extensions(directory_path: str) -> Counter:
	"""Return a Counter of file extensions in the given directory (non-recursive)."""
	counts: Counter = Counter()
	if not os.path.isdir(directory_path):
		raise FileNotFoundError(f"Directory not found: {directory_path}")

	for entry in os.listdir(directory_path):
		full_path = os.path.join(directory_path, entry)
		if not os.path.isfile(full_path):
			continue
		# Extract extension; handle files without extension
		_, ext = os.path.splitext(entry)
		if not ext:
			counts["<no extension>"] += 1
			continue
		# Normalize extension (lowercase, without leading dot)
		normalized = ext.lower().lstrip('.')
		counts[normalized] += 1

	return counts


def main() -> None:
	parser = argparse.ArgumentParser(
		description="List unique image file extensions in a directory (non-recursive).",
	)
	parser.add_argument(
		"directory",
		nargs="?",
		default="images_unlabelled",
		help="Directory to scan (default: images_unlabelled)",
	)
	args = parser.parse_args()

	counts = list_image_extensions(args.directory)
	if not counts:
		print("No files found.")
		return

	print(f"Directory: {os.path.abspath(args.directory)}")
	print("Found file extensions:")
	for ext in sorted(counts):
		print(f"- {ext}: {counts[ext]}")

	# Short summary of just the kinds
	kinds = ", ".join(sorted(counts))
	print(f"\nKinds: {kinds}")


if __name__ == "__main__":
	main()


