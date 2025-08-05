import argparse
import logging
from pycleaner.core import clean_import

from pathlib import Path

# base logger
logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s"
)

def main():
    parser = argparse.ArgumentParser(description="Python Import Cleaner")
    parser.add_argument("command", choices=["clean-import"], help="Command to run")
    parser.add_argument("file", type=str, help="Path to the Python File")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug output")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    file_path = Path(args.file).resolve()

    if args.command == "clean-import":
        logger.info(f"Cleaning imports in {file_path}")
        clean_import(file_path)
        logger.info("Done ✅")

if __name__ == "__main__":
    main()
