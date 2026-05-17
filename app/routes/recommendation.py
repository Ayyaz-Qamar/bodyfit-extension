"""
Shirt size recommendation endpoint - the complete pipeline.
"""

from pathlib import Path
from fastapi import APIRouter, HTTPException
from app.schemas.image_schemas import (
    SizeRecommendationRequest,
    SizeRecommendationResponse,
    BodyMeasurements,
    AlternativeSize
)
from app.services.pose_detector import detect_pose_from_image
from app.services.measurement_calculator import calculate_measurements
from app.services.size_recommender import recommend_shirt_size


router = APIRouter(prefix="/api", tags=["Size Recommendation"])

UPLOAD_DIR = Path("uploads")


@router.post("/recommend-size", response_model=SizeRecommendationResponse)
async def recommend_size(request: SizeRecommendationRequest):
    """
    Complete pipeline: image → pose → measurements → size recommendation.
    
    - **upload_id**: ID from /api/upload-image
    - **user_height_cm**: User's height (50-250 cm)
    - **user_gender**: 'male' or 'female' (default: male)
    
    Returns the best matching shirt size with confidence and alternatives.
    """
    
    # Step 1: Find uploaded image
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
    
    # Step 2: Pose detection
    pose_result = detect_pose_from_image(str(image_path))
    if not pose_result["success"]:
        raise HTTPException(
            status_code=422,
            detail=f"Pose detection failed: {pose_result['error']}"
        )
    
    # Step 3: Calculate body measurements
    measurements_data = calculate_measurements(
        landmarks=pose_result["landmarks"],
        image_shape=pose_result["image_shape"],
        user_height_cm=request.user_height_cm
    )
    
    # Step 4: Recommend size
    recommendation = recommend_shirt_size(
        chest_width_cm=measurements_data["chest_width_cm"],
        shoulder_width_cm=measurements_data["shoulder_width_cm"],
        gender=request.user_gender
    )
    
    # Step 5: Build structured response
    body_measurements = BodyMeasurements(
        shoulder_width_cm=measurements_data["shoulder_width_cm"],
        hip_width_cm=measurements_data["hip_width_cm"],
        chest_width_cm=measurements_data["chest_width_cm"],
        torso_length_cm=measurements_data["torso_length_cm"],
        arm_length_cm=measurements_data["arm_length_cm"],
        estimated_height_cm=measurements_data["estimated_height_cm"]
    )
    
    alternatives = [
        AlternativeSize(size=alt["size"], confidence_score=alt["confidence_score"])
        for alt in recommendation["alternative_sizes"]
    ]
    
    return SizeRecommendationResponse(
        success=True,
        message="Size recommendation completed successfully",
        upload_id=upload_id,
        recommended_size=recommendation["recommended_size"],
        confidence_score=recommendation["confidence_score"],
        chest_circumference_estimated_cm=recommendation["chest_circumference_estimated_cm"],
        alternative_sizes=alternatives,
        explanation=recommendation["explanation"],
        fit_advice=recommendation["fit_advice"],
        measurements_used=body_measurements
    )