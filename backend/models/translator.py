"""
Medical radiology report translation pipeline.

Architecture:
1. Language detection (regex heuristic — no external API needed)
2. If English input:
   a. RAG glossary scan → retrieve relevant medical term translations
   b. Ollama qwen2.5:7b → direct English→Korean translation with RAG context
3. If Korean input:
   → Ollama qwen2.5:7b → light proofreading / standardisation pass
4. Patient-friendly explanation → Ollama qwen2.5:7b
"""

from __future__ import annotations

import json
import logging
import re
import time
from dataclasses import dataclass, field
from typing import Any

import ollama

from models.prompts import (
    FALLBACK_MODEL,
    OLLAMA_OPTIONS,
    OLLAMA_OPTIONS_EXPLANATION,
    PATIENT_EXPLANATION_SYSTEM_PROMPT,
    PATIENT_EXPLANATION_USER_TEMPLATE,
    PRIMARY_MODEL,
    TRANSLATION_USER_PROMPT,
    TRANSLATION_SYSTEM_PROMPT,
)
from rag.vectorstore import MedicalRAG

logger = logging.getLogger(__name__)

# Heuristic: if >30% of alphanumeric characters are Korean (Hangul), treat as Korean
_KOREAN_CHAR_RATIO_THRESHOLD = 0.30


@dataclass
class TranslationResult:
    """Structured output of a translation pipeline run."""

    original_text: str
    translated_text: str
    source_language: str          # "en" or "ko"
    model_used: str               # Ollama model name that did the translation
    draft_translation: str = ""   # Kept for API compatibility (always empty now)
    elapsed_seconds: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PatientExplanation:
    """Structured patient explanation output."""

    summary: str
    key_findings: list[str]
    patient_explanation: str
    recommendations: list[str] = field(default_factory=list)
    raw_json: str = ""
    model_used: str = ""
    elapsed_seconds: float = 0.0


