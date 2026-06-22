# SQLAlchemy ORM models
import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, Text, text, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Dietitian(Base):
    __tablename__ = "dietitians"

    id: Mapped[uuid.UUID] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    full_name: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[Optional[str]] = mapped_column(Text, unique=True)
    username: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    reviewed_recommendations: Mapped[list["Recommendation"]] = relationship(
        back_populates="reviewer"
    )
    approval_actions: Mapped[list["ApprovalHistory"]] = relationship(
        back_populates="action_by_dietitian"
    )


class MenuOption(Base):
    __tablename__ = "menu_options"

    id: Mapped[uuid.UUID] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    menu_code: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    cycle_day: Mapped[int] = mapped_column(Integer, nullable=False)
    meal_time: Mapped[str] = mapped_column(Text, nullable=False)
    menu_name: Mapped[str] = mapped_column(Text, nullable=False)
    calories_kcal: Mapped[Optional[int]] = mapped_column(Integer)
    sugar_level: Mapped[str] = mapped_column(Text, nullable=False)
    sodium_level: Mapped[str] = mapped_column(Text, nullable=False)
    fat_level: Mapped[str] = mapped_column(Text, nullable=False)
    allergy_tags: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    vegetarian: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    suitable_chewing: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    protein_type: Mapped[str] = mapped_column(
        Text, nullable=False, default="none"
    )
    protein_level: Mapped[str] = mapped_column(
        Text, nullable=False, default="low"
    )
    carbohydrate_type: Mapped[str] = mapped_column(
        Text, nullable=False, default="none"
    )
    carbohydrate_level: Mapped[str] = mapped_column(
        Text, nullable=False, default="low"
    )
    fibre_level: Mapped[str] = mapped_column(
        Text, nullable=False, default="low"
    )
    oil_level: Mapped[str] = mapped_column(
        Text, nullable=False, default="low"
    )
    suitable_pregnant: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    suitable_preop: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    suitable_postop: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    suitability_notes: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    recommendation_items: Mapped[list["RecommendationItem"]] = relationship(
        back_populates="menu_option"
    )


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[uuid.UUID] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    patient_code: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    full_name: Mapped[str] = mapped_column(Text, nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    gender: Mapped[str] = mapped_column(Text, nullable=False)
    ward: Mapped[Optional[str]] = mapped_column(Text)
    admission_date: Mapped[Optional[date]] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    health_profile: Mapped[Optional["PatientHealthProfile"]] = relationship(
        back_populates="patient", uselist=False
    )
    recommendations: Mapped[list["Recommendation"]] = relationship(
        back_populates="patient"
    )


class PatientHealthProfile(Base):
    __tablename__ = "patient_health_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        String(36), ForeignKey("patients.id"), nullable=False, unique=True
    )
    weight_kg: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    height_cm: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    has_diabetes: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    has_hypertension: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    has_high_cholesterol: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    allergies: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    activity_level: Mapped[str] = mapped_column(
        Text, nullable=False, default="sedentary"
    )
    is_vegetarian: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    has_chewing_problem: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    preferred_protein: Mapped[str] = mapped_column(
        Text, nullable=False, default="none"
    )
    preferred_carbohydrate: Mapped[str] = mapped_column(
        Text, nullable=False, default="none"
    )
    patient_category: Mapped[str] = mapped_column(
        Text, nullable=False, default="normal"
    )
    pregnancy_trimester: Mapped[Optional[int]] = mapped_column(Integer)
    smokes: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    sleep_pattern: Mapped[str] = mapped_column(
        Text, nullable=False, default="normal"
    )
    notes: Mapped[Optional[str]] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    patient: Mapped["Patient"] = relationship(back_populates="health_profile")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[uuid.UUID] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        String(36), ForeignKey("patients.id"), nullable=False
    )
    cycle_day: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(
        Text, nullable=False, default="pending_review"
    )
    generated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    reviewed_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        String(36), ForeignKey("dietitians.id")
    )
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    review_note: Mapped[Optional[str]] = mapped_column(Text)
    rule_trace_json: Mapped[Any] = mapped_column(
        JSON, nullable=False, default=dict
    )
    explanation_json: Mapped[Any] = mapped_column(
        JSON, nullable=False, default=dict
    )
    no_suitable_alert_json: Mapped[Any] = mapped_column(
        JSON, nullable=False, default=dict
    )

    patient: Mapped["Patient"] = relationship(back_populates="recommendations")
    reviewer: Mapped[Optional["Dietitian"]] = relationship(
        back_populates="reviewed_recommendations"
    )
    items: Mapped[list["RecommendationItem"]] = relationship(
        back_populates="recommendation"
    )
    approval_history: Mapped[list["ApprovalHistory"]] = relationship(
        back_populates="recommendation"
    )


class RecommendationItem(Base):
    __tablename__ = "recommendation_items"

    id: Mapped[uuid.UUID] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    recommendation_id: Mapped[uuid.UUID] = mapped_column(
        String(36), ForeignKey("recommendations.id"), nullable=False
    )
    meal_time: Mapped[str] = mapped_column(Text, nullable=False)
    menu_option_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        String(36), ForeignKey("menu_options.id")
    )
    selection_reason: Mapped[Optional[str]] = mapped_column(Text)
    is_modified: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    modified_menu_name: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    recommendation: Mapped["Recommendation"] = relationship(back_populates="items")
    menu_option: Mapped[Optional["MenuOption"]] = relationship(
        back_populates="recommendation_items"
    )


class ApprovalHistory(Base):
    __tablename__ = "approval_history"

    id: Mapped[uuid.UUID] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    recommendation_id: Mapped[uuid.UUID] = mapped_column(
        String(36), ForeignKey("recommendations.id"), nullable=False
    )
    action: Mapped[str] = mapped_column(Text, nullable=False)
    action_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        String(36), ForeignKey("dietitians.id")
    )
    action_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    note: Mapped[Optional[str]] = mapped_column(Text)

    recommendation: Mapped["Recommendation"] = relationship(
        back_populates="approval_history"
    )
    action_by_dietitian: Mapped[Optional["Dietitian"]] = relationship(
        back_populates="approval_actions"
    )
