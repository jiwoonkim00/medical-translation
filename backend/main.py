"""
Medical Radiology Report Korean Translation – FastAPI Application
=================================================================

Entry point:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000

Architecture notes:
- Models (MedicalTranslator, MedicalValidator, MedicalRAG) are loaded lazily
  on the *first* request so that the server starts instantly even when GPU
  warm-up takes tens of seconds.
- All synchronous model calls are offloaded to a thread-pool via
  ``asyncio.to_thread`` so the event loop is never blocked.
- A single asyncio.Lock guards the lazy-initialisation section to prevent
  duplicate loading when concurrent requests arrive before the first load
  completes.
"""

from __future__ import annotations

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from typing import Any, Optional

import httpx
from fastapi import FastAPI, HTTPException, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import config
from schemas import (
    BilingualLine,
    ErrorResponse,
    HealthResponse,
    MedicalTerm,
    RiskLevel,
    TermSearchResponse,
    TranslateRequest,
    TranslateResponse,
    ValidateRequest,
    ValidateResponse,
    ValidationResult,
    PatientExplanation,
)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL, logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("medical_translation")

# ---------------------------------------------------------------------------
# Lazy-loaded model singletons
# ---------------------------------------------------------------------------

_translator: Optional[Any] = None  # MedicalTranslator instance
_validator: Optional[Any] = None   # MedicalValidator instance
_rag: Optional[Any] = None         # MedicalRAG instance
_init_lock = asyncio.Lock()
_models_ready = False


async def _ensure_models_loaded() -> None:
    """Initialise all ML models exactly once, even under concurrent load."""
    global _translator, _validator, _rag, _models_ready

    if _models_ready:
        return

    async with _init_lock:
        # Double-checked locking – another coroutine may have loaded while we
        # were waiting for the lock.
        if _models_ready:
            return

        logger.info("Initialising ML models (first request) …")
        t0 = time.perf_counter()

        try:
            # Import here so startup is not delayed by heavy imports
            from models.translator import MedicalTranslator  # type: ignore
            from models.validator import MedicalValidator    # type: ignore
            from rag.vectorstore import MedicalRAG           # type: ignore

            def _load_translator() -> "MedicalTranslator":
                t = MedicalTranslator()
                t.load_models()
                return t

            _translator = await asyncio.to_thread(_load_translator)
            logger.info("MedicalTranslator loaded.")

            _validator = await asyncio.to_thread(MedicalValidator)
            logger.info("MedicalValidator loaded.")

            _rag = await asyncio.to_thread(
                MedicalRAG,
                db_path=config.CHROMA_PERSIST_DIR,
            )
            logger.info("MedicalRAG loaded.")

            # Populate vector store with medical terminology on first run.
            await asyncio.to_thread(_rag.initialize)
            logger.info("RAG vectorstore initialised.")

            _models_ready = True
            elapsed = (time.perf_counter() - t0) * 1000
            logger.info("All models ready in %.0f ms.", elapsed)

        except Exception as exc:
            logger.exception("Failed to load models: %s", exc)
            # Re-raise so the request gets a 503 rather than a silent hang.
            raise


# ---------------------------------------------------------------------------
# Application lifespan
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan context manager (replaces on_event decorators)."""
    logger.info(
        "Medical Translation API starting up. "
        "Models will load lazily on the first request."
    )
    yield
    logger.info("Medical Translation API shutting down.")


# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Medical Radiology Report Translation API",
    description=(
        "Translates radiology reports from English to Korean, "
        "generates patient-friendly explanations, and validates translation quality."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Request logging middleware
# ---------------------------------------------------------------------------


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log every request with method, path, status code, and elapsed time."""
    t0 = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - t0) * 1000
    logger.info(
        "%s %s → %d (%.0f ms)",
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
    )
    return response


# ---------------------------------------------------------------------------
# Global exception handlers
# ---------------------------------------------------------------------------


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="internal_server_error",
            message="An unexpected error occurred. Please try again.",
            detail=str(exc) if config.LOG_LEVEL == "DEBUG" else None,
        ).model_dump(exclude_none=True),
    )


# ---------------------------------------------------------------------------
# Helper: detect critical findings
# ---------------------------------------------------------------------------


