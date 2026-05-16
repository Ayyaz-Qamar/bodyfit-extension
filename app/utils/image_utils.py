"""
Image processing and validation utilities.
"""

import os
import uuid
from pathlib import Path
from PIL import Image
from fastapi import HTTPException, UploadFile


# Configuration
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
MAX_FILE_SIZE_MB = 10
UPLOAD_DIR = Path("uploads")

# Ensure upload directory exists
UPLOAD_DIR.mkdir(exist_ok=True)


def validate_image_file(file: UploadFile) -> None:
    """
    Validates that uploaded file is a proper image.
    Raises HTTPException if invalid.
    """
    
    # Check 1: Filename exists
    if not file.filename:
        raise HTTPException(
            status_code=400, 
            detail="No filename provided"
        )
    
    # Check 2: File extension is allowed
    extension = file.filename.rsplit(".", 1)[-1].lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type '{extension}'. Allowed: {ALLOWED_EXTENSIONS}"
        )
    
    # Check 3: Content type is image
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail=f"File content-type is not an image: {file.content_type}"
        )


async def save_uploaded_image(file: UploadFile) -> dict:
    """
    Saves uploaded file to disk with unique filename.
    Returns metadata about saved file.
    """
    
    # Generate unique filename to prevent collisions
    upload_id = str(uuid.uuid4())
    extension = file.filename.rsplit(".", 1)[-1].lower()
    safe_filename = f"{upload_id}.{extension}"
    file_path = UPLOAD_DIR / safe_filename
    
    # Read file content
    content = await file.read()
    
    # Check file size
    file_size_bytes = len(content)
    file_size_mb = file_size_bytes / (1024 * 1024)
    
    if file_size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"File too large: {file_size_mb:.2f}MB. Max allowed: {MAX_FILE_SIZE_MB}MB"
        )
    
    # Save to disk
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Verify it's a valid image by opening with Pillow
    try:
        img = Image.open(file_path)
        width, height = img.size
        img.verify()
    except Exception as e:
        os.remove(file_path)
        raise HTTPException(
            status_code=400,
            detail=f"File is not a valid image: {str(e)}"
        )
    
    return {
        "upload_id": upload_id,
        "filename": safe_filename,
        "file_size_kb": round(file_size_bytes / 1024, 2),
        "image_width": width,
        "image_height": height,
        "file_path": str(file_path)
    }