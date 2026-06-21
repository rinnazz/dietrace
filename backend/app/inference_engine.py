# Inference engine for menu recommendations
# app/inference_engine.py

from datetime import datetime
from sqlalchemy.orm import Session

from app.models import (
Patient,
PatientHealthProfile,
MenuOption,
Recommendation,
RecommendationItem,
ApprovalHistory,
)

from app.rules import (
calculate_bmi,
get_bmi_category,
get_age_category,
get_calorie_factor,
calculate_daily_calories,
calculate_meal_targets,
get_cycle_day,
build_constraints,
passes_constraints,
score_menu,
)

from app.explanation import build_explanation

def generate_recommendation(
db: Session,
patient_id,
):
"""
Main Forward Chaining Engine
"""

```
# ======================================================
# Load Patient
# ======================================================

patient = (
    db.query(Patient)
    .filter(Patient.id == patient_id)
    .first()
)

if not patient:
    raise ValueError("Patient not found")

profile = (
    db.query(PatientHealthProfile)
    .filter(PatientHealthProfile.patient_id == patient.id)
    .first()
)

if not profile:
    raise ValueError("Patient health profile not found")

# ======================================================
# Generate Facts
# ======================================================

bmi = calculate_bmi(
    profile.weight_kg,
    profile.height_cm,
)

bmi_category = get_bmi_category(bmi)

age_category = get_age_category(patient.age)

calorie_factor = get_calorie_factor(
    bmi_category,
    profile.activity_level,
)

final_daily_calories = calculate_daily_calories(
    weight_kg=profile.weight_kg,
    age_category=age_category,
    patient_category=profile.patient_category,
    calorie_factor=calorie_factor,
    pregnancy_trimester=profile.pregnancy_trimester,
)

meal_targets = calculate_meal_targets(
    final_daily_calories
)

constraints = build_constraints(profile)

cycle_day = get_cycle_day()

# ======================================================
# Candidate Search
# ======================================================

selected_menus = {}
score_traces = {}
recommendation_items = []

meal_types = [
    "breakfast",
    "lunch",
    "dinner",
]

no_suitable_alert = {}

for meal_time in meal_types:

    menus = (
        db.query(MenuOption)
        .filter(
            MenuOption.cycle_day == cycle_day,
            MenuOption.meal_time == meal_time,
            MenuOption.is_active == True,
        )
        .all()
    )

    candidates = []

    for menu in menus:

        passed, reject_reasons = passes_constraints(
            menu,
            profile,
        )

        if not passed:
            continue

        score, trace = score_menu(
            menu,
            profile,
        )

        candidates.append(
            {
                "menu": menu,
                "score": score,
                "trace": trace,
            }
        )

    # ==================================================
    # R65
    # ==================================================

    if not candidates:

        selected_menus[meal_time] = None

        score_traces[meal_time] = [
            "No suitable menu found"
        ]

        no_suitable_alert[meal_time] = True

        continue

    # ==================================================
    # R64
    # ==================================================

    best_candidate = max(
        candidates,
        key=lambda x: x["score"]
    )

    selected_menus[meal_time] = best_candidate["menu"]

    score_traces[meal_time] = best_candidate["trace"]

    no_suitable_alert[meal_time] = False

# ======================================================
# Recommendation Status
# ======================================================

if any(no_suitable_alert.values()):
    status = "needs_dietitian_action"
else:
    status = "pending_review"

# ======================================================
# Rule Trace
# ======================================================

rule_trace = {
    "bmi": bmi,
    "bmi_category": bmi_category,
    "age_category": age_category,
    "calorie_factor": calorie_factor,
    "daily_calories": final_daily_calories,
    "constraints": constraints,
    "meal_scores": score_traces,
}

# ======================================================
# Explanation
# ======================================================

explanation_json = build_explanation(
    patient=patient,
    profile=profile,
    bmi=bmi,
    bmi_category=bmi_category,
    age_category=age_category,
    final_daily_calories=final_daily_calories,
    meal_targets=meal_targets,
    selected_menus=selected_menus,
    score_traces=score_traces,
    constraints=constraints,
)

# ======================================================
# Save Recommendation
# ======================================================

recommendation = Recommendation(
    patient_id=patient.id,
    cycle_day=cycle_day,
    status=status,
    generated_at=datetime.utcnow(),
    rule_trace_json=rule_trace,
    explanation_json=explanation_json,
    no_suitable_alert_json=no_suitable_alert,
)

db.add(recommendation)
db.flush()

# ======================================================
# Save Items
# ======================================================

for meal_time in meal_types:

    menu = selected_menus.get(meal_time)

    item = RecommendationItem(
        recommendation_id=recommendation.id,
        meal_time=meal_time,
        menu_option_id=menu.id if menu else None,
        selection_reason=", ".join(
            score_traces.get(meal_time, [])
        ),
        is_modified=False,
    )

    db.add(item)

# ======================================================
# Approval History
# ======================================================

history = ApprovalHistory(
    recommendation_id=recommendation.id,
    action="generated",
    note="Recommendation generated by expert system",
)

db.add(history)

db.commit()
db.refresh(recommendation)

return recommendation
```