def _extract_critical_findings(text: str) -> list[str]:
    """Heuristic scan for urgent / critical phrases in either language.

    This is intentionally a fast, rule-based pre-filter. The LLM validator
    performs a deeper semantic check in 'full' mode.
    """
    critical_patterns: list[str] = [
        # English
        "pulmonary embolism", "aortic dissection", "tension pneumothorax",
        "intracranial hemorrhage", "subarachnoid hemorrhage", "acute stroke",
        "cord compression", "bowel perforation", "ruptured aneurysm",
        "cardiac tamponade", "massive hemothorax",
        # Korean
        "폐색전증", "대동맥박리", "긴장성기흉", "두개내출혈", "지주막하출혈",
        "급성뇌졸중", "척수압박", "장천공", "파열된동맥류", "심낭압전",
    ]
    lower = text.lower()
    found: list[str] = []
    for pattern in critical_patterns:
        if pattern.lower() in lower:
            found.append(pattern)
    return found


# ---------------------------------------------------------------------------
# Helper: map risk keywords to RiskLevel
# ---------------------------------------------------------------------------


def _classify_risk(text: str) -> RiskLevel:
    """Map risk keywords to RiskLevel, skipping negated mentions.

    Negation window: up to 6 tokens (words) immediately before the keyword
    are inspected for English negation phrases.  Korean negation is checked
    by scanning a short character window after the keyword.

    Examples that must produce LOW risk:
        "No acute cardiopulmonary findings. The lungs are clear."
        "without hemorrhage"
        "absence of malignancy"
        "mass is not seen"
        "negative for malignant cells"
    """
    import re as _re

    # English negation words / phrases that precede a keyword
    _NEGATION_PREFIX = _re.compile(
        r"\b(?:no|not|without|absent|absence\s+of|no\s+evidence\s+of|"
        r"negative\s+for|free\s+of|clear\s+of|not\s+seen|not\s+identified|"
        r"not\s+detected|not\s+visualized|not\s+observed|unremarkable)\b",
        _re.IGNORECASE,
    )
    # Korean negation that appears within ~10 chars AFTER the keyword
    _KOREAN_NEGATION_SUFFIX = _re.compile(
        r"(?:없|않|아님|음성|관찰되지|확인되지|보이지|발견되지)"
    )

    def _is_negated(text_lower: str, kw_lower: str) -> bool:
        """Return True if every occurrence of kw in text is negated."""
        pattern = _re.compile(r"\b" + _re.escape(kw_lower) + r"\b") if kw_lower.isascii() else None
        if pattern:
            matches = list(pattern.finditer(text_lower))
        else:
            # Korean keyword — find all substring positions
            start = 0
            positions = []
            while True:
                idx = text_lower.find(kw_lower, start)
                if idx == -1:
                    break
                positions.append(idx)
                start = idx + 1
            if not positions:
                return False  # not found at all — treat as not present
            matches = positions  # list of int positions

        if not matches:
            return False  # keyword not present — treat as not negated (not found)

        all_negated = True
        for m in matches:
            start_pos = m.start() if hasattr(m, "start") else m
            # Check English negation: scan up to 60 chars before keyword
            prefix = text_lower[max(0, start_pos - 60): start_pos]
            prefix_words = prefix.split()
            # Look within last 6 words for a negation token
            window = " ".join(prefix_words[-6:])
            if _NEGATION_PREFIX.search(window):
                continue  # this occurrence is negated
            # Check English post-keyword negation: "X is not seen" etc.
            end_pos = m.end() if hasattr(m, "end") else m + len(kw_lower)
            suffix = text_lower[end_pos: end_pos + 40]
            if _re.search(r"\b(?:not\s+(?:seen|identified|detected|visualized|observed|present))\b", suffix):
                continue  # negated
            # Check Korean negation suffix
            if _KOREAN_NEGATION_SUFFIX.search(suffix[:10]):
                continue  # negated
            all_negated = False
            break

        return all_negated

    lower = text.lower()

    for kw in config.RISK_KEYWORDS_HIGH:
        kw_lower = kw.lower()
        # Check if keyword is present at all (fast path)
        if kw_lower not in lower:
            continue
        if not _is_negated(lower, kw_lower):
            return RiskLevel.high

    for kw in config.RISK_KEYWORDS_MEDIUM:
        kw_lower = kw.lower()
        if kw_lower not in lower:
            continue
        if not _is_negated(lower, kw_lower):
            return RiskLevel.medium

    return RiskLevel.low


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.post(
    "/api/translate",
    response_model=TranslateResponse,
    summary="Translate a radiology report to Korean",
    tags=["Translation"],
)
async def translate(body: TranslateRequest) -> TranslateResponse:
    """
    Translate a medical radiology report and (optionally) generate a
    patient-friendly explanation and quality validation.

    **Modes**:
    - ``translation_only`` – returns bare translation, fastest.
    - ``with_explanation`` – adds patient-friendly explanation in Korean.
    - ``full`` – also runs automated translation validation.
    """
    await _ensure_models_loaded()

    t_start = time.perf_counter()

    # ------------------------------------------------------------------ #
    # 1. Translation                                                       #
    # ------------------------------------------------------------------ #
    try:
        translation_result = await asyncio.to_thread(
            _translator.translate,
            text=body.text,
            source_lang=body.source_lang.value,
        )
        translated: str = translation_result.translated_text
        bilingual_pairs = translation_result.metadata.get("bilingual")
        bilingual: Optional[list[BilingualLine]] = (
            [BilingualLine(en=p["en"], ko=p["ko"]) for p in bilingual_pairs]
            if bilingual_pairs else None
        )
    except Exception as exc:
        logger.exception("Translation failed.")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Translation model error: {exc}",
        ) from exc

    # ------------------------------------------------------------------ #
    # 2. Critical findings (always, fast rule-based pass)                  #
    # ------------------------------------------------------------------ #
    critical_findings = _extract_critical_findings(body.text + " " + translated)

    # ------------------------------------------------------------------ #
    # 3 + 4. Patient explanation and validation run concurrently          #
    # Explanation: with_explanation | full                                #
    # Validation:  full only                                              #
    # The two tasks are independent — launch both and await together.     #
    # ------------------------------------------------------------------ #

    need_explanation = body.mode.value in ("with_explanation", "full")
    need_validation = body.mode.value == "full"

    async def _run_explanation() -> Optional[PatientExplanation]:
        if not need_explanation:
            return None
        try:
            exp = await asyncio.to_thread(
                _translator.generate_patient_explanation,
                translated_text=translated,
                original_text=body.text,
            )
            return PatientExplanation(
                summary=exp.summary,
                key_findings=exp.key_findings,
                patient_text=exp.patient_explanation,
                recommendations=exp.recommendations,
            )
        except Exception as exc:
            logger.warning("Patient explanation generation failed: %s", exc)
            return PatientExplanation(
                summary="설명을 생성하는 중 오류가 발생했습니다.",
                key_findings=[],
                patient_text="현재 환자용 설명을 생성할 수 없습니다. 담당 의사에게 문의하세요.",
            )

    async def _run_validation() -> Optional[ValidationResult]:
        if not need_validation:
            return None
        try:
            val = await asyncio.to_thread(
                _validator.validate_translation,
                original=body.text,
                translated=translated,
            )
            risk = RiskLevel(val.risk_level)
            issue_count = len(val.issues)
            base = {"low": 0.95, "medium": 0.65, "high": 0.35}.get(risk.value, 0.5)
            confidence = round(max(0.1, base - issue_count * 0.05), 2)
            return ValidationResult(
                is_valid=val.is_valid,
                issues=[i.description if hasattr(i, "description") else str(i) for i in val.issues],
                risk_level=risk,
                confidence_score=confidence,
            )
        except Exception as exc:
            logger.warning("Validation failed: %s", exc)
            risk = _classify_risk(body.text)
            return ValidationResult(
                is_valid=True,
                issues=["자동 검증을 완료할 수 없습니다. 휴리스틱 위험도만 제공됩니다."],
                risk_level=risk,
            )

    patient_explanation, validation = await asyncio.gather(
        _run_explanation(),
        _run_validation(),
    )

    elapsed_ms = int((time.perf_counter() - t_start) * 1000)

    return TranslateResponse(
        original=body.text,
        translated=translated,
        patient_explanation=patient_explanation,
        validation=validation,
        bilingual=bilingual,
        critical_findings=critical_findings,
        processing_time_ms=elapsed_ms,
    )


