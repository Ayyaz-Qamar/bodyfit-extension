"""
Body measurement calculation endpoints.
"""

from pathlib import Path
from fastapi import APIRouter, HTTPException
from app.schemas.image_schemas import (
    MeasurementRequest,
    MeasurementResponse,
    BodyMeasurements
)
from app.services.pose_detector import detect_pose_from_image
from app.services.measurement_calculator import calculate_measurements


router = APIRouter(prefix="/api", tags=["Body Measurements"])

UPLOAD_DIR = Path("uploads")


@router.post("/calculate-measurements", response_model=MeasurementResponse)
async def calculate_body_measurements(request: MeasurementRequest):
    """
    Calculate body measurements from a previously uploaded image.
    
    - **upload_id**: ID from /api/upload-image
    - **user_height_cm**: User's actual height (50-250 cm)
    - **user_gender**: Optional ('male' or 'female')
    
    Returns shoulder width, chest, hip, torso, arm length in centimeters.
    """
    
    # Step 1: Find the uploaded image
    upload_id = request.upload_id
    image_path = None
    for ext in ["jpg", "jpeg", "png", "webp"]:
        candidate = UPLOAD_DIR / f"{upload_id}.{ext}"
        if candidate.exists():
            image_path = candidate
            break
    
    if image_path is None:
        raise HTTPException(
            status_code=404,
            detail=f"Image with upload_id '{upload_id}' not found"
        )
    
    # Step 2: Run pose detection
    pose_result = detect_pose_from_image(str(image_path))
    
    if not pose_result["success"]:
        raise HTTPException(
            status_code=422,
            detail=f"Pose detection failed: {pose_result['error']}"
        )
    
    # Step 3: Calculate measurements
    measurements_data = calculate_measurements(
        landmarks=pose_result["landmarks"],
        image_shape=pose_result["image_shape"],
        user_height_cm=request.user_height_cm
    )
    
    # Step 4: Build response
    body_measurements = BodyMeasurements(
        shoulder_width_cm=measurements_data["shoulder_width_cm"],
        hip_width_cm=measurements_data["hip_width_cm"],
        chest_width_cm=measurements_data["chest_width_cm"],
        torso_length_cm=measurements_data["torso_length_cm"],
        arm_length_cm=measurements_data["arm_length_cm"],
        estimated_height_cm=measurements_data["estimated_height_cm"]
    )
    
    return MeasurementResponse(
        success=True,
        message="Body measurements calculated successfully",
        upload_id=upload_id,
        user_height_cm=request.user_height_cm,
        pixels_per_cm=measurements_data["pixels_per_cm"],
        measurements=body_measurements,
        confidence_score=measurements_data["confidence_score"],
        notes=measurements_data["notes"]
    )