from __future__ import annotations
import hashlib
from typing import Dict, Tuple

# Magic numbers for common document types
MAGIC_NUMBERS = {
    "pdf": b"%PDF-",
    "docx": b"PK\x03\x04", # ZIP based
    "png": b"\x89PNG\r\n\x1a\n",
    "jpg": b"\xff\xd8\xff",
    "jpeg": b"\xff\xd8\xff",
}

def verify_file_signature(content: bytes, filename: str) -> bool:
    """
    Verifies that the file content matches its extension using magic bytes.
    """
    ext = filename.split('.')[-1].lower()
    signature = MAGIC_NUMBERS.get(ext)

    if not signature:
        # If we don't have a signature for the extension, we can't verify,
        # but for this product, we only allow known types.
        return False

    return content.startswith(signature)

def compute_sha256(content: bytes) -> str:
    """
    Computes a SHA-256 hash of the provided bytes.
    """
    return hashlib.sha256(content).hexdigest()
