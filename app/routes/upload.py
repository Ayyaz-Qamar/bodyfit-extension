"""
Image upload endpoints.
"""

from fastapi import APIRouter, UploadFile, File
from app.schemas.image_schemas import UploadResponse
from app.utils.image_utils import validate_image_file, save_uploaded_image


router = APIRouter(prefix="/api", tags=["Image Upload"])


@router.post("/upload-image", response_model=UploadResponse)
async def upload_image(file: UploadFile = File(...)):
    """
    Upload a single body image (front or side view).
    
    - **file**: Image file (JPG, JPEG, PNG, or WebP, max 10MB)
    
    Returns metadata about the saved image including a unique upload_id.
    """
    
    # Step 1: Validate file
    validate_image_file(file)
    
    # Step 2: Save to disk
    saved_info = await save_uploaded_image(file)
    
    # Step 3: Return response
    return UploadResponse(
        success=True,
        message="Image uploaded successfully",
        filename=saved_info["filename"],
        file_size_kb=saved_info["file_size_kb"],
        image_width=saved_info["image_width"],
        image_height=saved_info["image_height"],
        upload_id=saved_info["upload_id"]
    )