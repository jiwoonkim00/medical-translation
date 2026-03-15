"""
Medical radiology report translation pipeline.

Architecture:
1. Language detection (regex heuristic — no external API needed)
2. If English input:
   a. Helsinki-NLP/opus-mt-en-ko (HuggingFace transformers) → fast base translation
   b. Ollama qwen2.5:14b → medical terminology refinement
3. If Korean input:
   → Ollama qwen2.5:14b → light proofreading / standardisation pass
4. Patient-friendly explanation → Ollama qwen2.5:14b
"""

from __future__ import annotations

import json
import logging
import re
import time
from dataclasses import dataclass, field
from typing import Any

import ollama
from transformers import MarianMTModel, MarianTokenizer

from models.prompts import (
    FALLBACK_MODEL,
    OLLAMA_OPTIONS,
    PATIENT_EXPLANATION_SYSTEM_PROMPT,
    PATIENT_EXPLANATION_USER_TEMPLATE,
    PRIMARY_MODEL,
    TRANSLATION_REFINEMENT_PROMPT,
    TRANSLATION_SYSTEM_PROMPT,
)
from rag.vectorstore import MedicalRAG

logger = logging.getLogger(__name__)

# Helsinki-NLP model for English → Korean base translation
_HELSINKI_MODEL_NAME = "Helsinki-NLP/opus-mt-en-ko"

# Heuristic: if >30% of alphanumeric characters are Korean (Hangul), treat as Korean
_KOREAN_CHAR_RATIO_THRESHOLD = 0.30

# Maximum token length for Helsinki model (MarianMT hard limit is 512)
_MAX_HELSINKI_TOKENS = 480


