import os
import sys
import re
import uuid
from datetime import datetime
from pathlib import Path

try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    sys.path.append(MAIN_DIR)

    from logs import log_debug, log_error, log_info
except Exception as e:
    msg = f"Import Error in: {os.path.dirname(__file__)}, Error: {e}"
    raise ImportError(msg)


def create_unique_name(orig_file_name: str) -> str:
    """
    Cleans and generates a unique file name based on the original name.

    Args:
        orig_file_name (str): The original uploaded file name.

    Returns:
        str: A sanitized, unique file name.
    """
    try:
        if not orig_file_name or not isinstance(orig_file_name, str):
            raise ValueError("Invalid file name provided.")

        # Extract extension and name
        extension = Path(orig_file_name).suffix
        name = Path(orig_file_name).stem

        if not extension:
            log_error(f"Missing file extension in: {orig_file_name}")
            extension = ".dat"  # fallback default

        if not name:
            log_error(f"Missing file name, using 'file' as default.")
            name = "file"

        # Sanitize the name: replace non-word characters with underscore
        cleaned_name = re.sub(r"[^\w]", "_", name).strip("_")

        # Add unique suffix: timestamp + short UUID
        unique_suffix = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:8]

        # Build new filename
        new_filename = f"{cleaned_name}_{unique_suffix}{extension}"

        log_debug(f"Original filename: {orig_file_name} | Cleaned: {new_filename}")
        return new_filename

    except Exception as e:
        log_error(f"Error generating clean filename: {e}")
        # Fallback filename if something goes wrong
        fallback_name = f"file_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.dat"
        return fallback_name


if __name__ == "__main__":
    print(create_unique_name("AlRashid.pdf"))
