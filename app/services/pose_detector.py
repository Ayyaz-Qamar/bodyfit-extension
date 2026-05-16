"""
Pose detection service using MediaPipe.
Extracts 33 body landmarks from an image.
"""
import cv2
import mediapipe as mp


# MediaPipe modules - global, reused across calls
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils


def detect_pose_from_image(image_path: str) -> dict:
    """
    Detects 33 body landmarks from an image file.
    
    Args:
        image_path: Path to image file (jpg/png)
    
    Returns:
        Dictionary with success, landmarks, image_shape, or error
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
            "error": "No pose detected. Ensure full body visible with good lighting."
        }
    
    # Step 5: Extract landmark coordinates
    landmarks = []
    for idx, lm in enumerate(results.pose_landmarks.landmark):
        landmarks.append({
            "index": idx,
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


# Test code - runs only when this file is executed directly
if __name__ == "__main__":
    print("🤖 Testing pose detection...")
    print("=" * 60)
    
    test_image = "uploads/test_image.jpg"
    output_image = "uploads/test_image_with_pose.jpg"
    
    # Test 1: Detect landmarks
    result = detect_pose_from_image(test_image)
    
    if not result["success"]:
        print(f"❌ Error: {result['error']}")
    else:
        print(f"✅ SUCCESS! Detected {len(result['landmarks'])} landmarks")
        print(f"📐 Image size: {result['image_shape']['width']}x{result['image_shape']['height']} pixels")
        print()
        print("First 5 landmarks (sample):")
        for lm in result["landmarks"][:5]:
            print(f"  [{lm['index']:2d}] x={lm['x']:.3f}, y={lm['y']:.3f}, visibility={lm['visibility']:.3f}")
        
        print()
        print("Key body landmarks:")
        key_indices = {11: "Left Shoulder", 12: "Right Shoulder", 23: "Left Hip", 24: "Right Hip"}
        for idx, name in key_indices.items():
            lm = result["landmarks"][idx]
            print(f"  {name:18s}: x={lm['x']:.3f}, y={lm['y']:.3f}, visibility={lm['visibility']:.3f}")
        
        # Test 2: Visualization
        print()
        print("🎨 Creating visualization...")
        if visualize_pose_on_image(test_image, output_image):
            print(f"✅ Visualization saved to: {output_image}")
            print("👉 Open this file in VS Code or File Explorer to see the magic!")
        else:
            print("❌ Visualization failed")