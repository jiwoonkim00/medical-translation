"""
RAG (Retrieval-Augmented Generation) vector store for medical terminology.

Uses:
- ChromaDB as the persistent vector database
- sentence-transformers with BAAI/bge-m3 for multilingual embeddings
  (bge-m3 supports Korean, English, and 100+ languages with strong cross-lingual retrieval)
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from rag.medical_terms import RADIOLOGY_TERMS, TermEntry

logger = logging.getLogger(__name__)

# ChromaDB collection name
_COLLECTION_NAME = "medical_radiology_terms"

# Default path for persistent ChromaDB storage
_DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "chromadb"

# Embedding model — BAAI/bge-m3 is a state-of-the-art multilingual dense retrieval model
_EMBEDDING_MODEL_NAME = "BAAI/bge-m3"


class _BGEEmbeddingFunction(chromadb.EmbeddingFunction):
    """
    Custom ChromaDB embedding function backed by sentence-transformers BAAI/bge-m3.
    bge-m3 natively supports Korean + English, which is ideal for cross-lingual RAG.
    """

    def __init__(self, model_name: str = _EMBEDDING_MODEL_NAME) -> None:
        logger.info("Loading embedding model: %s", model_name)
        self._model = SentenceTransformer(model_name)
        logger.info("Embedding model loaded successfully.")

    def __call__(self, input: list[str]) -> list[list[float]]:  # noqa: A002
        embeddings = self._model.encode(
            input,
            normalize_embeddings=True,   # cosine similarity
            show_progress_bar=False,
        )
        return embeddings.tolist()


class MedicalRAG:
    """
    Retrieval-Augmented Generation helper for medical radiology terminology.

    Workflow:
    1. Call ``initialize()`` once at startup to populate the vector store.
    2. Call ``get_relevant_terms()`` at inference time to retrieve context.
    3. Call ``augment_prompt_with_context()`` to inject that context into prompts.
    """

    def __init__(self, db_path: str | os.PathLike | None = None) -> None:
        self._db_path = Path(db_path) if db_path else _DEFAULT_DB_PATH
        self._db_path.mkdir(parents=True, exist_ok=True)

        self._embedding_fn: _BGEEmbeddingFunction | None = None
        self._client: chromadb.ClientAPI | None = None
        self._collection: chromadb.Collection | None = None
        self._ready = False

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _ensure_ready(self) -> None:
        if not self._ready:
            raise RuntimeError(
                "MedicalRAG is not initialised. Call initialize() first."
            )

    def _build_document(self, term: str, entry: TermEntry) -> str:
        """
        Compose a plain-text document that combines all facets of a term
        so the embedding captures the full semantic content.
        """
        return (
            f"Medical term (English): {term}\n"
            f"Korean translation: {entry['korean']}\n"
            f"Patient-friendly explanation: {entry['patient_friendly']}\n"
            f"Category: {entry['category']}"
        )

    def _load_terms_from_file(self, terms_file_path: str | os.PathLike) -> dict[str, TermEntry]:
        """
        Load additional terms from a JSON file.
        Expected format:
        {
            "term": {
                "korean": "...",
                "patient_friendly": "...",
                "category": "..."
            },
            ...
        }
        """
        path = Path(terms_file_path)
        if not path.exists():
            logger.warning("Terms file not found: %s — using built-in terms only.", path)
            return {}
        try:
            with path.open(encoding="utf-8") as fh:
                data = json.load(fh)
            logger.info("Loaded %d extra terms from %s", len(data), path)
            return data
        except (json.JSONDecodeError, OSError) as exc:
            logger.error("Failed to load terms file %s: %s", path, exc)
            return {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def initialize(self, terms_file_path: str | os.PathLike | None = None) -> None:
        """
        Initialise the ChromaDB vector store and populate it with medical terms.

        Parameters
        ----------
        terms_file_path:
            Optional path to a JSON file with extra medical terms to add on top
            of the built-in ``RADIOLOGY_TERMS`` dictionary.
        """
        logger.info("Initialising MedicalRAG (db_path=%s) …", self._db_path)

        # Lazy-load the embedding model
        self._embedding_fn = _BGEEmbeddingFunction()

        # Persistent ChromaDB client
        self._client = chromadb.PersistentClient(
            path=str(self._db_path),
            settings=Settings(anonymized_telemetry=False),
        )

        # Get or create the collection
        self._collection = self._client.get_or_create_collection(
            name=_COLLECTION_NAME,
            embedding_function=self._embedding_fn,
            metadata={"hnsw:space": "cosine"},
        )

        # Merge built-in terms with any extra file-based terms
        all_terms: dict[str, TermEntry] = dict(RADIOLOGY_TERMS)
        if terms_file_path:
            extra = self._load_terms_from_file(terms_file_path)
            all_terms.update(extra)

        # Upsert all terms into ChromaDB (idempotent)
        documents: list[str] = []
        metadatas: list[dict[str, Any]] = []
        ids: list[str] = []

        for term, entry in all_terms.items():
            doc_id = term.lower().replace(" ", "_")
            documents.append(self._build_document(term, entry))
            metadatas.append(
                {
                    "term_en": term,
                    "term_ko": entry["korean"],
                    "patient_friendly": entry["patient_friendly"],
                    "category": entry["category"],
                }
            )
            ids.append(doc_id)

        if documents:
            self._collection.upsert(
                documents=documents,
                metadatas=metadatas,
                ids=ids,
            )
            logger.info(
                "Upserted %d medical terms into ChromaDB collection '%s'.",
                len(documents),
                _COLLECTION_NAME,
            )

        self._ready = True
        logger.info("MedicalRAG initialised successfully.")

    def get_relevant_terms(
        self,
        query: str,
        n_results: int = 5,
    ) -> list[dict[str, Any]]:
        """
        Retrieve the most relevant medical terms for a given query text.

        Parameters
        ----------
        query:
            Free-form text (English or Korean) describing the medical context.
        n_results:
            Number of results to return.

        Returns
        -------
        List of dicts, each containing:
            - term_en: English term
            - term_ko: Korean term
            - patient_friendly: patient-friendly explanation
            - category: term category
            - distance: cosine distance (lower = more similar)
        """
        self._ensure_ready()
        assert self._collection is not None  # narrowing for type checkers

        try:
            results = self._collection.query(
                query_texts=[query],
                n_results=min(n_results, self._collection.count()),
                include=["metadatas", "distances"],
            )
        except Exception as exc:
            logger.error("ChromaDB query failed: %s", exc)
            return []

        hits: list[dict[str, Any]] = []
        metadatas_list = results.get("metadatas") or [[]]
        distances_list = results.get("distances") or [[]]

        for meta, dist in zip(metadatas_list[0], distances_list[0]):
            hits.append(
                {
                    "term_en": meta.get("term_en", ""),
                    "term_ko": meta.get("term_ko", ""),
                    "patient_friendly": meta.get("patient_friendly", ""),
                    "category": meta.get("category", ""),
                    "distance": round(float(dist), 4),
                }
            )

        logger.debug("RAG query '%s' → %d hits", query[:60], len(hits))
        return hits

    def augment_prompt_with_context(
        self,
        base_prompt: str,
        query: str,
        n_results: int = 5,
    ) -> str:
        """
        Inject relevant medical term context into a prompt template.

        The method retrieves ``n_results`` terms relevant to ``query`` and
        appends a structured context block to ``base_prompt``.

        Parameters
        ----------
        base_prompt:
            The original prompt string (may contain ``{rag_context}`` placeholder).
        query:
            Text used to retrieve relevant terms from the vector store.
        n_results:
            Number of terms to retrieve.

        Returns
        -------
        The prompt with ``{rag_context}`` replaced by the retrieved context,
        or the context appended at the end if the placeholder is absent.
        """
        self._ensure_ready()

        relevant_terms = self.get_relevant_terms(query, n_results=n_results)

        if not relevant_terms:
            context_block = "관련 의학 용어 정보를 찾을 수 없습니다."
        else:
            lines = ["[관련 의학 용어 참고]"]
            for hit in relevant_terms:
                lines.append(
                    f"- {hit['term_en']} → {hit['term_ko']}: {hit['patient_friendly']}"
                )
            context_block = "\n".join(lines)

        if "{rag_context}" in base_prompt:
            return base_prompt.replace("{rag_context}", context_block)

        return base_prompt + "\n\n" + context_block

    @property
    def is_ready(self) -> bool:
        """Return True if the vector store has been initialised."""
        return self._ready

    def count_terms(self) -> int:
        """Return the number of terms currently stored in the collection."""
        self._ensure_ready()
        assert self._collection is not None
        return self._collection.count()
