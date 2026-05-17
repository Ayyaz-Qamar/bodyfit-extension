"""
Pydantic schemas for image upload and pose detection endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, List


# ============================================
# UPLOAD ENDPOINT SCHEMAS
# ============================================

class UploadResponse(BaseModel):
    """Response sent back after successful image upload."""
    
    success: bool = Field(..., description="Whether upload was successful")
    message: str = Field(..., description="Human-readable status message")
    filename: str = Field(..., description="Saved filename on server")
    file_size_kb: float = Field(..., description="File size in kilobytes")
    image_width: int = Field(..., description="Image width in pixels")
    image_height: int = Field(..., description="Image height in pixels")
    upload_id: str = Field(..., description="Unique ID to reference this upload")


# ============================================
# POSE DETECTION SCHEMAS
# ============================================

class Landmark(BaseModel):
    """Single body landmark point."""
    
    index: int = Field(..., description="Landmark index (0-32)")
    name: str = Field(..., description="Body part name")
    x: float = Field(..., description="Normalized x coordinate (0-1)")
    y: float = Field(..., description="Normalized y coordinate (0-1)")
    z: float = Field(..., description="Normalized z (depth) coordinate")
    visibility: float = Field(..., description="Detection confidence (0-1)")


class ImageShape(BaseModel):
    """Image dimensions."""
    
    width: int
    height: int
    channels: int


class PoseDetectionRequest(BaseModel):
    """Request body for pose detection endpoint."""
    
    upload_id: str = Field(..., description="ID of previously uploaded image")


class PoseDetectionResponse(BaseModel):
    """Response from pose detection endpoint."""
    
    success: bool
    message: str
    upload_id: str
    landmark_count: int = Field(..., description="Number of detected landmarks (33 if successful)")
    image_shape: ImageShape
    landmarks: List[Landmark] = Field(..., description="33 body landmarks")
    visualization_url: str = Field(..., description="URL to view annotated image")
    # ============================================
# MEASUREMENT SCHEMAS
# ============================================

class MeasurementRequest(BaseModel):
    """Request body for measurement calculation."""
    
    upload_id: str = Field(..., description="ID of previously uploaded image")
    user_height_cm: float = Field(..., gt=50, lt=250, description="User's actual height in centimeters")
    user_gender: Optional[str] = Field(None, description="Optional: 'male' or 'female' for better estimation")


class BodyMeasurements(BaseModel):
    """Estimated body measurements in centimeters."""
    
    shoulder_width_cm: float = Field(..., description="Distance between shoulder joints")
    hip_width_cm: float = Field(..., description="Distance between hip joints")
    chest_width_cm: float = Field(..., description="Estimated chest width (front view)")
    torso_length_cm: float = Field(..., description="Shoulder midpoint to hip midpoint")
    arm_length_cm: float = Field(..., description="Shoulder to wrist (average)")
    estimated_height_cm: float = Field(..., description="Detected body height from image")


class MeasurementResponse(BaseModel):
    """Response from measurement calculation."""
    
    success: bool
    message: str
    upload_id: str
    user_height_cm: float
    pixels_per_cm: float = Field(..., description="Conversion factor used")
    measurements: BodyMeasurements
    confidence_score: float = Field(..., ge=0, le=1, description="Overall measurement confidence (0-1)")
    notes: List[str] = Field(default_factory=list, description="Any warnings or notes")


# ============================================
# ERROR SCHEMAS
# ============================================

class ErrorResponse(BaseModel):
    """Standard error response format."""
    
    success: bool = False
    error: str
    detail: Optional[str] = None