"use client";

import { useState, useCallback } from "react";
import type { TranslateResponse, RiskLevel } from "@/lib/api";

// ─── Sub-components ────────────────────────────────────────────────────────

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // fallback for older browsers
      const el = document.createElement("textarea");
      el.value = text;
      document.body.appendChild(el);
      el.select();
      document.execCommand("copy");
      document.body.removeChild(el);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  }, [text]);

  return (
    <button
      onClick={handleCopy}
      aria-label={copied ? "복사됨" : "클립보드에 복사"}
      className={`inline-flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-full transition-all ${
        copied
          ? "bg-green-100 text-green-700"
          : "bg-slate-100 text-slate-600 hover:bg-blue-100 hover:text-blue-700"
      }`}
    >
      {copied ? (
        <>
          <svg
            className="w-3.5 h-3.5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2.5}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M5 13l4 4L19 7"
            />
          </svg>
          복사됨
        </>
      ) : (
        <>
          <svg
            className="w-3.5 h-3.5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
            />
          </svg>
          복사
        </>
      )}
    </button>
  );
}

function RiskBadge({ level }: { level: RiskLevel }) {
  const config = {
    low: {
      label: "낮음",
      className: "bg-green-100 text-green-700 border-green-200",
      dot: "bg-green-500",
    },
    medium: {
      label: "중간",
      className: "bg-amber-100 text-amber-700 border-amber-200",
      dot: "bg-amber-500",
    },
    high: {
      label: "높음",
      className: "bg-orange-100 text-orange-700 border-orange-200",
      dot: "bg-orange-500",
    },
    critical: {
      label: "위험",
      className: "bg-red-100 text-red-700 border-red-200",
      dot: "bg-red-500",
    },
  }[level];

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-semibold border ${config.className}`}
    >
      <span className={`w-2 h-2 rounded-full ${config.dot}`} />
      위험도: {config.label}
    </span>
  );
}

// ─── Loading Skeleton ──────────────────────────────────────────────────────

function Skeleton({ className }: { className?: string }) {
  return (
    <div
      className={`animate-pulse bg-slate-200 rounded ${className ?? ""}`}
    />
  );
}

function LoadingSkeleton() {
  return (
    <div className="flex flex-col gap-4 p-1">
      <div className="flex gap-3 mb-2">
        <Skeleton className="h-9 w-24 rounded-full" />
        <Skeleton className="h-9 w-24 rounded-full" />
        <Skeleton className="h-9 w-24 rounded-full" />
      </div>
      <Skeleton className="h-4 w-1/3" />
      <Skeleton className="h-4 w-full" />
      <Skeleton className="h-4 w-5/6" />
      <Skeleton className="h-4 w-4/5" />
      <Skeleton className="h-4 w-full" />
      <Skeleton className="h-4 w-3/4" />
      <div className="mt-4">
        <Skeleton className="h-4 w-1/4 mb-3" />
        <div className="flex flex-wrap gap-2">
          <Skeleton className="h-7 w-20 rounded-full" />
          <Skeleton className="h-7 w-24 rounded-full" />
          <Skeleton className="h-7 w-16 rounded-full" />
        </div>
      </div>
    </div>
  );
}

// ─── Empty state ───────────────────────────────────────────────────────────

function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center h-full py-20 text-center">
      <div className="w-20 h-20 mb-6 rounded-2xl bg-slate-100 flex items-center justify-center">
        <svg
          className="w-10 h-10 text-slate-300"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={1.5}
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
          />
        </svg>
      </div>
      <h3 className="text-base font-semibold text-slate-500 mb-2">
        번역 결과가 여기에 표시됩니다
      </h3>
      <p className="text-sm text-slate-400 max-w-xs leading-relaxed">
        왼쪽 패널에 판독문을 입력하고 번역하기 버튼을 누르세요
      </p>
    </div>
  );
}

// ─── Tab content components ────────────────────────────────────────────────

function TranslationTab({ result }: { result: TranslateResponse }) {
  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-xs text-slate-400">
          <span className="bg-slate-100 px-2 py-1 rounded font-medium text-slate-600">
            {result.source_language?.toUpperCase() ?? "EN"}
          </span>
          <svg
            className="w-4 h-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M13 7l5 5m0 0l-5 5m5-5H6"
            />
          </svg>
          <span className="bg-blue-100 px-2 py-1 rounded font-medium text-blue-700">
            KO
          </span>
        </div>
        <CopyButton text={result.translated_text} />
      </div>

      <div className="bg-slate-50 rounded-xl p-5 border border-slate-200">
        <p className="text-sm leading-7 text-slate-800 whitespace-pre-wrap font-sans">
          {result.translated_text}
        </p>
      </div>

      {result.processing_time_ms !== undefined && (
        <div className="flex items-center gap-2 text-xs text-slate-400">
          <svg
            className="w-3.5 h-3.5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          처리 시간: {(result.processing_time_ms / 1000).toFixed(2)}초
          {result.model_used && (
            <span className="ml-2 text-slate-300">|</span>
          )}
          {result.model_used && (
            <span className="text-slate-400">{result.model_used}</span>
          )}
        </div>
      )}
    </div>
  );
}

function ExplanationTab({ result }: { result: TranslateResponse }) {
  const exp = result.patient_explanation;

  if (!exp) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <div className="w-14 h-14 rounded-full bg-amber-50 flex items-center justify-center mb-4">
          <svg
            className="w-7 h-7 text-amber-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={1.5}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </div>
        <p className="text-sm text-slate-500">
          환자 설명을 포함하려면{" "}
          <span className="font-semibold">&lsquo;번역 + 설명&rsquo;</span> 또는{" "}
          <span className="font-semibold">&lsquo;전체 분석&rsquo;</span> 모드를 선택하세요
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-5">
      {/* Summary */}
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
        <h4 className="text-xs font-bold text-blue-600 uppercase tracking-wider mb-2">
          요약
        </h4>
        <p className="text-sm leading-relaxed text-blue-900">{exp.summary}</p>
      </div>

      {/* Key Findings as list */}
      {exp.key_findings && exp.key_findings.length > 0 && (
        <div>
          <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">
            주요 소견 ({exp.key_findings.length}개)
          </h4>
          <ul className="flex flex-col gap-2">
            {exp.key_findings.map((finding, idx) => (
              <li
                key={idx}
                className="flex items-start gap-3 bg-white border border-slate-200 rounded-xl p-3 shadow-sm"
              >
                <span className="flex-shrink-0 w-5 h-5 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center text-xs font-bold mt-0.5">
                  {idx + 1}
                </span>
                <p className="text-sm text-slate-700 leading-relaxed">{finding}</p>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Patient-friendly text */}
      <div>
        <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">
          환자 안내문
        </h4>
        <div className="bg-slate-50 rounded-xl p-4 border border-slate-200">
          <p className="text-sm leading-7 text-slate-700 whitespace-pre-wrap">
            {exp.patient_text}
          </p>
        </div>
      </div>

      {/* Recommendations */}
      {exp.recommendations && exp.recommendations.length > 0 && (
        <div>
          <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">
            권고 사항
          </h4>
          <ul className="space-y-2">
            {exp.recommendations.map((rec, idx) => (
              <li
                key={idx}
                className="flex items-start gap-2 text-sm text-slate-700"
              >
                <span className="flex-shrink-0 w-5 h-5 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center text-xs font-bold mt-0.5">
                  {idx + 1}
                </span>
                {rec}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Follow-up */}
      {exp.follow_up && (
        <div className="flex items-start gap-3 bg-amber-50 border border-amber-200 rounded-xl p-4">
          <svg
            className="w-5 h-5 text-amber-500 flex-shrink-0 mt-0.5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
            />
          </svg>
          <div>
            <p className="text-xs font-bold text-amber-700 mb-1">추적 관찰</p>
            <p className="text-sm text-amber-800">{exp.follow_up}</p>
          </div>
        </div>
      )}
    </div>
  );
}

function ValidationTab({ result }: { result: TranslateResponse }) {
  const val = result.validation;

  if (!val) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <div className="w-14 h-14 rounded-full bg-amber-50 flex items-center justify-center mb-4">
          <svg
            className="w-7 h-7 text-amber-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={1.5}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </div>
        <p className="text-sm text-slate-500">
          검증 결과를 포함하려면{" "}
          <span className="font-semibold">&lsquo;전체 분석&rsquo;</span> 모드를 선택하세요
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-5">
      {/* Status header */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div className="flex items-center gap-3">
          <div
            className={`w-9 h-9 rounded-full flex items-center justify-center ${
              val.is_valid ? "bg-green-100" : "bg-red-100"
            }`}
          >
            <svg
              className={`w-5 h-5 ${
                val.is_valid ? "text-green-600" : "text-red-600"
              }`}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2.5}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d={
                  val.is_valid
                    ? "M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                    : "M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
                }
              />
            </svg>
          </div>
          <div>
            <p className="text-sm font-bold text-slate-800">
              {val.is_valid ? "번역 검증 통과" : "번역 검토 필요"}
            </p>
            <p className="text-xs text-slate-400">
              {val.issues.length}개의 항목 발견
            </p>
          </div>
        </div>
        <RiskBadge level={val.risk_level} />
      </div>

      {/* Confidence score */}
      {val.confidence_score !== undefined && (
        <div>
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-xs font-semibold text-slate-500">
              신뢰도 점수
            </span>
            <span className="text-sm font-bold text-slate-700">
              {Math.round(val.confidence_score * 100)}%
            </span>
          </div>
          <div className="w-full bg-slate-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all ${
                val.confidence_score >= 0.8
                  ? "bg-green-500"
                  : val.confidence_score >= 0.6
                  ? "bg-amber-500"
                  : "bg-red-500"
              }`}
              style={{ width: `${val.confidence_score * 100}%` }}
            />
          </div>
        </div>
      )}

      {/* Issues list */}
      {val.issues && val.issues.length > 0 ? (
        <div>
          <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">
            검증 항목 ({val.issues.length})
          </h4>
          <ul className="flex flex-col gap-2">
            {val.issues.map((issue, idx) => (
              <li
                key={idx}
                className="flex items-start gap-3 rounded-xl border p-3 bg-amber-50 border-amber-200 text-amber-800"
              >
                <svg
                  className="w-4 h-4 flex-shrink-0 mt-0.5 text-amber-600"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={2}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                  />
                </svg>
                <p className="text-xs leading-relaxed">{issue}</p>
              </li>
            ))}
          </ul>
        </div>
      ) : (
        <div className="flex items-center gap-3 bg-green-50 border border-green-200 rounded-xl p-4">
          <svg
            className="w-5 h-5 text-green-500 flex-shrink-0"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <p className="text-sm text-green-700 font-medium">
            검증 항목이 발견되지 않았습니다. 번역 품질이 우수합니다.
          </p>
        </div>
      )}
    </div>
  );
}