class MedicalTranslator:
    """
    End-to-end pipeline for translating radiology reports into Korean
    and generating patient-friendly explanations.

    Usage::

        translator = MedicalTranslator()
        translator.load_models()

        result = translator.translate("Chest CT shows a 1.2 cm nodule in the right upper lobe.")
        explanation = translator.generate_patient_explanation(
            result.translated_text, result.original_text
        )
    """

    def __init__(
        self,
        rag: MedicalRAG | None = None,
        primary_model: str = PRIMARY_MODEL,
        fallback_model: str = FALLBACK_MODEL,
        ollama_host: str = "http://localhost:11434",
    ) -> None:
        self._rag = rag
        self._primary_model = primary_model
        self._fallback_model = fallback_model
        self._ollama_host = ollama_host

        # Ollama client
        self._ollama_client = ollama.Client(host=ollama_host)

        self._models_loaded = False

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def load_models(self) -> None:
        """
        Verify Ollama connectivity.
        Call this once at application startup before handling requests.
        """
        if self._models_loaded:
            logger.debug("Models already loaded — skipping.")
            return

        logger.info("Verifying Ollama connectivity (model: %s) …", self._primary_model)
        try:
            self._ollama_client.list()
            logger.info("Ollama connected successfully.")
        except Exception as exc:
            logger.error("Ollama connection failed: %s", exc)

        self._models_loaded = True

    # ------------------------------------------------------------------
    # Language detection
    # ------------------------------------------------------------------

    @staticmethod
    def _detect_language(text: str) -> str:
        """
        Heuristic language detection.

        Returns ``"ko"`` if the text contains a significant proportion of
        Hangul characters, otherwise ``"en"``.
        """
        hangul_chars = re.findall(r"[\uAC00-\uD7A3\u1100-\u11FF\u3130-\u318F]", text)
        alnum_chars = re.findall(r"[a-zA-Z0-9\uAC00-\uD7A3]", text)
        if not alnum_chars:
            return "en"
        ratio = len(hangul_chars) / len(alnum_chars)
        detected = "ko" if ratio >= _KOREAN_CHAR_RATIO_THRESHOLD else "en"
        logger.debug(
            "Language detection: ratio=%.2f → %s", ratio, detected
        )
        return detected

    # ------------------------------------------------------------------
    # RAG context injection
    # ------------------------------------------------------------------

    def _get_rag_context(self, text: str) -> str:
        """Return a formatted RAG context string, or empty string if RAG is unavailable."""
        if self._rag is None or not self._rag.is_ready:
            return "RAG context not available."
        try:
            terms = self._rag.get_relevant_terms(text, n_results=6)
            if not terms:
                return "관련 의학 용어 정보를 찾을 수 없습니다."
            lines = ["[관련 의학 용어 참고]"]
            for t in terms:
                lines.append(f"- {t['term_en']} → {t['term_ko']}: {t['patient_friendly']}")
            return "\n".join(lines)
        except Exception as exc:
            logger.warning("RAG context retrieval failed: %s", exc)
            return "RAG context retrieval failed."

    # ------------------------------------------------------------------
    # Ollama helpers
    # ------------------------------------------------------------------

    def _ollama_chat(
        self,
        system_prompt: str,
        user_message: str,
        model: str | None = None,
        options: dict | None = None,
    ) -> tuple[str, str]:
        """
        Send a chat request to Ollama and return ``(response_text, model_used)``.
        Automatically falls back to ``_fallback_model`` on error.
        """
        target_model = model or self._primary_model
        chat_options = options if options is not None else OLLAMA_OPTIONS

        for attempt_model in (target_model, self._fallback_model):
            try:
                response = self._ollama_client.chat(
                    model=attempt_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message},
                    ],
                    options=chat_options,
                )
                content: str = response["message"]["content"].strip()
                logger.debug(
                    "Ollama [%s] responded (%d chars).", attempt_model, len(content)
                )
                return content, attempt_model
            except Exception as exc:
                logger.warning(
                    "Ollama request failed with model %s: %s. "
                    "Trying fallback …",
                    attempt_model,
                    exc,
                )

        raise RuntimeError(
            "All Ollama models failed. Ensure Ollama is running and models are pulled."
        )

    # ------------------------------------------------------------------
    # Deterministic post-processing corrections
    # ------------------------------------------------------------------

    # Lobe abbreviations that must always be translated
    _LOBE_ABBREV: dict[str, str] = {
        "RUL": "우상엽",
        "LUL": "좌상엽",
        "RML": "우중엽",
        "RLL": "우하엽",
        "LLL": "좌하엽",
    }

    # Known mistranslations: pattern → correct Korean
    _KNOWN_ERRORS: list[tuple[str, str]] = [
        (r"중심성\s*폐렴", "국소 폐렴"),
        (r"CT\s*흉부", "흉부 CT"),
        (r"CT\s*복부", "복부 CT"),
        (r"CT\s*뇌", "뇌 CT"),
        (r"MRI\s*뇌", "뇌 MRI"),
        (r"MRI\s*척추", "척추 MRI"),
        (r"MRI\s*흉부", "흉부 MRI"),
        (r"소형\s*폐\s*결절", "작은 폐결절"),
        (r"크기\s*소소", "작은 크기"),
    ]

    @staticmethod
    def _pair_bilingual(original: str, translated: str) -> list[dict[str, str]]:
        """
        Pair English source lines with Korean translated lines for bilingual display.
        Uses newline-based splitting — radiology reports are line-structured so
        line counts typically match 1-to-1.
        """
        def split_lines(text: str) -> list[str]:
            return [l.rstrip() for l in text.strip().split("\n")]

        en_lines = split_lines(original)
        ko_lines = split_lines(translated)

        pairs: list[dict[str, str]] = []
        max_len = max(len(en_lines), len(ko_lines))
        for i in range(max_len):
            en = en_lines[i] if i < len(en_lines) else ""
            ko = ko_lines[i] if i < len(ko_lines) else ""
            pairs.append({"en": en, "ko": ko})

        return pairs

    @classmethod
    def _apply_corrections(cls, text: str) -> str:
        """
        Deterministic post-processing:
        1. Replace lobe abbreviations (RUL→우상엽, etc.)
        2. Fix known mistranslation patterns
        """
        # 1. Lobe abbreviations — word-boundary aware
        for abbrev, korean in cls._LOBE_ABBREV.items():
            text = re.sub(r"\b" + abbrev + r"\b", korean, text)

        # 2. Known mistranslations
        for pattern, replacement in cls._KNOWN_ERRORS:
            text = re.sub(pattern, replacement, text)

        return text

    # ------------------------------------------------------------------
    # Chinese contamination filter
    # ------------------------------------------------------------------

    @staticmethod
    def _strip_chinese_contamination(text: str) -> str:
        """
        If the model output contains Chinese characters mixed with Korean,
        attempt to extract only the Korean portion.
        """
        chinese_char_re = re.compile(r"[\u4E00-\u9FFF\u3400-\u4DBF\uF900-\uFAFF]+")
        if not chinese_char_re.search(text):
            return text

        logger.warning("Chinese characters detected in model output — attempting cleanup.")

        matches = list(chinese_char_re.finditer(text))
        if matches:
            last_match = matches[-1]
            after = text[last_match.end():]
            after = re.sub(r"^[\s：:：。，、\n]+", "", after)
            if len(after.strip()) > 50:
                logger.info("Extracted post-Chinese Korean content (%d chars).", len(after))
                return after.strip()

        cleaned = chinese_char_re.sub("", text)
        logger.info("Stripped Chinese characters in place (%d chars remaining).", len(cleaned))
        return cleaned.strip()

    # ------------------------------------------------------------------
    # Public: translate
    # ------------------------------------------------------------------

    def translate(
        self,
        text: str,
        source_lang: str = "auto",
    ) -> TranslationResult:
        """
        Translate a radiology report text to Korean.

        Parameters
        ----------
        text:
            The input text (English or Korean radiology report).
        source_lang:
            ``"auto"`` (default) to auto-detect, ``"en"`` to force English,
            or ``"ko"`` to force Korean.

        Returns
        -------
        TranslationResult with the translated text and metadata.
        """
        if not text or not text.strip():
            raise ValueError("Input text must not be empty.")

        start = time.perf_counter()

        lang = source_lang if source_lang in ("en", "ko") else self._detect_language(text)
        logger.info("translate() called — detected language: %s", lang)

        rag_context = self._get_rag_context(text)
        translated = ""
        model_used = self._primary_model
        metadata: dict[str, Any] = {"rag_terms_retrieved": rag_context != "RAG context not available."}

        if lang == "en":
            logger.info("Direct Ollama translation (en→ko) …")
            user_msg = TRANSLATION_USER_PROMPT.format(
                rag_context=rag_context,
                original_text=text,
            )
            translated, model_used = self._ollama_chat(
                system_prompt=TRANSLATION_SYSTEM_PROMPT,
                user_message=user_msg,
            )
            translated = self._strip_chinese_contamination(translated)
            translated = self._apply_corrections(translated)
            metadata["bilingual"] = self._pair_bilingual(text, translated)

        else:  # Korean input — proofreading / standardisation only
            logger.info("Input is Korean — running Ollama standardisation pass …")
            standardise_msg = (
                "다음 한국어 방사선 판독문을 표준 한국어 의학 용어로 교정하고 "
                "자연스러운 판독 문체로 다듬어 주세요. "
                "숫자, 단위, 부위명, 부정 표현은 절대 변경하지 마세요.\n\n"
                "CRITICAL: 출력은 반드시 순수한 한국어(한글)로만 작성하세요. "
                "중국어 한자(漢字/中文) 또는 일본어를 절대 사용하지 마세요. "
                "한자가 포함된 단어는 반드시 한글로 바꿔 쓰세요.\n\n"
                f"원문:\n{text}\n\n"
                f"{rag_context}"
            )
            translated, model_used = self._ollama_chat(
                system_prompt=TRANSLATION_SYSTEM_PROMPT,
                user_message=standardise_msg,
            )
            translated = self._strip_chinese_contamination(translated)
            translated = self._apply_corrections(translated)

        elapsed = time.perf_counter() - start
        logger.info(
            "Translation complete in %.2fs using model '%s'.", elapsed, model_used
        )

        return TranslationResult(
            original_text=text,
            translated_text=translated,
            source_language=lang,
            model_used=model_used,
            elapsed_seconds=round(elapsed, 2),
            metadata=metadata,
        )

    # ------------------------------------------------------------------
    # Public: generate_patient_explanation
    # ------------------------------------------------------------------

    def generate_patient_explanation(
        self,
        translated_text: str,
        original_text: str,
    ) -> PatientExplanation:
        """
        Generate a structured, patient-friendly Korean explanation of a radiology report.
        """
        if not translated_text or not translated_text.strip():
            raise ValueError("translated_text must not be empty.")

        start = time.perf_counter()

        user_message = PATIENT_EXPLANATION_USER_TEMPLATE.format(
            translated_text=translated_text,
            original_text=original_text,
        )

        logger.info("Generating patient explanation …")
        raw_response, model_used = self._ollama_chat(
            system_prompt=PATIENT_EXPLANATION_SYSTEM_PROMPT,
            user_message=user_message,
            options=OLLAMA_OPTIONS_EXPLANATION,
        )

        explanation = self._parse_patient_explanation(raw_response, model_used)
        explanation.elapsed_seconds = round(time.perf_counter() - start, 2)

        logger.info(
            "Patient explanation generated in %.2fs.", explanation.elapsed_seconds
        )
        return explanation

    def _parse_patient_explanation(
        self, raw_response: str, model_used: str
    ) -> PatientExplanation:
        """
        Parse the LLM JSON response into a PatientExplanation dataclass.
        Falls back to a structured error response if JSON parsing fails.
        """
        clean = re.sub(r"```(?:json)?\s*", "", raw_response).strip().rstrip("`").strip()

        try:
            data = json.loads(clean)
            return PatientExplanation(
                summary=str(data.get("summary", "")),
                key_findings=[str(f) for f in data.get("key_findings", [])],
                patient_explanation=str(data.get("patient_explanation", "")),
                recommendations=[str(r) for r in data.get("recommendations", [])],
                raw_json=raw_response,
                model_used=model_used,
            )
        except json.JSONDecodeError as exc:
            logger.error(
                "Failed to parse patient explanation JSON: %s\nRaw response:\n%s",
                exc,
                raw_response[:500],
            )
            return PatientExplanation(
                summary="판독 결과 요약을 생성하는 중 오류가 발생했습니다.",
                key_findings=[],
                patient_explanation=raw_response,
                raw_json=raw_response,
                model_used=model_used,
            )
