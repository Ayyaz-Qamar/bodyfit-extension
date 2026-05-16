"""
Pydantic schemas for image upload endpoints.
Defines the shape of request/response data.
"""

from pydantic import BaseModel, Field
from typing import Optional


class UploadResponse(BaseModel):
    """Response sent back after successful image upload."""
    
    success: bool = Field(..., description="Whether upload was successful")
    message: str = Field(..., description="Human-readable status message")
    filename: str = Field(..., description="Saved filename on server")
    file_size_kb: float = Field(..., description="File size in kilobytes")
    image_width: int = Field(..., description="Image width in pixels")
    image_height: int = Field(..., description="Image height in pixels")
    upload_id: str = Field(..., description="Unique ID to reference this upload")


class ErrorResponse(BaseModel):
    """Standard error response format."""
    
    success: bool = False
    error: str
    detail: Optional[str] = None