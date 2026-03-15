// ─── TypeScript Interfaces ─────────────────────────────────────────────────

export type LanguageCode = "auto" | "en" | "ko";
export type TranslationMode = "translation_only" | "with_explanation" | "full";
export type RiskLevel = "low" | "medium" | "high" | "critical";

export interface TranslateRequest {
  text: string;
  source_language?: LanguageCode;
  target_language?: LanguageCode;
  mode?: TranslationMode;
  include_explanation?: boolean;
  include_validation?: boolean;
}

export interface KeyFinding {
  term: string;
  explanation: string;
  severity?: "normal" | "mild" | "moderate" | "severe";
}

export interface PatientExplanation {
  summary: string;
  key_findings: KeyFinding[];
  patient_friendly_text: string;
  recommendations?: string[];
  follow_up?: string;
}

export interface ValidationIssue {
  type: "error" | "warning" | "info";
  message: string;
  term?: string;
  suggestion?: string;
}

export interface ValidationResult {
  is_valid: boolean;
  risk_level: RiskLevel;
  issues: ValidationIssue[];
  critical_terms_found: string[];
  confidence_score?: number;
  reviewed_at?: string;
}

export interface TranslateResponse {
  original_text: string;
  translated_text: string;
  source_language?: string;
  target_language?: string;
  translation_mode?: TranslationMode;
  patient_explanation?: PatientExplanation | null;
  validation?: ValidationResult | null;
  critical_findings: string[];
  processing_time_ms: number;
  model_used?: string;
  timestamp?: string;
}

export interface MedicalTerm {
  term: string;
  korean: string;
  definition: string;
  category?: string;
}

export interface TermSearchResponse {
  query: string;
  results: MedicalTerm[];
  total: number;
}

export interface ValidateRequest {
  original_text: string;
  translated_text: string;
}

// ─── API Base URL ──────────────────────────────────────────────────────────

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

// ─── Error Handling ────────────────────────────────────────────────────────

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
    public detail?: unknown
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail: unknown;
    try {
      detail = await res.json();
    } catch {
      detail = await res.text();
    }
    const message =
      typeof detail === "object" &&
      detail !== null &&
      "detail" in (detail as Record<string, unknown>)
        ? String((detail as Record<string, unknown>).detail)
        : `HTTP ${res.status}: ${res.statusText}`;
    throw new ApiError(res.status, message, detail);
  }
  return res.json() as Promise<T>;
}

// ─── API Functions ─────────────────────────────────────────────────────────

// Raw shape returned by the backend (field names differ from our internal interface)
interface RawTranslateResponse {
  original?: string;
  translated?: string;
  original_text?: string;
  translated_text?: string;
  source_language?: string;
  target_language?: string;
  translation_mode?: TranslationMode;
  patient_explanation?: PatientExplanation | null;
  validation?: ValidationResult | null;
  critical_findings?: string[];
  processing_time_ms?: number;
  model_used?: string;
  timestamp?: string;
}

/**
 * Translate a medical radiology report.
 */
export async function translateReport(
  request: TranslateRequest
): Promise<TranslateResponse> {
  const res = await fetch(`${API_BASE_URL}/api/translate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
  const raw = await handleResponse<RawTranslateResponse>(res);

  // Normalise: the backend may return `original`/`translated` (short form)
  // or `original_text`/`translated_text` (long form). Prefer long form if
  // present, fall back to short form so both API versions work.
  return {
    ...raw,
    original_text: raw.original_text ?? raw.original ?? "",
    translated_text: raw.translated_text ?? raw.translated ?? "",
    critical_findings: raw.critical_findings ?? [],
    processing_time_ms: raw.processing_time_ms ?? 0,
  } as TranslateResponse;
}

/**
 * Validate a translation against the original report.
 */
export async function validateTranslation(
  original: string,
  translated: string
): Promise<ValidationResult> {
  const res = await fetch(`${API_BASE_URL}/api/validate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      original_text: original,
      translated_text: translated,
    } satisfies ValidateRequest),
  });
  return handleResponse<ValidationResult>(res);
}

/**
 * Search for medical terminology definitions.
 */
export async function searchTerms(query: string): Promise<TermSearchResponse> {
  const params = new URLSearchParams({ q: query });
  const res = await fetch(`${API_BASE_URL}/api/terms/search?${params}`, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  });
  return handleResponse<TermSearchResponse>(res);
}
