# app/rules.py

from datetime import datetime
from typing import Dict, List, Tuple


# ==========================================================
# BMI RULES (R1-R4)
# ==========================================================

def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    """
    R1:
    BMI = weight / height(m)^2
    """
    if not weight_kg or not height_cm:
        return 0.0

    height_m = float(height_cm) / 100
    return round(float(weight_kg) / (height_m ** 2), 2)


def get_bmi_category(bmi: float) -> str:
    """
    R2-R4
    """
    if bmi < 18.5:
        return "underweight"

    if bmi < 25:
        return "normal"

    return "overweight"


# ==========================================================
# AGE CATEGORY RULES (R5-R7)
# ==========================================================

def get_age_category(age: int) -> str:
    if 7 <= age < 13:
        return "child"

    if 13 <= age < 18:
        return "teenager"

    return "adult"


# ==========================================================
# CALORIE FACTOR RULES (R8-R16)
# ==========================================================

CALORIE_FACTORS = {
    ("overweight", "sedentary"): 20,
    ("overweight", "moderate"): 22,
    ("overweight", "active"): 25,

    ("normal", "sedentary"): 30,
    ("normal", "moderate"): 35,
    ("normal", "active"): 40,

    ("underweight", "sedentary"): 35,
    ("underweight", "moderate"): 40,
    ("underweight", "active"): 45,
}


def get_calorie_factor(
    bmi_category: str,
    activity_level: str
) -> int:

    return CALORIE_FACTORS.get(
        (bmi_category.lower(), activity_level.lower()),
        30
    )


# ==========================================================
# DAILY CALORIE RULES (R17-R27)
# ==========================================================

def calculate_daily_calories(
    weight_kg: float,
    age_category: str,
    patient_category: str,
    calorie_factor: int,
    pregnancy_trimester: int | None = None
) -> int:
    """
    Returns Final Daily Calories
    """
    # R17
    base_daily_calories = float(weight_kg) * calorie_factor

    # R18-R20
    if age_category == "child":
        age_adjusted = base_daily_calories * 0.80

    elif age_category == "teenager":
        age_adjusted = base_daily_calories * 0.90

    else:
        age_adjusted = base_daily_calories

    adjustment = 0

    # R21-R26
    if patient_category == "pregnant":

        if pregnancy_trimester == 1:
            adjustment = 300

        elif pregnancy_trimester == 2:
            adjustment = 350

        elif pregnancy_trimester == 3:
            adjustment = 500

    elif patient_category == "pre-operation":
        adjustment = -200

    elif patient_category == "post-operation":
        adjustment = 200

    final_daily_calories = age_adjusted + adjustment

    return int(round(final_daily_calories))


# ==========================================================
# MEAL TARGET RULES (R28-R30)
# ==========================================================

def calculate_meal_targets(
    final_daily_calories: int
) -> Dict[str, int]:

    return {
        "breakfast": int(round(final_daily_calories * 0.25)),
        "lunch": int(round(final_daily_calories * 0.40)),
        "dinner": int(round(final_daily_calories * 0.35)),
    }


# ==========================================================
# MENU DAY RULES (R41-R44)
# ==========================================================

def get_cycle_day(
    current_date: datetime | None = None
) -> int:

    if current_date is None:
        current_date = datetime.now()

    weekday = current_date.weekday()

    # Monday=0 Tuesday=1 Wednesday=2 Thursday=3
    # Friday=4 Saturday=5 Sunday=6

    mapping = {
        6: 1,  # Sunday
        3: 1,  # Thursday

        0: 2,  # Monday
        4: 2,  # Friday

        1: 3,  # Tuesday
        5: 3,  # Saturday

        2: 4,  # Wednesday
    }

    return mapping[weekday]


# ==========================================================
# MEDICAL CONSTRAINTS
# ==========================================================

def build_constraints(profile) -> List[str]:

    constraints = []

    if profile.has_diabetes:
        constraints.append("low_sugar")

    if profile.has_hypertension:
        constraints.append("low_sodium")

    if profile.has_high_cholesterol:
        constraints.append("low_fat")

    if profile.is_vegetarian:
        constraints.append("vegetarian")

    if profile.has_chewing_problem:
        constraints.append("chewing")

    if profile.patient_category == "pregnant":
        constraints.append("pregnant")

    if profile.patient_category == "pre-operation":
        constraints.append("pre_operation")
        constraints.append("low_fibre")   # R47

    if profile.patient_category == "post-operation":
        constraints.append("post_operation")

    return constraints


# ==========================================================
# SAFETY FILTERS
# ==========================================================

def passes_constraints(
    menu,
    profile
) -> Tuple[bool, List[str]]:

    reasons = []

    # Diabetes
    if profile.has_diabetes and menu.sugar_level.lower() == "high":
        reasons.append("high sugar")

    # Hypertension
    if profile.has_hypertension and menu.sodium_level.lower() == "high":
        reasons.append("high sodium")

    # Cholesterol
    if profile.has_high_cholesterol and menu.fat_level.lower() == "high":
        reasons.append("high fat")

    # Vegetarian
    if profile.is_vegetarian and not menu.vegetarian:
        reasons.append("not vegetarian")

    # Chewing problem
    if profile.has_chewing_problem and not menu.suitable_chewing:
        reasons.append("not chewing friendly")

    # Low fibre (pre-operation) — R47 / R57
    if (
        profile.patient_category == "pre-operation"
        and menu.fibre_level.lower() != "low"
    ):
        reasons.append("not low fibre")

    # Pregnancy
    if (
        profile.patient_category == "pregnant"
        and not menu.suitable_pregnant
    ):
        reasons.append("not suitable for pregnancy")

    # Pre-op
    if (
        profile.patient_category == "pre-operation"
        and not menu.suitable_preop
    ):
        reasons.append("not suitable for pre-operation")

    # Post-op
    if (
        profile.patient_category == "post-operation"
        and not menu.suitable_postop
    ):
        reasons.append("not suitable for post-operation")

    # Allergies
    patient_allergies = {
        allergy.lower()
        for allergy in (profile.allergies or [])
    }

    menu_allergies = {
        allergy.lower()
        for allergy in (menu.allergy_tags or [])
    }

    if patient_allergies.intersection(menu_allergies):
        reasons.append("contains allergy ingredient")

    return len(reasons) == 0, reasons


# ==========================================================
# SCORING RULES (R59-R63)
# ==========================================================

def score_menu(
    menu,
    profile
) -> tuple[int, List[str]]:

    score = 0
    trace = []

    # R59
    if (
        profile.preferred_protein
        and profile.preferred_protein != "none"
        and menu.protein_type == profile.preferred_protein
    ):
        score += 30
        trace.append("+30 preferred protein")

    # R60
    if (
        profile.preferred_carbohydrate
        and profile.preferred_carbohydrate != "none"
        and menu.carbohydrate_type == profile.preferred_carbohydrate
    ):
        score += 20
        trace.append("+20 preferred carbohydrate")

    # R61
    if (
        profile.is_vegetarian
        and menu.vegetarian
    ):
        score += 10
        trace.append("+10 vegetarian match")

    # R62
    if (
        profile.patient_category == "post-operation"
        and menu.protein_level.lower() == "high"
    ):
        score += 40
        trace.append("+40 post-op high protein")

    # R63
    if score == 0:
        trace.append("+0 no preference match")

    return score, trace
