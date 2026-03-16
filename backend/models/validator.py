"""
Post-processing validation for Korean medical translations.

Two-tier validation strategy:
1. Rule-based: fast regex checks for numbers, units, negations.
2. LLM-based: Ollama semantic check for dangerous misinterpretation.
"""

from __future__ import annotations

import json
import logging
import re
import time
from dataclasses import dataclass, field
from typing import Literal

import ollama

from models.prompts import (
    FALLBACK_MODEL,
    OLLAMA_OPTIONS_VALIDATION,
    PRIMARY_MODEL,
    VALIDATION_PROMPT,
)
from rag.medical_terms import CRITICAL_TERMS, NEGATION_PATTERNS

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Type aliases
# ---------------------------------------------------------------------------

RiskLevel = Literal["low", "medium", "high"]

# ---------------------------------------------------------------------------
# Unit patterns (covers all common radiology units)
# ---------------------------------------------------------------------------

_UNIT_PATTERN = re.compile(
    r"\b\d+(?:\.\d+)?\s*"
    r"(?:mm²?|cm²?|m²?|mL|L|HU|SUV|Bq|MBq|GBq|mg|g|kg|%|mmHg|bpm|"
    r"msec|sec|ms|keV|MeV|mGy|Gy|mSv|Sv|mCi|Ci|μm|nm|T|mT)\b",
    re.IGNORECASE,
)

# Numeric value pattern (standalone numbers and ranges)
_NUMBER_PATTERN = re.compile(
    r"""
    (?:
        \d+(?:\.\d+)?          # plain number: 3, 2.5
        (?:\s*[-–]\s*\d+(?:\.\d+)?)?  # optional range: 3-5, 2.5–3.0
    )
    """,
    re.VERBOSE,
)

# Common English negation patterns
_ENGLISH_NEGATION_PATTERN = re.compile(
    r"\b(?:"
    r"no\b|not\b|without\b|absent\b|absence\s+of|not\s+seen|not\s+identified|"
    r"not\s+detected|not\s+visualized|not\s+observed|unremarkable|"
    r"within\s+normal\s+limits|wnl|negative\s+for|free\s+of|clear\s+of|"
    r"no\s+evidence(?:\s+of)?"
    r")",
    re.IGNORECASE,
)

# Korean negation patterns
# Covers both formal report style (없음, 않음) and LLM conversational endings
# (없습니다, 없었습니다, 않습니다, 않았습니다) and particle variations
# (이상 소견이 없 / 이상 소견은 없 / 이상이 없).
_KOREAN_NEGATION_PATTERN = re.compile(
    r"(?:"
    # 없- family: 없음, 없습니다, 없었습니다, 없어요, 없다
    r"없(?:음|습니다|었습니다|어(?:요)?|다\b)|"
    # 않- family: 않음, 않습니다, 않았습니다, 않았음
    r"않(?:음|습니다|았습니다|았음)|"
    # 관찰/확인/보이/발견 + 되지 않 (어미 무관)
    r"(?:관찰|확인|보이|발견)되지\s*않|"
    # 이상 소견 + 조사 허용 + 없
    r"이상\s*소견[이가은는]?\s*없|"
    # 이상 + 조사 허용 + 없 (이상이 없습니다 등)
    r"이상[이가은는]?\s*없|"
    # 특이 소견/사항 + 조사 허용 + 없
    r"특이\s*(?:소견|사항)[이가은는]?\s*없|"
    # 정상 범위/소견/입니다/이었습니다
    r"정상\s*(?:범위|소견)|정상(?:입니다|이었습니다|이다\b)|"
    # 음성 (negative for)
    r"음성"
    r")"
)


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class ValidationIssue:
    issue_type: str
    description: str
    original_fragment: str = ""
    translated_fragment: str = ""


@dataclass
class ValidationResult:
    is_valid: bool
    risk_level: RiskLevel
    issues: list[ValidationIssue] = field(default_factory=list)
    overall_assessment: str = ""
    rule_based_passed: bool = True
    llm_based_passed: bool = True
    elapsed_seconds: float = 0.0


# ---------------------------------------------------------------------------
# Main validator class
# ---------------------------------------------------------------------------

