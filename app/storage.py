
"""Helpers for saving uploaded files to MEDIA_ROOT organized per company."""
from pathlib import Path
from .config import settings
from uuid import uuid4

def save_upload_file(file_obj, company_id: int, filename: str) -> str:
    """Save an UploadFile to disk under MEDIA_ROOT/<company_id>/ and return path.

    Args:
        file_obj: FastAPI UploadFile object.
        company_id: Company primary key used to namespace files.
        filename: Original filename from the upload (used for extension).

    Returns:
        Absolute path to the saved file as a string.
    """
    root = Path(settings.MEDIA_ROOT) / str(company_id)
    root.mkdir(parents=True, exist_ok=True)
    safe_name = f"{uuid4().hex}-{Path(filename).name}"
    dest = root / safe_name
    # Stream write to avoid loading entire file in memory
    with open(dest, "wb") as out:
        while True:
            chunk = file_obj.file.read(1024 * 64)
            if not chunk:
                break
            out.write(chunk)
    return str(dest)