// ─── Main ResultPanel ──────────────────────────────────────────────────────

type TabKey = "translation" | "explanation" | "validation";

interface ResultPanelProps {
  result: TranslateResponse | null;
  isLoading: boolean;
}

const TABS: { key: TabKey; label: string; icon: string }[] = [
  {
    key: "translation",
    label: "번역문",
    icon: "M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129",
  },
  {
    key: "explanation",
    label: "환자 설명",
    icon: "M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z",
  },
  {
    key: "validation",
    label: "검증 결과",
    icon: "M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z",
  },
];

export default function ResultPanel({ result, isLoading }: ResultPanelProps) {
  const [activeTab, setActiveTab] = useState<TabKey>("translation");

  return (
    <div className="flex flex-col h-full">
      {/* Tab navigation */}
      <div className="flex items-center gap-1 border-b border-slate-200 mb-5 pb-0">
        {TABS.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            disabled={isLoading}
            className={`flex items-center gap-2 px-4 py-2.5 text-sm font-medium rounded-t-lg transition-colors border-b-2 -mb-px ${
              activeTab === tab.key
                ? "text-blue-700 border-blue-600 bg-blue-50"
                : "text-slate-500 border-transparent hover:text-slate-700 hover:border-slate-300"
            } disabled:opacity-50 disabled:cursor-not-allowed`}
          >
            <svg
              className="w-4 h-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path strokeLinecap="round" strokeLinejoin="round" d={tab.icon} />
            </svg>
            {tab.label}
            {/* Validation indicator dot */}
            {tab.key === "validation" &&
              result?.validation &&
              !result.validation.is_valid && (
                <span className="w-2 h-2 rounded-full bg-red-500" />
              )}
            {tab.key === "translation" && result?.critical_findings && result.critical_findings.length > 0 && (
              <span className="inline-flex items-center justify-center w-4 h-4 rounded-full bg-red-500 text-white text-xs font-bold">
                !
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Tab content */}
      <div className="flex-1 overflow-y-auto result-scroll pr-1">
        {isLoading ? (
          <LoadingSkeleton />
        ) : result ? (
          <>
            {activeTab === "translation" && (
              <TranslationTab result={result} />
            )}
            {activeTab === "explanation" && (
              <ExplanationTab result={result} />
            )}
            {activeTab === "validation" && (
              <ValidationTab result={result} />
            )}
          </>
        ) : (
          <EmptyState />
        )}
      </div>
    </div>
  );
}
