# Explanation generation for recommendations
# app/explanation.py

from typing import Dict, Any

def build_explanation(
patient,
profile,
bmi: float,
bmi_category: str,
age_category: str,
final_daily_calories: int,
meal_targets: dict,
selected_menus: dict,
score_traces: dict,
constraints: list,
):
"""
Human-readable explanation saved into Recommendation.explanation_json
"""

```
recommendations = {}

for meal_time, menu in selected_menus.items():

    if menu is None:
        recommendations[meal_time] = {
            "menu": None,
            "reason": "No suitable menu found. Dietitian action required."
        }
        continue

    recommendations[meal_time] = {
        "menu": menu.menu_name,
        "menu_code": menu.menu_code,
        "calories": menu.calories_kcal,
        "score_reasons": score_traces.get(meal_time, [])
    }

return {
    "patient_name": patient.full_name,
    "patient_code": patient.patient_code,
    "bmi": bmi,
    "bmi_category": bmi_category,
    "age_category": age_category,
    "daily_calories": final_daily_calories,
    "meal_targets": meal_targets,
    "constraints": constraints,
    "recommendations": recommendations,
}
```
