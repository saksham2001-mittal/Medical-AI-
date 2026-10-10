from typing import Dict, Any

def interpret_test_result( comparison: Dict[str, Any], medical_context: str = "") -> Dict[str, Any]:

    if not comparison:
        return {
            "interpretation": "Unknown",
            "reason": "No comparison data available."
        }

    test_name = comparison.get("test_name")
    latest_value = comparison.get("latest_value")
    previous_value = comparison.get("previous_value")
    latest_change = comparison.get("latest_change")
    overall_trend = comparison.get("overall_trend")
    latest_status = comparison.get("latest_status")
    reference_range = comparison.get("reference_range")

    return {
        "test_name": test_name,
        "latest_value": latest_value,
        "previous_value": previous_value,
        "latest_change": latest_change,
        "overall_trend": overall_trend,
        "latest_status": latest_status,
        "reference_range": reference_range,
        "medical_context": medical_context,
        "interpretation": "Unknown",
    }