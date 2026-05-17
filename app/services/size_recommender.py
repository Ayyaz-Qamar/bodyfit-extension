"""
Shirt size recommendation engine.
Maps body measurements to standard sizes using industry charts.
"""

from typing import Optional, List, Tuple
from app.config.size_charts import (
    get_size_chart,
    CHEST_WIDTH_TO_CIRCUMFERENCE
)


def calculate_size_match_score(
    chest_circumference: float,
    shoulder_width: float,
    size_ranges: dict
) -> Tuple[float, str]:
    """
    Calculate how well user's measurements match a size's ranges.
    
    Returns:
        (score 0-1, reason string)
    """
    chest_min = size_ranges["chest_min"]
    chest_max = size_ranges["chest_max"]
    shoulder_min = size_ranges["shoulder_min"]
    shoulder_max = size_ranges["shoulder_max"]
    
    # Chest score
    chest_center = (chest_min + chest_max) / 2
    chest_range = chest_max - chest_min
    
    if chest_min <= chest_circumference <= chest_max:
        # Inside range - score based on distance from center
        chest_score = 1.0 - (abs(chest_circumference - chest_center) / (chest_range / 2)) * 0.3
    else:
        # Outside range - penalty based on how far
        if chest_circumference < chest_min:
            distance = chest_min - chest_circumference
        else:
            distance = chest_circumference - chest_max
        chest_score = max(0, 1.0 - (distance / chest_range))
    
    # Shoulder score (same logic)
    shoulder_center = (shoulder_min + shoulder_max) / 2
    shoulder_range = shoulder_max - shoulder_min
    
    if shoulder_min <= shoulder_width <= shoulder_max:
        shoulder_score = 1.0 - (abs(shoulder_width - shoulder_center) / (shoulder_range / 2)) * 0.3
    else:
        if shoulder_width < shoulder_min:
            distance = shoulder_min - shoulder_width
        else:
            distance = shoulder_width - shoulder_max
        shoulder_score = max(0, 1.0 - (distance / shoulder_range))
    
    # Weighted final score (chest is more important than shoulder for shirts)
    final_score = (chest_score * 0.65) + (shoulder_score * 0.35)
    
    # Generate reason
    reason_parts = []
    if chest_min <= chest_circumference <= chest_max:
        reason_parts.append(f"chest ({chest_circumference:.1f}cm) in range")
    else:
        reason_parts.append(f"chest ({chest_circumference:.1f}cm) outside {chest_min}-{chest_max}cm range")
    
    if shoulder_min <= shoulder_width <= shoulder_max:
        reason_parts.append(f"shoulder ({shoulder_width:.1f}cm) in range")
    else:
        reason_parts.append(f"shoulder ({shoulder_width:.1f}cm) outside {shoulder_min}-{shoulder_max}cm range")
    
    reason = "; ".join(reason_parts)
    return final_score, reason


def recommend_shirt_size(
    chest_width_cm: float,
    shoulder_width_cm: float,
    gender: Optional[str] = "male"
) -> dict:
    """
    Recommends a shirt size based on body measurements.
    
    Args:
        chest_width_cm: Front-view chest width
        shoulder_width_cm: Shoulder-to-shoulder distance
        gender: 'male' or 'female'
    
    Returns:
        Dictionary with recommended_size, confidence, alternative sizes, and reasoning
    """
    
    # Convert chest WIDTH to CIRCUMFERENCE (industry standard for sizing)
    chest_circumference = chest_width_cm * CHEST_WIDTH_TO_CIRCUMFERENCE
    
    # Get appropriate size chart
    size_chart = get_size_chart(gender)
    
    # Calculate match scores for all sizes
    size_scores = {}
    size_reasons = {}
    
    for size_name, ranges in size_chart.items():
        score, reason = calculate_size_match_score(
            chest_circumference,
            shoulder_width_cm,
            ranges
        )
        size_scores[size_name] = score
        size_reasons[size_name] = reason
    
    # Sort by score (highest first)
    sorted_sizes = sorted(size_scores.items(), key=lambda x: x[1], reverse=True)
    
    # Best match
    best_size, best_score = sorted_sizes[0]
    
    # Top 3 alternatives
    alternatives = [
        {"size": size, "confidence_score": round(score, 3)}
        for size, score in sorted_sizes[:3]
    ]
    
    # Build human-readable explanation
    explanation_parts = [
        f"Based on chest circumference of {chest_circumference:.1f} cm",
        f"and shoulder width of {shoulder_width_cm:.1f} cm",
        f"size {best_size} is the best match ({size_reasons[best_size]})."
    ]
    explanation = " ".join(explanation_parts)
    
    # Fit advice
    fit_advice = []
    if best_score >= 0.85:
        fit_advice.append("Excellent fit expected.")
    elif best_score >= 0.65:
        fit_advice.append("Good fit, may feel slightly loose or tight.")
    else:
        fit_advice.append("Approximate fit — consider trying both this size and adjacent sizes.")
    
    if best_score < 0.7:
        fit_advice.append("Recommendation: Compare with the alternative sizes above.")
    
    return {
        "recommended_size": best_size,
        "confidence_score": round(best_score, 3),
        "chest_circumference_estimated_cm": round(chest_circumference, 2),
        "alternative_sizes": alternatives,
        "explanation": explanation,
        "fit_advice": " ".join(fit_advice),
        "gender_used": gender if gender else "male"
    }