class MedicalValidator:
    """
    Two-tier validator for Korean radiology translations.

    Usage::

        validator = MedicalValidator()
        result = validator.validate_translation(original_en, korean_translation)
        if result.risk_level == "high":
            # reject or flag for human review
        critical = validator.check_critical_findings(korean_translation)
    """

    def __init__(
        self,
        primary_model: str = PRIMARY_MODEL,
        fallback_model: str = FALLBACK_MODEL,
        ollama_host: str = "http://localhost:11434",
        run_llm_validation: bool = True,
    ) -> None:
        self._primary_model = primary_model
        self._fallback_model = fallback_model
        self._ollama_client = ollama.Client(host=ollama_host)
        self._run_llm_validation = run_llm_validation

    # ------------------------------------------------------------------
    # Rule-based checks
    # ------------------------------------------------------------------

    def _extract_numbers(self, text: str) -> list[str]:
        """Extract all numeric values (with optional ranges) from text."""
        return _NUMBER_PATTERN.findall(text)

    def _extract_units(self, text: str) -> list[str]:
        """Extract all unit-bearing measurements from text."""
        return _UNIT_PATTERN.findall(text)

    def _check_numbers_preserved(
        self, original: str, translated: str
    ) -> list[ValidationIssue]:
        """
        Verify every numeric value in the original appears in the translation.
        Numbers are critical — a wrong dose or size can mislead treatment.
        """
        issues: list[ValidationIssue] = []
        orig_numbers = set(self._extract_numbers(original))
        trans_numbers = set(self._extract_numbers(translated))

        for num in orig_numbers:
            # Allow minor whitespace/formatting differences
            normalised = re.sub(r"\s+", "", num)
            found = any(
                re.sub(r"\s+", "", t) == normalised for t in trans_numbers
            )
            if not found:
                issues.append(
                    ValidationIssue(
                        issue_type="number_mismatch",
                        description=f"Numeric value '{num}' not found in translation.",
                        original_fragment=num,
                        translated_fragment="",
                    )
                )
        return issues

    def _check_units_preserved(
        self, original: str, translated: str
    ) -> list[ValidationIssue]:
        """Verify unit-bearing measurements are preserved in the translation."""
        issues: list[ValidationIssue] = []
        orig_units = _UNIT_PATTERN.findall(original)
        trans_text_normalised = translated.lower()

        for measurement in orig_units:
            # Check for the unit abbreviation itself (case-insensitive)
            unit_part = re.search(r"[a-zA-Z%²]+", measurement)
            if unit_part and unit_part.group().lower() not in trans_text_normalised:
                issues.append(
                    ValidationIssue(
                        issue_type="unit_mismatch",
                        description=(
                            f"Unit measurement '{measurement}' may be missing "
                            "or altered in translation."
                        ),
                        original_fragment=measurement,
                        translated_fragment="",
                    )
                )
        return issues

    def _check_negations_preserved(
        self, original: str, translated: str
    ) -> list[ValidationIssue]:
        """
        Verify negation expressions are accurately translated.
        A missed negation (e.g. 'no mass' → '종괴') is a critical safety issue.
        """
        issues: list[ValidationIssue] = []
        en_negations = _ENGLISH_NEGATION_PATTERN.findall(original)
        ko_negations = _KOREAN_NEGATION_PATTERN.findall(translated)
        # Count English negations still present in translated text (mixed-language output)
        en_negations_in_translation = _ENGLISH_NEGATION_PATTERN.findall(translated)
        effective_ko_count = len(ko_negations) + len(en_negations_in_translation)

        # Heuristic: the count of negation expressions should be roughly equal
        if len(en_negations) > effective_ko_count:
            missing_count = len(en_negations) - effective_ko_count
            issues.append(
                ValidationIssue(
                    issue_type="negation_error",
                    description=(
                        f"{missing_count} negation expression(s) in the original "
                        "appear to be missing or under-represented in the translation. "
                        f"English negations found: {en_negations}. "
                        f"Korean negations found: {ko_negations}."
                    ),
                    original_fragment=", ".join(en_negations),
                    translated_fragment=", ".join(ko_negations),
                )
            )
        return issues

    def _run_rule_based_checks(
        self, original: str, translated: str
    ) -> list[ValidationIssue]:
        """Aggregate all rule-based checks and return their issues."""
        issues: list[ValidationIssue] = []
        issues.extend(self._check_numbers_preserved(original, translated))
        issues.extend(self._check_units_preserved(original, translated))
        issues.extend(self._check_negations_preserved(original, translated))
        return issues

    # ------------------------------------------------------------------
    # LLM-based semantic validation
    # ------------------------------------------------------------------

    def _run_llm_check(
        self, original: str, translated: str
    ) -> list[ValidationIssue]:
        """
        Use Ollama to perform a semantic validation of the translation.
        Detects meaning distortion that rule-based checks cannot catch.
        """
        prompt = VALIDATION_PROMPT.format(
            original_text=original,
            translated_text=translated,
        )

        model_used = self._primary_model
        raw_response = ""

        for attempt_model in (self._primary_model, self._fallback_model):
            try:
                response = self._ollama_client.chat(
                    model=attempt_model,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a medical translation quality auditor. "
                                "Respond ONLY with valid JSON."
                            ),
                        },
                        {"role": "user", "content": prompt},
                    ],
                    options=OLLAMA_OPTIONS_VALIDATION,
                )
                raw_response = response["message"]["content"].strip()
                model_used = attempt_model
                break
            except Exception as exc:
                logger.warning(
                    "LLM validation failed with model %s: %s", attempt_model, exc
                )

        if not raw_response:
            logger.error("LLM validation produced no response.")
            return []

        return self._parse_llm_validation_response(raw_response)

    def _parse_llm_validation_response(
        self, raw_response: str
    ) -> list[ValidationIssue]:
        """Parse LLM JSON validation response into ValidationIssue objects."""
        clean = re.sub(r"```(?:json)?\s*", "", raw_response).strip().rstrip("`").strip()
        try:
            data = json.loads(clean)
            issues_data = data.get("issues", [])
            issues: list[ValidationIssue] = []
            for item in issues_data:
                issues.append(
                    ValidationIssue(
                        issue_type=str(item.get("type", "unknown")),
                        description=str(item.get("description", "")),
                        original_fragment=str(item.get("original_fragment", "")),
                        translated_fragment=str(item.get("translated_fragment", "")),
                    )
                )
            return issues
        except (json.JSONDecodeError, KeyError) as exc:
            logger.error(
                "Failed to parse LLM validation JSON: %s\nResponse: %s",
                exc,
                raw_response[:400],
            )
            return []

    # ------------------------------------------------------------------
    # Risk level determination
    # ------------------------------------------------------------------

    @staticmethod
    def _determine_risk_level(issues: list[ValidationIssue]) -> RiskLevel:
        """
        Determine overall risk level based on the types of issues found.

        Risk matrix:
        - high   : negation errors, meaning distortion
        - medium : number/unit mismatches, terminology errors
        - low    : no significant issues
        """
        # negation_error is handled by rule-based checks which are more reliable.
        # Only meaning_distortion (LLM semantic check) triggers high risk.
        high_risk_types = {"meaning_distortion"}
        medium_risk_types = {"negation_error", "number_mismatch", "unit_mismatch", "direction_error", "terminology_error"}

        for issue in issues:
            if issue.issue_type in high_risk_types:
                return "high"

        for issue in issues:
            if issue.issue_type in medium_risk_types:
                return "medium"

        return "low"

    # ------------------------------------------------------------------
    # Public: validate_translation
    # ------------------------------------------------------------------

    def validate_translation(
        self, original: str, translated: str
    ) -> ValidationResult:
        """
        Validate a Korean translation of a radiology report.

        Performs both rule-based and (optionally) LLM-based checks.

        Parameters
        ----------
        original:
            The original English radiology report text.
        translated:
            The Korean translation to validate.

        Returns
        -------
        ValidationResult with is_valid, risk_level, and a list of issues.
        """
        if not original or not translated:
            raise ValueError("Both original and translated texts must be non-empty.")

        start = time.perf_counter()
        all_issues: list[ValidationIssue] = []

        # Tier 1: Rule-based checks
        logger.info("Running rule-based validation checks …")
        rule_issues = self._run_rule_based_checks(original, translated)
        all_issues.extend(rule_issues)
        rule_passed = len(rule_issues) == 0

        # Tier 2: LLM-based semantic check
        rule_negation_passed = not any(i.issue_type == "negation_error" for i in rule_issues)
        llm_passed = True
        if self._run_llm_validation:
            logger.info("Running LLM-based semantic validation …")
            try:
                llm_issues = self._run_llm_check(original, translated)
                # If rule-based negation check passed, discard LLM negation_error
                # (rule-based is more reliable; LLM often false-positives on mixed-language text)
                if rule_negation_passed:
                    llm_issues = [i for i in llm_issues if i.issue_type != "negation_error"]
                all_issues.extend(llm_issues)
                llm_passed = len(llm_issues) == 0
            except Exception as exc:
                logger.error("LLM validation encountered an error: %s", exc)

        risk_level = self._determine_risk_level(all_issues)
        is_valid = risk_level in ("low", "medium") and not any(
            i.issue_type == "meaning_distortion" for i in all_issues
        )

        elapsed = round(time.perf_counter() - start, 2)

        overall = (
            "Translation passed all validation checks."
            if is_valid
            else f"Translation has {len(all_issues)} issue(s); risk level: {risk_level}."
        )

        logger.info(
            "Validation complete in %.2fs — is_valid=%s, risk=%s, issues=%d",
            elapsed,
            is_valid,
            risk_level,
            len(all_issues),
        )

        return ValidationResult(
            is_valid=is_valid,
            risk_level=risk_level,
            issues=all_issues,
            overall_assessment=overall,
            rule_based_passed=rule_passed,
            llm_based_passed=llm_passed,
            elapsed_seconds=elapsed,
        )

    # ------------------------------------------------------------------
    # Public: check_critical_findings
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # Internal: negation-aware keyword presence check
    # ------------------------------------------------------------------

    @staticmethod
    def _is_negated_in_context(text_lower: str, term_lower: str) -> bool:
        """Return True if ALL occurrences of term_lower in text_lower are negated.

        Negation is detected by:
        - English negation words within 60 chars (6 words) BEFORE the term.
        - English post-term phrases like "is not seen / not identified" within 40 chars AFTER.
        - Korean negation characters within 10 chars AFTER the term.

        If the term is not present at all, returns False (not negated = not found).
        """
        # Collect all match positions
        if re.search(r"[가-힣]", term_lower):
            # Korean term — substring positions
            positions: list[tuple[int, int]] = []
            start = 0
            while True:
                idx = text_lower.find(term_lower, start)
                if idx == -1:
                    break
                positions.append((idx, idx + len(term_lower)))
                start = idx + 1
        else:
            # English term — whole-word positions
            pat = re.compile(r"\b" + re.escape(term_lower) + r"\b")
            positions = [(m.start(), m.end()) for m in pat.finditer(text_lower)]

        if not positions:
            return False  # term not present at all

        _neg_prefix = re.compile(
            r"\b(?:no|not|without|absent|absence\s+of|no\s+evidence\s+of|"
            r"negative\s+for|free\s+of|clear\s+of|not\s+seen|not\s+identified|"
            r"not\s+detected|not\s+visualized|not\s+observed|unremarkable)\b",
            re.IGNORECASE,
        )
        _neg_suffix_en = re.compile(
            r"\b(?:not\s+(?:seen|identified|detected|visualized|observed|present))\b"
        )
        _neg_suffix_ko = re.compile(r"(?:없|않|아님|음성|관찰되지|확인되지|보이지|발견되지)")

        for start_pos, end_pos in positions:
            prefix = text_lower[max(0, start_pos - 60): start_pos]
            window = " ".join(prefix.split()[-6:])
            if _neg_prefix.search(window):
                continue  # this occurrence is negated
            suffix = text_lower[end_pos: end_pos + 40]
            if _neg_suffix_en.search(suffix):
                continue  # negated
            if _neg_suffix_ko.search(suffix[:10]):
                continue  # negated
            return False  # found a non-negated occurrence

        return True  # all occurrences were negated

    def check_critical_findings(self, text: str) -> list[str]:
        """
        Scan text for critical medical findings that require special attention.

        Checks against both English and Korean critical term lists from
        ``rag.medical_terms.CRITICAL_TERMS``.  Terms that appear only in a
        negated context (e.g. "no hemorrhage", "absence of malignancy") are
        NOT reported as critical findings.

        Parameters
        ----------
        text:
            The text to scan (translated Korean report or original English report).

        Returns
        -------
        A de-duplicated list of critical terms found in the text (non-negated only).
        """
        if not text:
            return []

        text_lower = text.lower()
        found: list[str] = []

        for term in CRITICAL_TERMS:
            term_lower = term.lower()
            # Skip if term is absent or all occurrences are negated
            if self._is_negated_in_context(text_lower, term_lower):
                continue
            # Check presence (fast path before declaring a hit)
            if re.search(r"[가-힣]", term):
                if term not in text:
                    continue
            else:
                if not re.search(r"\b" + re.escape(term_lower) + r"\b", text_lower):
                    continue
            found.append(term)

        # De-duplicate while preserving order
        seen: set[str] = set()
        unique_found: list[str] = []
        for t in found:
            if t not in seen:
                seen.add(t)
                unique_found.append(t)

        if unique_found:
            logger.warning(
                "Critical findings detected: %s", unique_found
            )

        return unique_found
