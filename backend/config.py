"""
Configuration settings for the Medical Radiology Report Translation System.
All environment-sensitive values can be overridden via environment variables.
"""

import os

# ---------------------------------------------------------------------------
# Ollama LLM settings
# ---------------------------------------------------------------------------
OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
OLLAMA_FALLBACK_MODEL: str = os.getenv("OLLAMA_FALLBACK_MODEL", "llama3.2:latest")

# Timeout in seconds for a single Ollama API call
OLLAMA_TIMEOUT: int = int(os.getenv("OLLAMA_TIMEOUT", "120"))

# ---------------------------------------------------------------------------
# HuggingFace model names
# ---------------------------------------------------------------------------
# Helsinki-NLP MT model used for fast rule-based translation baseline
TRANSLATION_MODEL: str = os.getenv(
    "TRANSLATION_MODEL", "Helsinki-NLP/opus-mt-en-ko"
)

# BGE-M3 multilingual embedding model for RAG retrieval
EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")

# ---------------------------------------------------------------------------
# Vector store (ChromaDB) settings
# ---------------------------------------------------------------------------
CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
CHROMA_COLLECTION_NAME: str = os.getenv(
    "CHROMA_COLLECTION_NAME", "medical_terms"
)

# ---------------------------------------------------------------------------
# Input / output constraints
# ---------------------------------------------------------------------------
MAX_TEXT_LENGTH: int = int(os.getenv("MAX_TEXT_LENGTH", "10000"))

# Maximum number of RAG results returned per query
RAG_TOP_K: int = int(os.getenv("RAG_TOP_K", "5"))

# ---------------------------------------------------------------------------
# CORS settings
# ---------------------------------------------------------------------------
# Comma-separated list of allowed origins
_raw_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
ALLOWED_ORIGINS: list[str] = [o.strip() for o in _raw_origins.split(",") if o.strip()]

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

# ---------------------------------------------------------------------------
# Risk classification thresholds (used by validator)
# ---------------------------------------------------------------------------
RISK_KEYWORDS_HIGH: list[str] = [
    "malignancy", "malignant", "cancer", "carcinoma", "tumor", "metastasis",
    "metastatic", "hemorrhage", "embolism", "occlusion", "rupture",
    "악성", "암", "종양", "전이", "출혈", "색전", "폐색", "파열",
]

RISK_KEYWORDS_MEDIUM: list[str] = [
    "nodule", "mass", "lesion", "opacity", "consolidation", "effusion",
    "adenopathy", "lymphadenopathy", "stenosis", "aneurysm",
    "결절", "종괴", "병변", "음영", "경화", "삼출", "선증", "림프절종대",
    "협착", "동맥류",
]