@dataclass
class TranslationResult:
    """Structured output of a translation pipeline run."""

    original_text: str
    translated_text: str
    source_language: str          # "en" or "ko"
    model_used: str               # Ollama model name that did the refinement
    draft_translation: str = ""   # Raw Helsinki output (only populated for en→ko)
    elapsed_seconds: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PatientExplanation:
    """Structured patient explanation output."""

    summary: str
    key_findings: list[str]
    patient_explanation: str
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

        # Helsinki-NLP components (loaded lazily by load_models())
        self._helsinki_tokenizer: MarianTokenizer | None = None
        self._helsinki_model: MarianMTModel | None = None

        # Ollama client
        self._ollama_client = ollama.Client(host=ollama_host)

        self._models_loaded = False

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def load_models(self) -> None:
        """
        Download / load the Helsinki-NLP MarianMT model into memory.
        Call this once at application startup before handling requests.
        """
        if self._models_loaded:
            logger.debug("Models already loaded — skipping.")
            return

        logger.info("Loading Helsinki-NLP model: %s …", _HELSINKI_MODEL_NAME)
        try:
            self._helsinki_tokenizer = MarianTokenizer.from_pretrained(
                _HELSINKI_MODEL_NAME
            )
            self._helsinki_model = MarianMTModel.from_pretrained(
                _HELSINKI_MODEL_NAME
            )
            self._helsinki_model.eval()  # inference mode
            logger.info("Helsinki-NLP model loaded successfully.")
        except Exception as exc:
            logger.error(
                "Failed to load Helsinki-NLP model: %s. "
                "Base translation step will be skipped.",
                exc,
            )

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
    # Helsinki-NLP base translation (English → Korean)
    # ------------------------------------------------------------------

    def _helsinki_translate(self, text: str) -> str:
        """
        Translate English text to Korean using Helsinki-NLP/opus-mt-en-ko.

        Handles long texts by chunking at sentence boundaries to stay within
        the MarianMT 512-token limit.
        """
        if self._helsinki_tokenizer is None or self._helsinki_model is None:
            logger.warning(
                "Helsinki-NLP model not available — skipping base translation."
            )
            return text

        # Split into sentences to avoid exceeding the token limit
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        chunks: list[str] = []
        current_chunk: list[str] = []
        current_length = 0

        for sentence in sentences:
            token_count = len(self._helsinki_tokenizer.encode(sentence))
            if current_length + token_count > _MAX_HELSINKI_TOKENS and current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = [sentence]
                current_length = token_count
            else:
                current_chunk.append(sentence)
                current_length += token_count

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        translated_chunks: list[str] = []
        for chunk in chunks:
            try:
                inputs = self._helsinki_tokenizer(
                    [chunk],
                    return_tensors="pt",
                    padding=True,
                    truncation=True,
                    max_length=512,
                )
                translated_tokens = self._helsinki_model.generate(
                    **inputs,
                    num_beams=4,
                    early_stopping=True,
                )
                decoded = self._helsinki_tokenizer.batch_decode(
                    translated_tokens, skip_special_tokens=True
                )
                translated_chunks.append(decoded[0])
            except Exception as exc:
                logger.error("Helsinki translation chunk failed: %s", exc)
                translated_chunks.append(chunk)  # fallback: keep original

        return " ".join(translated_chunks)

    # ------------------------------------------------------------------
    # Ollama helpers
    # ------------------------------------------------------------------

    def _ollama_chat(
        self,
        system_prompt: str,
        user_message: str,
        model: str | None = None,
    ) -> tuple[str, str]:
        """
        Send a chat request to Ollama and return ``(response_text, model_used)``.
        Automatically falls back to ``_fallback_model`` on error.
        """
        target_model = model or self._primary_model

        for attempt_model in (target_model, self._fallback_model):
            try:
                response = self._ollama_client.chat(
                    model=attempt_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message},
                    ],
                    options=OLLAMA_OPTIONS,
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

        # 1. Language detection
        lang = source_lang if source_lang in ("en", "ko") else self._detect_language(text)
        logger.info("translate() called — detected language: %s", lang)

        draft_translation = ""
        refined_translation = ""
        model_used = self._primary_model

        rag_context = self._get_rag_context(text)

        if lang == "en":
            # Step 2a: Helsinki-NLP base translation
            logger.info("Step 1: Helsinki-NLP base translation …")
            draft_translation = self._helsinki_translate(text)
            logger.info("Draft translation length: %d chars", len(draft_translation))

            # Step 2b: Ollama refinement
            logger.info("Step 2: Ollama medical terminology refinement …")
            refinement_user_msg = TRANSLATION_REFINEMENT_PROMPT.format(
                original_text=text,
                draft_translation=draft_translation,
                rag_context=rag_context,
            )
            refined_translation, model_used = self._ollama_chat(
                system_prompt=TRANSLATION_SYSTEM_PROMPT,
                user_message=refinement_user_msg,
            )

        else:  # Korean input — proofreading / standardisation only
            logger.info("Input is Korean — running Ollama standardisation pass …")
            standardise_msg = (
                "다음 한국어 방사선 판독문을 표준 한국어 의학 용어로 교정하고 "
                "자연스러운 판독 문체로 다듬어 주세요. "
                "숫자, 단위, 부위명, 부정 표현은 절대 변경하지 마세요.\n\n"
                f"원문:\n{text}\n\n"
                f"{rag_context}"
            )
            refined_translation, model_used = self._ollama_chat(
                system_prompt=TRANSLATION_SYSTEM_PROMPT,
                user_message=standardise_msg,
            )

        elapsed = time.perf_counter() - start
        logger.info(
            "Translation complete in %.2fs using model '%s'.", elapsed, model_used
        )

        return TranslationResult(
            original_text=text,
            translated_text=refined_translation,
            source_language=lang,
            model_used=model_used,
            draft_translation=draft_translation,
            elapsed_seconds=round(elapsed, 2),
            metadata={"rag_terms_retrieved": rag_context != "RAG context not available."},
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

        Parameters
        ----------
        translated_text:
            Korean translation of the radiology report.
        original_text:
            Original English (or Korean) radiology report for reference.

        Returns
        -------
        PatientExplanation with summary, key_findings, and patient_explanation.
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
        )

        # Parse JSON response
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
        # Strip markdown code fences if present
        clean = re.sub(r"```(?:json)?\s*", "", raw_response).strip().rstrip("`").strip()

        try:
            data = json.loads(clean)
            return PatientExplanation(
                summary=str(data.get("summary", "")),
                key_findings=[str(f) for f in data.get("key_findings", [])],
                patient_explanation=str(data.get("patient_explanation", "")),
                raw_json=raw_response,
                model_used=model_used,
            )
        except json.JSONDecodeError as exc:
            logger.error(
                "Failed to parse patient explanation JSON: %s\nRaw response:\n%s",
                exc,
                raw_response[:500],
            )
            # Graceful degradation: return raw response as explanation
            return PatientExplanation(
                summary="판독 결과 요약을 생성하는 중 오류가 발생했습니다.",
                key_findings=[],
                patient_explanation=raw_response,
                raw_json=raw_response,
                model_used=model_used,
            )
