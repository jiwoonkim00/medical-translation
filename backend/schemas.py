"""
Pydantic request / response schemas for the Medical Translation API.

All models use strict typing and include field-level documentation so that
FastAPI's auto-generated OpenAPI docs are self-explanatory.
"""

from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from config import MAX_TEXT_LENGTH


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class SourceLang(str, Enum):
    """Source language of the radiology report."""

    en = "en"
    ko = "ko"
    auto = "auto"


class TranslationMode(str, Enum):
    """Controls how much additional information is returned alongside the
    core translation.

    - ``translation_only`` – bare translation, fastest.
    - ``with_explanation`` – translation + patient-friendly explanation.
    - ``full`` – translation + explanation + medical validation.
    """

    translation_only = "translation_only"
    with_explanation = "with_explanation"
    full = "full"


class RiskLevel(str, Enum):
    """Clinical risk classification produced by the validator."""

    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


# ---------------------------------------------------------------------------
# Sub-models
# ---------------------------------------------------------------------------


class PatientExplanation(BaseModel):
    """Lay-language explanation of the radiology report for patients."""

    summary: str = Field(
        ...,
        description="One-sentence plain-language summary of the overall findings.",
    )
    key_findings: List[str] = Field(
        default_factory=list,
        description="Bullet-point key findings expressed in non-technical language.",
    )
    patient_text: str = Field(
        ...,
        description=(
            "Full patient-friendly explanation written in Korean, "
            "avoiding medical jargon."
        ),
    )


class ValidationResult(BaseModel):
    """Quality and safety validation of the translation."""

    is_valid: bool = Field(
        ...,
        description="True when the translation passes all automated checks.",
    )
    issues: List[str] = Field(
        default_factory=list,
        description="List of human-readable validation issues found.",
    )
    risk_level: RiskLevel = Field(
        default=RiskLevel.low,
        description="Estimated clinical risk level of the original report.",
    )
    confidence_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Model confidence in the translation quality (0–1), if available.",
    )


# ---------------------------------------------------------------------------
# /api/translate
# ---------------------------------------------------------------------------


class TranslateRequest(BaseModel):
    """Request body for POST /api/translate."""

    text: str = Field(
        ...,
        min_length=1,
        description="Raw radiology report text to translate.",
        examples=["Chest CT: No acute cardiopulmonary process identified."],
    )
    source_lang: SourceLang = Field(
        default=SourceLang.auto,
        description="Source language of *text*. Use 'auto' for automatic detection.",
    )
    mode: TranslationMode = Field(
        default=TranslationMode.translation_only,
        description="Controls the depth of the response.",
    )
    patient_name: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Optional patient name used to personalise the patient explanation.",
    )

    @field_validator("text")
    @classmethod
    def text_length(cls, v: str) -> str:
        if len(v) > MAX_TEXT_LENGTH:
            raise ValueError(
                f"Text exceeds the maximum allowed length of {MAX_TEXT_LENGTH} characters."
            )
        return v.strip()


class TranslateResponse(BaseModel):
    """Full response from POST /api/translate."""

    original: str = Field(..., description="The original input text (stripped).")
    translated: str = Field(..., description="Korean translation of the report.")
    patient_explanation: Optional[PatientExplanation] = Field(
        default=None,
        description="Patient-friendly explanation (present for 'with_explanation' and 'full' modes).",
    )
    validation: Optional[ValidationResult] = Field(
        default=None,
        description="Translation validation result (present for 'full' mode only).",
    )
    critical_findings: List[str] = Field(
        default_factory=list,
        description=(
            "List of critical/urgent findings that may require immediate attention. "
            "Always present; empty list when nothing critical is detected."
        ),
    )
    processing_time_ms: int = Field(
        ...,
        description="Wall-clock time taken to process the request, in milliseconds.",
    )


# ---------------------------------------------------------------------------
# /api/validate
# ---------------------------------------------------------------------------


class ValidateRequest(BaseModel):
    """Request body for POST /api/validate."""

    original: str = Field(
        ...,
        min_length=1,
        description="The original source text.",
    )
    translated: str = Field(
        ...,
        min_length=1,
        description="The translated text to validate against the original.",
    )

    @field_validator("original", "translated")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        return v.strip()


class ValidateResponse(BaseModel):
    """Response from POST /api/validate (validation result only)."""

    validation: ValidationResult


# ---------------------------------------------------------------------------
# /api/health
# ---------------------------------------------------------------------------


class ModelStatus(BaseModel):
    """Status of a single backing model / service."""

    status: str = Field(..., description="'connected', 'loaded', 'unavailable', etc.")
    detail: Optional[str] = Field(
        default=None, description="Additional detail or error message."
    )


class HealthResponse(BaseModel):
    """Response from GET /api/health."""

    status: str = Field(..., description="Overall service status ('ok' or 'degraded').")
    models: dict[str, str] = Field(
        ...,
        description="Mapping of model/service name to its current status string.",
    )
    version: str = Field(
        default="1.0.0",
        description="API version string.",
    )


# ---------------------------------------------------------------------------
# /api/terms/search
# ---------------------------------------------------------------------------


class MedicalTerm(BaseModel):
    """A single medical terminology entry returned by the search endpoint."""

    term: str = Field(..., description="The medical term (typically English).")
    korean: str = Field(..., description="Official Korean translation of the term.")
    definition: str = Field(
        default="",
        description="Plain-language definition of the term.",
    )
    category: Optional[str] = Field(
        default=None,
        description="Clinical category (e.g., 'Pulmonary', 'Oncology').",
    )
    synonyms: List[str] = Field(
        default_factory=list,
        description="Alternate spellings or abbreviations.",
    )
    score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Relevance score from the vector search (0–1).",
    )


class TermSearchResponse(BaseModel):
    """Response from GET /api/terms/search."""

    query: str = Field(..., description="The search query that was used.")
    results: List[MedicalTerm] = Field(
        default_factory=list,
        description="List of matching medical terms, ordered by relevance.",
    )
    total: int = Field(..., description="Total number of results returned.")


# ---------------------------------------------------------------------------
# Generic error response (used in exception handlers)
# ---------------------------------------------------------------------------


class ErrorResponse(BaseModel):
    """Standard error envelope returned on 4xx / 5xx responses."""

    error: str = Field(..., description="Short machine-readable error code.")
    message: str = Field(..., description="Human-readable error description.")
    detail: Optional[str] = Field(
        default=None,
        description="Additional diagnostic detail (omitted in production).",
    )
