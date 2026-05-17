"""
Pose detection endpoints.
"""

from pathlib import Path
from fastapi import APIRouter, HTTPException
from app.schemas.image_schemas import (
    PoseDetectionRequest,
    PoseDetectionResponse,
    Landmark,
    ImageShape
)
from app.services.pose_detector import (
    detect_pose_from_image,
    visualize_pose_on_image
)


router = APIRouter(prefix="/api", tags=["Pose Detection"])

UPLOAD_DIR = Path("uploads")


@router.post("/detect-pose", response_model=PoseDetectionResponse)
async def detect_pose(request: PoseDetectionRequest):
    """
    Detect 33 body landmarks from a previously uploaded image.
    
    - **upload_id**: ID returned from /api/upload-image endpoint
    
    Returns landmark coordinates and a URL to the annotated visualization image.
    """
    
    # Step 1: Find the uploaded image
    upload_id = request.upload_id
    
    # Try common extensions to locate file
    image_path = None
    for ext in ["jpg", "jpeg", "png", "webp"]:
        candidate = UPLOAD_DIR / f"{upload_id}.{ext}"
        if candidate.exists():
            image_path = candidate
            break
    
    if image_path is None:
        raise HTTPException(
            status_code=404,
            detail=f"Image with upload_id '{upload_id}' not found. Upload first via /api/upload-image"
        )
    
    # Step 2: Run pose detection
    result = detect_pose_from_image(str(image_path))
    
    if not result["success"]:
        raise HTTPException(
            status_code=422,
            detail=result["error"]
        )
    
    # Step 3: Generate visualization image
    viz_filename = f"{upload_id}_pose.jpg"
    viz_path = UPLOAD_DIR / viz_filename
    
    viz_success = visualize_pose_on_image(str(image_path), str(viz_path))
    
    if not viz_success:
        raise HTTPException(
            status_code=500,
            detail="Pose detected but visualization failed"
        )
    
    # Step 4: Build structured response
    landmarks_list = [Landmark(**lm) for lm in result["landmarks"]]
    
    return PoseDetectionResponse(
        success=True,
        message="Pose detection completed successfully",
        upload_id=upload_id,
        landmark_count=len(landmarks_list),
        image_shape=ImageShape(**result["image_shape"]),
        landmarks=landmarks_list,
        visualization_url=f"/uploads/{viz_filename}"
    )