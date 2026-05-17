"""
Body measurement calculator service.
Converts pose landmarks into real-world centimeter measurements.
"""

import math
from typing import List, Dict


# Industry-standard adjustment factors
# Pose landmarks are at JOINT centers, real body measurements include flesh/clothing
SHOULDER_WIDTH_FACTOR = 1.15      # Joint-to-joint × 1.15 ≈ actual shoulder width
CHEST_WIDTH_FACTOR = 0.95          # Chest is slightly narrower than shoulder span
HIP_WIDTH_FACTOR = 1.10            # Hip joint distance × 1.10 ≈ actual hip width
HEAD_TOP_ADJUSTMENT = 0.95         # Visible height (eyes to ankles) ≈ 95% of true height


def euclidean_distance(p1: Dict, p2: Dict, image_width: int, image_height: int) -> float:
    """
    Calculate Euclidean distance between 2 landmarks in PIXELS.
    
    Args:
        p1, p2: Landmark dicts with 'x' and 'y' (normalized 0-1)
        image_width, image_height: Image dimensions
    
    Returns:
        Distance in pixels
    """
    x1_px = p1['x'] * image_width
    y1_px = p1['y'] * image_height
    x2_px = p2['x'] * image_width
    y2_px = p2['y'] * image_height
    
    return math.sqrt((x2_px - x1_px) ** 2 + (y2_px - y1_px) ** 2)


def calculate_pixel_height(landmarks: List[Dict], image_height: int) -> float:
    """
    Estimate total body height in PIXELS using face top and ankle bottom.
    
    Adjusts for the fact that MediaPipe doesn't detect top of head (only eyes/nose).
    """
    # Find topmost visible point (lowest y value among face landmarks)
    face_indices = [0, 1, 4, 7, 8]  # nose, eyes, ears
    top_y_norm = min(landmarks[i]['y'] for i in face_indices)
    
    # Find bottommost point (highest y value among ankles)
    left_ankle_y = landmarks[27]['y']
    right_ankle_y = landmarks[28]['y']
    bottom_y_norm = max(left_ankle_y, right_ankle_y)
    
    # Visible body height in pixels (face top to ankle)
    visible_pixel_height = (bottom_y_norm - top_y_norm) * image_height
    
    # Adjust for hidden top of head
    estimated_total_pixel_height = visible_pixel_height / HEAD_TOP_ADJUSTMENT
    
    return estimated_total_pixel_height


def calculate_measurements(
    landmarks: List[Dict],
    image_shape: Dict,
    user_height_cm: float
) -> Dict:
    """
    Calculate all body measurements in centimeters.
    
    Args:
        landmarks: List of 33 landmark dicts from MediaPipe
        image_shape: Dict with 'width', 'height', 'channels'
        user_height_cm: User's actual height in cm
    
    Returns:
        Dictionary with all measurements, confidence, and notes
    """
    
    image_width = image_shape['width']
    image_height = image_shape['height']
    notes = []
    
    # Step 1: Calculate pixel height and conversion factor
    pixel_height = calculate_pixel_height(landmarks, image_height)
    pixels_per_cm = pixel_height / user_height_cm
    
    # Step 2: Shoulder width (landmarks 11 + 12)
    shoulder_pixel_dist = euclidean_distance(
        landmarks[11], landmarks[12],
        image_width, image_height
    )
    shoulder_width_cm = (shoulder_pixel_dist / pixels_per_cm) * SHOULDER_WIDTH_FACTOR
    
    # Step 3: Hip width (landmarks 23 + 24)
    hip_pixel_dist = euclidean_distance(
        landmarks[23], landmarks[24],
        image_width, image_height
    )
    hip_width_cm = (hip_pixel_dist / pixels_per_cm) * HIP_WIDTH_FACTOR
    
    # Step 4: Chest width (interpolated between shoulders and hips, ~30% down from shoulders)
    # Chest level is approximately 30% of the way from shoulders to hips
    chest_width_cm = shoulder_width_cm * CHEST_WIDTH_FACTOR
    
    # Step 5: Torso length (shoulder midpoint to hip midpoint)
    shoulder_mid_x = (landmarks[11]['x'] + landmarks[12]['x']) / 2
    shoulder_mid_y = (landmarks[11]['y'] + landmarks[12]['y']) / 2
    hip_mid_x = (landmarks[23]['x'] + landmarks[24]['x']) / 2
    hip_mid_y = (landmarks[23]['y'] + landmarks[24]['y']) / 2
    
    torso_pixel_dist = math.sqrt(
        ((hip_mid_x - shoulder_mid_x) * image_width) ** 2 +
        ((hip_mid_y - shoulder_mid_y) * image_height) ** 2
    )
    torso_length_cm = torso_pixel_dist / pixels_per_cm
    
    # Step 6: Arm length (shoulder to wrist, average of left and right)
    left_arm_pixel = euclidean_distance(landmarks[11], landmarks[15], image_width, image_height)
    right_arm_pixel = euclidean_distance(landmarks[12], landmarks[16], image_width, image_height)
    avg_arm_pixel = (left_arm_pixel + right_arm_pixel) / 2
    arm_length_cm = avg_arm_pixel / pixels_per_cm
    
    # Step 7: Confidence score based on landmark visibility
    key_indices = [11, 12, 23, 24, 27, 28]  # shoulders, hips, ankles
    visibilities = [landmarks[i]['visibility'] for i in key_indices]
    confidence_score = sum(visibilities) / len(visibilities)
    
    # Step 8: Add notes/warnings
    if confidence_score < 0.7:
        notes.append("Low landmark confidence — try a clearer image")
    
    if image_width < 400 or image_height < 600:
        notes.append("Small image — accuracy may be reduced")
    
    if shoulder_width_cm < 30 or shoulder_width_cm > 60:
        notes.append("Shoulder measurement unusual — check user height input")
    
    return {
        "shoulder_width_cm": round(shoulder_width_cm, 2),
        "hip_width_cm": round(hip_width_cm, 2),
        "chest_width_cm": round(chest_width_cm, 2),
        "torso_length_cm": round(torso_length_cm, 2),
        "arm_length_cm": round(arm_length_cm, 2),
        "estimated_height_cm": round(pixel_height / pixels_per_cm, 2),
        "pixels_per_cm": round(pixels_per_cm, 4),
        "confidence_score": round(confidence_score, 3),
        "notes": notes
    }