@app.post(
    "/api/validate",
    response_model=ValidateResponse,
    summary="Validate a translation against its original",
    tags=["Validation"],
)
async def validate_translation(body: ValidateRequest) -> ValidateResponse:
    """
    Run quality and safety checks on an existing translation without
    re-running the full translation pipeline.
    """
    await _ensure_models_loaded()

    try:
        val = await asyncio.to_thread(
            _validator.validate_translation,
            original=body.original,
            translated=body.translated,
        )
        result = ValidationResult(
            is_valid=val.is_valid,
            issues=[i.description if hasattr(i, 'description') else str(i) for i in val.issues],
            risk_level=RiskLevel(val.risk_level),
        )
    except Exception as exc:
        logger.exception("Standalone validation failed.")
        # Graceful degradation: return heuristic result
        risk = _classify_risk(body.original + " " + body.translated)
        result = ValidationResult(
            is_valid=True,
            issues=[f"자동 검증 오류: {exc}"],
            risk_level=risk,
        )

    return ValidateResponse(validation=result)


@app.get(
    "/api/health",
    response_model=HealthResponse,
    summary="Service health check",
    tags=["Operations"],
)
async def health_check() -> HealthResponse:
    """
    Probe the liveness of upstream services (Ollama) and local models.
    Returns HTTP 200 even when a dependency is degraded so that load balancers
    keep the instance in rotation; the ``status`` field communicates health.
    """
    model_statuses: dict[str, str] = {}
    overall_ok = True

    # ---- Ollama connectivity ------------------------------------------ #
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{config.OLLAMA_BASE_URL}/api/tags")
        if resp.status_code == 200:
            tags = resp.json()
            available_models = [m["name"] for m in tags.get("models", [])]
            primary_ok = any(
                config.OLLAMA_MODEL in m for m in available_models
            )
            fallback_ok = any(
                config.OLLAMA_FALLBACK_MODEL in m for m in available_models
            )
            if primary_ok:
                model_statuses["ollama"] = "connected"
            elif fallback_ok:
                model_statuses["ollama"] = f"connected (fallback: {config.OLLAMA_FALLBACK_MODEL})"
                overall_ok = False  # Degraded – primary model absent
            else:
                model_statuses["ollama"] = "connected (no required model found)"
                overall_ok = False
        else:
            model_statuses["ollama"] = f"error (HTTP {resp.status_code})"
            overall_ok = False
    except Exception as exc:
        model_statuses["ollama"] = f"unavailable ({exc})"
        overall_ok = False

    # ---- Local translation model --------------------------------------- #
    if _models_ready and _translator is not None:
        model_statuses["translator"] = "loaded"
    else:
        model_statuses["translator"] = "not_loaded_yet"

    # ---- RAG / embedding model ----------------------------------------- #
    if _models_ready and _rag is not None:
        model_statuses["rag"] = "loaded"
    else:
        model_statuses["rag"] = "not_loaded_yet"

    # ---- Validator ----------------------------------------------------- #
    if _models_ready and _validator is not None:
        model_statuses["validator"] = "loaded"
    else:
        model_statuses["validator"] = "not_loaded_yet"

    return HealthResponse(
        status="ok" if overall_ok else "degraded",
        models=model_statuses,
    )


