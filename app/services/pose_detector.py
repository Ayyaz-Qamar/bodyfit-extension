"""
Pose detection service using MediaPipe.
Extracts 33 body landmarks from an image.
"""

import cv2
import mediapipe as mp


# MediaPipe modules - global, reused across calls
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils


# Human-readable names for 33 MediaPipe pose landmarks
LANDMARK_NAMES = {
    0: "Nose",
    1: "Left Eye Inner", 2: "Left Eye", 3: "Left Eye Outer",
    4: "Right Eye Inner", 5: "Right Eye", 6: "Right Eye Outer",
    7: "Left Ear", 8: "Right Ear",
    9: "Mouth Left", 10: "Mouth Right",
    11: "Left Shoulder", 12: "Right Shoulder",
    13: "Left Elbow", 14: "Right Elbow",
    15: "Left Wrist", 16: "Right Wrist",
    17: "Left Pinky", 18: "Right Pinky",
    19: "Left Index", 20: "Right Index",
    21: "Left Thumb", 22: "Right Thumb",
    23: "Left Hip", 24: "Right Hip",
    25: "Left Knee", 26: "Right Knee",
    27: "Left Ankle", 28: "Right Ankle",
    29: "Left Heel", 30: "Right Heel",
    31: "Left Foot Index", 32: "Right Foot Index"
}


def detect_pose_from_image(image_path: str) -> dict:
    """
    Detects 33 body landmarks from an image file.
    
    Args:
        image_path: Path to image file (jpg/png)
    
    Returns:
        Dictionary with success status, landmarks list, image_shape, or error message
    """
    
    # Step 1: Read image with OpenCV
    image = cv2.imread(image_path)
    if image is None:
        return {
            "success": False,
            "error": f"Could not read image at {image_path}"
        }
    
    # Step 2: Convert BGR to RGB (OpenCV uses BGR, MediaPipe needs RGB)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Step 3: Initialize MediaPipe Pose and process
    with mp_pose.Pose(
        static_image_mode=True,
        model_complexity=1,
        enable_segmentation=False,
        min_detection_confidence=0.5
    ) as pose:
        results = pose.process(image_rgb)
    
    # Step 4: Check if pose was detected
    if not results.pose_landmarks:
        return {
            "success": False,
            "error": "No pose detected. Ensure full body is visible with good lighting."
        }
    
    # Step 5: Extract landmark coordinates with human-readable names
    landmarks = []
    for idx, lm in enumerate(results.pose_landmarks.landmark):
        landmarks.append({
            "index": idx,
            "name": LANDMARK_NAMES.get(idx, f"Unknown_{idx}"),
            "x": round(lm.x, 4),
            "y": round(lm.y, 4),
            "z": round(lm.z, 4),
            "visibility": round(lm.visibility, 4)
        })
    
    return {
        "success": True,
        "landmarks": landmarks,
        "image_shape": {
            "height": image.shape[0],
            "width": image.shape[1],
            "channels": image.shape[2]
        }
    }


def visualize_pose_on_image(image_path: str, output_path: str) -> bool:
    """
    Draws pose landmarks and connections on image, saves to output_path.
    
    Args:
        image_path: Input image path
        output_path: Where to save annotated image
    
    Returns:
        True if successful, False if pose not detected
    """
    
    image = cv2.imread(image_path)
    if image is None:
        return False
    
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    with mp_pose.Pose(
        static_image_mode=True,
        model_complexity=1,
        min_detection_confidence=0.5
    ) as pose:
        results = pose.process(image_rgb)
    
    if not results.pose_landmarks:
        return False
    
    # Draw landmarks (green dots) and connections (blue lines)
    mp_drawing.draw_landmarks(
        image,
        results.pose_landmarks,
        mp_pose.POSE_CONNECTIONS,
        landmark_drawing_spec=mp_drawing.DrawingSpec(
            color=(0, 255, 0),
            thickness=4,
            circle_radius=4
        ),
        connection_drawing_spec=mp_drawing.DrawingSpec(
            color=(255, 0, 0),
            thickness=2
        )
    )
    
    cv2.imwrite(output_path, image)
    return True