import os
import sys
import shutil


def delpycache():
    # Get Arguments
    argv = sys.argv
    if len(argv) > 2:
        raise ValueError(
            "Too many arguments provided. Usage: python delpycache.py [target_directory]"
        )

    # Set target dir
    target_dir = os.getcwd()
    if len(argv) == 2:
        if os.path.isabs(argv[1]):
            target_dir = argv[1]
        else:
            target_dir = os.path.join(os.getcwd(), argv[1])

        if not os.path.isdir(target_dir):
            raise ValueError(f"Invalid directory: {target_dir}")
    print(f"Deleting __pycache__ files under target dir: {target_dir}")

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
