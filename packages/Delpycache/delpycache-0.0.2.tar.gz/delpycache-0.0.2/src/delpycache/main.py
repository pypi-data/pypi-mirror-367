import argparse
import os
import shutil


def delpycache():
    """
    Deletes all __pycache__ directories recursively under the specified target directory.

    This function scans the given directory (or current directory by default),
    finds all subdirectories named '__pycache__', and deletes them.
    Useful for cleaning up Python bytecode cache files.
    """

    # Get Arguments
    parser = argparse.ArgumentParser(
        description="Delete all __pycache__ directories under the given directory (default: current directory)."
    )
    parser.add_argument(
        "target_dir",
        nargs="?",
        default=".",
        help="Target directory to scan (default: current working directory)",
    )
    args = parser.parse_args()

    # Resolve absolute path
    target_dir = os.path.abspath(args.target_dir)
    if not os.path.isdir(target_dir):
        raise ValueError(f"Invalid directory: {target_dir}")
    print(f"Deleting __pycache__ files under: {target_dir}")

    # Loop to find and delete __pycache__
    num = 0
    try:
        for dirpath, dirnames, _ in os.walk(target_dir):
            for dirname in dirnames:
                if dirname == "__pycache__":
                    full_path = os.path.join(dirpath, dirname)
                    print(f"Deleting: {full_path}")
                    num += 1
                    shutil.rmtree(full_path)
    except Exception as e:
        print(f"Error while deleting __pycache__ directories: {e}")
    print(f"Total __pycache__ directories deleted: {num}")


__all__ = ["delpycache"]
