"""
Industry-standard shirt size charts.
Based on common Pakistani/international men's and women's sizing.
"""

# Conversion factor: chest WIDTH (front view) to chest CIRCUMFERENCE
# Industry average ~2.2 (depends on body type)
CHEST_WIDTH_TO_CIRCUMFERENCE = 2.2

# Male shirt size chart (chest circumference in cm)
MALE_SIZE_CHART = {
    "XS":  {"chest_min": 80, "chest_max": 85, "shoulder_min": 38, "shoulder_max": 40},
    "S":   {"chest_min": 86, "chest_max": 91, "shoulder_min": 41, "shoulder_max": 43},
    "M":   {"chest_min": 92, "chest_max": 97, "shoulder_min": 44, "shoulder_max": 46},
    "L":   {"chest_min": 98, "chest_max": 104, "shoulder_min": 47, "shoulder_max": 49},
    "XL":  {"chest_min": 105, "chest_max": 112, "shoulder_min": 50, "shoulder_max": 52},
    "XXL": {"chest_min": 113, "chest_max": 120, "shoulder_min": 53, "shoulder_max": 55},
    "3XL": {"chest_min": 121, "chest_max": 130, "shoulder_min": 56, "shoulder_max": 58},
}

# Female shirt size chart
FEMALE_SIZE_CHART = {
    "XS":  {"chest_min": 75, "chest_max": 81, "shoulder_min": 34, "shoulder_max": 36},
    "S":   {"chest_min": 82, "chest_max": 87, "shoulder_min": 37, "shoulder_max": 39},
    "M":   {"chest_min": 88, "chest_max": 93, "shoulder_min": 40, "shoulder_max": 42},
    "L":   {"chest_min": 94, "chest_max": 100, "shoulder_min": 43, "shoulder_max": 45},
    "XL":  {"chest_min": 101, "chest_max": 108, "shoulder_min": 46, "shoulder_max": 48},
    "XXL": {"chest_min": 109, "chest_max": 116, "shoulder_min": 49, "shoulder_max": 51},
}

# Default to male if gender not specified
DEFAULT_SIZE_CHART = MALE_SIZE_CHART


def get_size_chart(gender: str = None) -> dict:
    """Returns appropriate size chart based on gender."""
    if gender and gender.lower() == "female":
        return FEMALE_SIZE_CHART
    return MALE_SIZE_CHART