@app.get(
    "/api/terms/search",
    response_model=TermSearchResponse,
    summary="Search the medical terminology dictionary",
    tags=["Terminology"],
)
async def search_terms(
    q: str = Query(
        ...,
        min_length=1,
        max_length=200,
        description="Search query (English or Korean medical term).",
        examples=["nodule"],
    ),
    limit: int = Query(
        default=config.RAG_TOP_K,
        ge=1,
        le=20,
        description="Maximum number of results to return.",
    ),
) -> TermSearchResponse:
    """
    Semantic search over the medical terminology vector store.
    Returns terms ordered by relevance to the query.
    """
    await _ensure_models_loaded()

    try:
        raw_results: list[dict] = await asyncio.to_thread(
            _rag.get_relevant_terms,
            query=q,
            n_results=limit,
        )
    except Exception as exc:
        logger.exception("Term search failed for query '%s'.", q)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Term search error: {exc}",
        ) from exc

    terms: list[MedicalTerm] = []
    for item in raw_results:
        try:
            terms.append(
                MedicalTerm(
                    term=item.get("term", ""),
                    korean=item.get("korean", ""),
                    definition=item.get("definition", ""),
                    category=item.get("category"),
                    synonyms=item.get("synonyms", []),
                    score=item.get("score"),
                )
            )
        except Exception:
            logger.warning("Skipping malformed term entry: %s", item)

    return TermSearchResponse(query=q, results=terms, total=len(terms))


# ---------------------------------------------------------------------------
# Dev / debug entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=config.LOG_LEVEL.lower(),
    )
